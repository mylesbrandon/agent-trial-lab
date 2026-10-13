"""Build and evaluate Code Reliability Bench in a bounded Linux container.

The host launcher uses only the standard library; pytest lives in the image.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def positive_seconds(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Timeout must be finite and greater than zero.")
    return number


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution-set", type=Path, help="Directory of task_001.py through task_032.py; defaults to validated references.")
    parser.add_argument("--model", default="reference")
    parser.add_argument("--condition", default="docker")
    parser.add_argument("--results-root", type=Path, default=Path("work/docker-runs"), help="Parent for a fresh output directory per invocation.")
    parser.add_argument("--timeout-seconds", type=positive_seconds, default=10.0, help="Deadline for EACH candidate test suite.")
    parser.add_argument("--validation-timeout-seconds", type=positive_seconds, default=10.0, help="Deadline for EACH reference/starter/defect test suite.")
    parser.add_argument("--run-timeout-seconds", type=positive_seconds, default=600.0, help="Wall deadline for the complete container workflow, excluding build.")
    parser.add_argument("--build-timeout-seconds", type=positive_seconds, default=600.0)
    parser.add_argument("--require-all-pass", action="store_true", help="Fail the command if any candidate fails or is missing (automatic for default references).")
    parser.add_argument("--image", help="Use an existing image instead of building this checkout.")
    return parser.parse_args(argv)


def bind_mount(source: Path, target: str, *, readonly: bool = False) -> str:
    stream = io.StringIO()
    fields = ["type=bind", f"source={source}", f"target={target}"]
    if readonly:
        fields.append("readonly")
    csv.writer(stream, lineterminator="").writerow(fields)
    return stream.getvalue()


def runtime_user() -> str:
    if hasattr(os, "getuid") and os.getuid() != 0:
        return f"{os.getuid()}:{os.getgid()}"
    return "10001:10001"


def container_command(docker: str, image: str, name: str, output: Path,
                      args: argparse.Namespace) -> list[str]:
    command = [
        docker, "run", "--rm", "--name", name, "--init",
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--pids-limit", "128",
        "--memory", "1g", "--memory-swap", "1g", "--cpus", "2",
        "--user", runtime_user(),
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m,mode=1777",
        "--mount", bind_mount(output, "/output"),
    ]
    if args.solution_set is not None:
        command += ["--mount", bind_mount(args.solution_set.resolve(), "/candidates", readonly=True)]
    command += [image, "--root", "/app", "--results-root", "/output",
                "--model", args.model, "--condition", args.condition,
                "--timeout-seconds", str(args.timeout_seconds),
                "--validation-timeout-seconds", str(args.validation_timeout_seconds)]
    if args.solution_set is not None:
        command += ["--solution-set", "/candidates"]
    if args.require_all_pass:
        command.append("--require-all-pass")
    return command


def _capture(command: list[str], timeout: float = 30) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True,
                          timeout=timeout).stdout.strip()


def remove_container(docker: str, name: str) -> dict:
    try:
        result = subprocess.run([docker, "rm", "--force", name], capture_output=True,
                                text=True, timeout=30)
        removed = result.returncode == 0 or "No such container" in result.stderr
        return {"confirmed": removed, "diagnostic": "" if removed else result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"confirmed": False, "diagnostic": str(error)}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def launch(args: argparse.Namespace) -> int:
    docker = shutil.which("docker")
    if docker is None:
        print("Docker CLI was not found. Install/start a local Docker engine with Linux containers, then rerun this command.", file=sys.stderr)
        return 2
    if args.solution_set is not None and not args.solution_set.is_dir():
        print(f"Solution set is not a directory: {args.solution_set}", file=sys.stderr)
        return 2
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
    output = args.results_root.resolve() / run_id
    try:
        output.mkdir(parents=True, exist_ok=False)
        # Root users still run candidates as an unprivileged container identity.
        if hasattr(os, "getuid") and os.getuid() == 0:
            os.chown(output, 10001, 10001)
    except OSError as error:
        print(f"Cannot create the output directory: {error}", file=sys.stderr)
        return 2
    name = "crb-" + run_id.lower()
    manifest = {
        "project": "Code Reliability Bench", "run_id": run_id,
        "started_at_utc": _utc_now(), "status": "starting",
        "container_name": name, "output_directory": str(output),
        "solution_set": str(args.solution_set.resolve()) if args.solution_set else "bundled references",
        "model": args.model, "condition": args.condition,
        "require_all_pass": args.require_all_pass or args.solution_set is None,
        "limits": {"suite_timeout_seconds": args.timeout_seconds,
                   "validation_suite_timeout_seconds": args.validation_timeout_seconds,
                   "run_timeout_seconds": args.run_timeout_seconds,
                   "build_timeout_seconds": args.build_timeout_seconds,
                   "memory": "1g", "cpus": 2, "pids": 128, "tmpfs": "256m",
                   "network": "none", "read_only_root": True, "user": runtime_user()},
    }
    manifest_path = output / "docker-run.json"

    def save() -> None:
        # Replace atomically so an interruption never leaves half a JSON record.
        temporary = output / ".docker-run.json.tmp"
        temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temporary.replace(manifest_path)

    def interrupted(signum, frame) -> None:
        raise KeyboardInterrupt

    attempted_run = False
    exit_code = 2
    print(f"Run output: {output}", flush=True)
    try:
        save()
    except OSError as error:
        print(f"Cannot write the run manifest: {error}", file=sys.stderr)
        return 2
    previous_term_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        if _capture([docker, "info", "--format", "{{.OSType}}"], timeout=30) != "linux":
            raise ValueError("Docker must use a Linux engine for this benchmark.")
        if args.image:
            image_reference = args.image
        else:
            manifest["status"] = "building"
            save()
            iidfile = output / "image-id.txt"
            subprocess.run([docker, "build", "--iidfile", str(iidfile), str(ROOT)],
                           check=True, timeout=args.build_timeout_seconds)
            image_reference = iidfile.read_text(encoding="utf-8").strip()
        image_info = json.loads(_capture([docker, "image", "inspect", image_reference]))[0]
        if image_info["Os"] != "linux":
            raise ValueError("The benchmark image must target Linux.")
        manifest["image"] = {"id": image_info["Id"], "os": image_info["Os"],
                             "architecture": image_info["Architecture"],
                             "repo_digests": image_info.get("RepoDigests", [])}
        manifest["status"] = "running"
        manifest["container_started_at_utc"] = _utc_now()
        save()
        attempted_run = True
        result = subprocess.run(container_command(docker, image_info["Id"], name, output, args),
                                timeout=args.run_timeout_seconds)
        exit_code = result.returncode if result.returncode >= 0 else 1
        if exit_code == 0:
            workflow = json.loads((output / "workflow.json").read_text(encoding="utf-8"))
            if workflow.get("status") != "completed" or workflow.get("exit_code") != 0:
                raise ValueError("Container exited zero without a completed benchmark report.")
        manifest["status"] = "completed" if exit_code == 0 else "failed"
    except subprocess.TimeoutExpired as error:
        manifest["status"] = "timed_out" if attempted_run else "setup_timed_out"
        manifest["error"] = f"Deadline exceeded after {error.timeout} seconds."
        exit_code = 124
    except KeyboardInterrupt:
        manifest["status"] = "interrupted"
        exit_code = 130
    except (OSError, ValueError, KeyError, IndexError, subprocess.CalledProcessError) as error:
        manifest["status"] = "error"
        manifest["error"] = str(error)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            manifest["error"] += "\n" + error.stderr.strip()
        exit_code = 2
    finally:
        # Killing `docker run` alone does not stop its server-side container.
        # Ignore a second interrupt only while performing bounded cleanup.
        previous_int_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        try:
            if attempted_run:
                manifest["cleanup"] = remove_container(docker, name)
                if not manifest["cleanup"]["confirmed"]:
                    print(f"Container cleanup could not be confirmed: docker rm --force {name}", file=sys.stderr)
                    if exit_code == 0:
                        exit_code = 2
                        manifest["status"] = "cleanup_failed"
            manifest["finished_at_utc"] = _utc_now()
            manifest["exit_code"] = exit_code
            save()
        finally:
            signal.signal(signal.SIGINT, previous_int_handler)
            signal.signal(signal.SIGTERM, previous_term_handler)
    if "error" in manifest:
        print(manifest["error"], file=sys.stderr)
    print(f"Docker workflow: {manifest['status']}. Evidence: {manifest_path}", flush=True)
    return exit_code


def main() -> None:
    try:
        exit_code = launch(parse_arguments())
    except OSError as error:
        print(f"Cannot preserve run evidence: {error}", file=sys.stderr)
        exit_code = 2
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
