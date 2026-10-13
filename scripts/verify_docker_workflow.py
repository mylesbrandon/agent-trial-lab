"""Real Docker regression checks; run after the default reference CLI in CI.

This deliberately stays outside pytest's native, cross-platform harness suite.
It requires a local Linux Docker engine and uses the image from the first run.
"""
from __future__ import annotations

import argparse
import json
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def single_run(parent: Path) -> Path:
    runs = list(parent.glob("*/docker-run.json"))
    assert len(runs) == 1, f"Expected one run under {parent}, found {len(runs)}"
    return runs[0].parent


def assert_removed(run: Path) -> dict:
    manifest = read_json(run / "docker-run.json")
    assert manifest["cleanup"]["confirmed"], manifest
    result = subprocess.run(["docker", "container", "inspect", manifest["container_name"]],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and "No such container" in result.stderr, result
    return manifest


def command(image: str, output: Path, *extra: str) -> list[str]:
    return [sys.executable, "-m", "runner.docker_benchmark", "--image", image,
            "--results-root", str(output), *extra]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    args = parser.parse_args()
    output = args.results_root.resolve()
    reference = single_run(output / "reference")
    manifest = assert_removed(reference)
    assert manifest["status"] == "completed" and manifest["exit_code"] == 0
    assert manifest["image"]["os"] == "linux"
    image = manifest["image"]["id"]
    quality = read_json(reference / "quality.json")
    assert quality["quality_passed"]
    assert (quality["task_count"], quality["total_test_count"], quality["reference_tasks_passed"],
            quality["starter_tasks_rejected"], quality["defect_fixtures_detected"]) == (32, 373, 32, 32, 39)
    summary = read_json(next((reference / "evaluation/summaries").glob("*.json")))
    assert summary["task_count"] == summary["attempted_count"] == 32
    assert summary["missing_count"] == 0 and summary["overall_pass_rate"] == 1.0

    candidates = output / "timeout candidates, with spaces"
    shutil.copytree(ROOT / "results/candidates/reference", candidates)
    (candidates / "task_001.py").write_text("while True:\n    pass\n", encoding="utf-8")
    subprocess.run(command(image, output / "suite-timeout", "--solution-set", str(candidates),
                           "--model", "timeout-probe", "--timeout-seconds", "2"),
                   check=True, cwd=ROOT, timeout=660)
    timed_suite = single_run(output / "suite-timeout")
    assert_removed(timed_suite)
    task_results = [read_json(path) for path in (timed_suite / "evaluation/runs").glob("*/*/result.json")]
    assert len(task_results) == 32
    first = next(row for row in task_results if row["task_id"] == "task_001")
    assert first["public_execution"]["status"] == first["hidden_execution"]["status"] == "timeout"
    assert sum(row["overall_passed"] for row in task_results) == 31
    summary = read_json(next((timed_suite / "evaluation/summaries").glob("*.json")))
    assert summary["overall_pass_rate"] == 31 / 32

    deadline = subprocess.run(command(image, output / "deadline", "--run-timeout-seconds", "2"),
                              cwd=ROOT, timeout=60)
    assert deadline.returncode == 124
    deadline_manifest = assert_removed(single_run(output / "deadline"))
    assert deadline_manifest["status"] == "timed_out"

    process = subprocess.Popen(command(image, output / "interrupted"), cwd=ROOT)
    try:
        limit = time.monotonic() + 30
        while time.monotonic() < limit:
            paths = list((output / "interrupted").glob("*/docker-run.json"))
            if paths:
                running = read_json(paths[0])
                if running["status"] == "running":
                    result = subprocess.run(["docker", "inspect", "--format", "{{.State.Running}}", running["container_name"]],
                                            capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip() == "true":
                        break
            assert process.poll() is None, "Launcher exited before the interruption probe."
            time.sleep(0.1)
        else:
            raise AssertionError("Container did not start before interruption deadline.")
        process.send_signal(signal.SIGTERM)
        assert process.wait(timeout=45) == 130
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=45)
    interrupted = assert_removed(single_run(output / "interrupted"))
    assert interrupted["status"] == "interrupted"
    print("Docker integration verified: 32/32 references, 373 tests, 39 defects; suite timeout continues; deadline and SIGTERM remove containers.")


if __name__ == "__main__":
    main()
