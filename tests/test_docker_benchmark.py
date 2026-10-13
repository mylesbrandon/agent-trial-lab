"""Host orchestration contracts without requiring a local Docker daemon.

Linux CI exercises the real image. These tests inject failures at the Docker
process boundary to verify evidence, deadlines, cleanup, and mount handling.
"""
from __future__ import annotations

import csv
import json
import signal
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from runner import docker_benchmark as launcher


IMAGE_ID = "sha256:" + "a" * 64


class DockerProcessDouble:
    def __init__(self):
        self.calls = []
        self.engine_os = "linux"
        self.image_os = "linux"
        self.run_exit = 0
        self.workflow = {"status": "completed", "exit_code": 0}
        self.failure_phase = None
        self.failure = None
        self.cleanup_exit = 0
        self.cleanup_stderr = ""

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        phase = command[1]
        if phase == self.failure_phase:
            if self.failure == "sigterm":
                signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
            raise self.failure
        if phase == "info":
            stdout = self.engine_os + "\n"
        elif phase == "image":
            stdout = json.dumps([{
                "Id": IMAGE_ID, "Os": self.image_os, "Architecture": "amd64",
                "RepoDigests": ["example/bench@" + IMAGE_ID],
            }])
        elif phase == "build":
            Path(command[command.index("--iidfile") + 1]).write_text(IMAGE_ID + "\n")
            stdout = ""
        elif phase == "run":
            for index, value in enumerate(command):
                if value == "--mount":
                    fields = next(csv.reader([command[index + 1]]))
                    if "target=/output" in fields:
                        output = Path(next(field.removeprefix("source=") for field in fields if field.startswith("source=")))
                        if self.workflow is not None:
                            (output / "workflow.json").write_text(json.dumps(self.workflow))
            return subprocess.CompletedProcess(command, self.run_exit)
        elif phase == "rm":
            return subprocess.CompletedProcess(command, self.cleanup_exit, "", self.cleanup_stderr)
        else:
            raise AssertionError(f"Unexpected Docker operation: {command}")
        return subprocess.CompletedProcess(command, 0, stdout, "")

    def commands(self, phase):
        return [(cmd, options) for cmd, options in self.calls if cmd[1] == phase]


@pytest.fixture
def docker(monkeypatch):
    process = DockerProcessDouble()
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/fake/docker")
    monkeypatch.setattr(launcher.subprocess, "run", process)
    # Replace only the launcher's OS dependency. Patching the shared os module
    # changes pytest's identity checks for its own temporary directories.
    monkeypatch.setattr(launcher, "os", SimpleNamespace(
        getuid=lambda: 501, getgid=lambda: 20,
    ))
    return process


def arguments(output, *extra):
    return launcher.parse_arguments(["--results-root", str(output), *extra])


def manifest(output):
    manifests = list(output.glob("*/docker-run.json"))
    assert len(manifests) == 1
    return json.loads(manifests[0].read_text())


def test_build_evaluate_and_preserve_exact_image_identity(docker, tmp_path):
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 0
    report = manifest(output)
    assert report["status"] == "completed"
    assert report["require_all_pass"] is True
    assert report["image"]["id"] == IMAGE_ID
    assert report["image"]["architecture"] == "amd64"
    assert report["cleanup"]["confirmed"] is True
    build, build_options = docker.commands("build")[0]
    assert build_options["timeout"] == 600
    assert build_options["check"] is True
    run, run_options = docker.commands("run")[0]
    assert IMAGE_ID in run
    assert run_options["timeout"] == 600
    assert Path(build[build.index("--iidfile") + 1]).parent == Path(report["output_directory"])
    assert report["started_at_utc"] <= report["finished_at_utc"]


def test_existing_tag_is_resolved_before_execution(docker, tmp_path):
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output, "--image", "example/bench:moving")) == 0
    assert not docker.commands("build")
    assert docker.commands("image")[0][0][-1] == "example/bench:moving"
    run = docker.commands("run")[0][0]
    assert IMAGE_ID in run
    assert "example/bench:moving" not in run


def test_candidate_paths_with_spaces_and_commas_are_exact_and_readonly(docker, tmp_path):
    candidates = tmp_path / 'candidate set, with spaces'
    candidates.mkdir()
    output = tmp_path / "output with spaces, commas"
    args = arguments(output, "--solution-set", str(candidates),
                     "--model", "model with spaces", "--require-all-pass")
    assert launcher.launch(args) == 0
    run = docker.commands("run")[0][0]
    mounts = [next(csv.reader([run[index + 1]]))
              for index, value in enumerate(run) if value == "--mount"]
    input_mount = next(fields for fields in mounts if "target=/candidates" in fields)
    assert f"source={candidates.resolve()}" in input_mount
    assert "readonly" in input_mount
    output_mount = next(fields for fields in mounts if "target=/output" in fields)
    assert f"source={manifest(output)['output_directory']}" in output_mount
    assert "readonly" not in output_mount
    assert len(mounts) == 2
    assert run[run.index("--model") + 1] == "model with spaces"
    assert "--require-all-pass" in run
    assert run[run.index("--solution-set") + 1] == "/candidates"


def test_runtime_bounds_privileges_and_preserves_host_file_ownership(docker, tmp_path):
    assert launcher.launch(arguments(tmp_path / "reports")) == 0
    run = docker.commands("run")[0][0]
    values = {
        "--network": "none", "--cap-drop": "ALL",
        "--security-opt": "no-new-privileges", "--pids-limit": "128",
        "--memory": "1g", "--memory-swap": "1g", "--cpus": "2",
        "--user": "501:20",
    }
    for option, expected in values.items():
        assert run[run.index(option) + 1] == expected
    assert "--read-only" in run
    assert "--init" in run
    assert "--privileged" not in run
    assert "docker.sock" not in " ".join(run)
    assert "mode=1777" in run[run.index("--tmpfs") + 1]


def test_root_host_still_runs_container_unprivileged(docker, tmp_path, monkeypatch):
    ownership_changes = []
    monkeypatch.setattr(launcher.os, "getuid", lambda: 0)
    monkeypatch.setattr(launcher.os, "chown", lambda *args: ownership_changes.append(args), raising=False)
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 0
    report = manifest(output)
    assert ownership_changes == [(Path(report["output_directory"]), 10001, 10001)]
    run = docker.commands("run")[0][0]
    assert run[run.index("--user") + 1] == "10001:10001"


@pytest.mark.parametrize("phase,expected_status", [
    ("run", "timed_out"), ("build", "setup_timed_out"), ("info", "setup_timed_out"),
])
def test_deadlines_preserve_failure_evidence_and_remove_started_container(
    docker, tmp_path, phase, expected_status,
):
    docker.failure_phase = phase
    docker.failure = subprocess.TimeoutExpired(["docker", phase], 7)
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output, "--run-timeout-seconds", "7")) == 124
    report = manifest(output)
    assert report["status"] == expected_status
    assert report["exit_code"] == 124
    assert "7 seconds" in report["error"]
    cleanup = docker.commands("rm")
    if phase == "run":
        assert report["cleanup"]["confirmed"] is True
        assert len(cleanup) == 1
        assert cleanup[0][0] == ["/fake/docker", "rm", "--force", report["container_name"]]
        assert 0 < cleanup[0][1]["timeout"] <= 30
    else:
        assert not cleanup


@pytest.mark.parametrize("interruption", [KeyboardInterrupt(), "sigterm"])
def test_interrupts_cleanup_and_restore_original_signal_handlers(docker, tmp_path, interruption):
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
    docker.failure_phase = "run"
    docker.failure = interruption
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 130
    report = manifest(output)
    assert report["status"] == "interrupted"
    assert report["exit_code"] == 130
    assert report["cleanup"]["confirmed"] is True
    assert len(docker.commands("rm")) == 1
    for sig, handler in previous.items():
        assert signal.getsignal(sig) == handler


@pytest.mark.parametrize("exit_code", [1, 2, 125, -9])
def test_nonzero_container_status_cannot_be_reported_as_success(docker, tmp_path, exit_code):
    docker.run_exit = exit_code
    output = tmp_path / "reports"
    returned = launcher.launch(arguments(output))
    report = manifest(output)
    assert returned != 0
    assert report["exit_code"] == returned
    assert report["status"] == "failed"
    assert report["cleanup"]["confirmed"] is True


def test_cleanup_failure_prevents_success_and_records_how_to_recover(docker, tmp_path, capsys):
    docker.cleanup_exit = 1
    docker.cleanup_stderr = "daemon unavailable"
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 2
    report = manifest(output)
    assert report["status"] == "cleanup_failed"
    assert report["cleanup"] == {"confirmed": False, "diagnostic": "daemon unavailable"}
    assert f"docker rm --force {report['container_name']}" in capsys.readouterr().err


def test_cleanup_timeout_is_bounded_and_retains_original_run_timeout(docker, tmp_path, monkeypatch):
    normal_process = docker.__call__

    def process(command, **kwargs):
        if command[1] in {"run", "rm"}:
            docker.calls.append((command, kwargs))
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return normal_process(command, **kwargs)

    # Replacing the module function keeps the same fake-Docker command history.
    monkeypatch.setattr(launcher.subprocess, "run", process)
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 124
    report = manifest(output)
    assert report["status"] == "timed_out"
    assert report["cleanup"]["confirmed"] is False
    assert docker.commands("rm")[0][1]["timeout"] <= 30


@pytest.mark.parametrize("workflow", [None, {"status": "started", "exit_code": None},
                                       {"status": "completed", "exit_code": 1}])
def test_zero_docker_exit_requires_completed_workflow_evidence(docker, tmp_path, workflow):
    docker.workflow = workflow
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 2
    report = manifest(output)
    assert report["status"] == "error"
    assert report["exit_code"] == 2
    assert report["cleanup"]["confirmed"] is True


def test_already_removed_container_counts_as_confirmed_cleanup(docker, tmp_path):
    docker.cleanup_exit = 1
    docker.cleanup_stderr = "Error response from daemon: No such container: old"
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 0
    assert manifest(output)["cleanup"]["confirmed"] is True


def test_missing_docker_returns_clear_error_without_starting_process(docker, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: None)
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 2
    assert not docker.calls
    assert not output.exists()
    assert "Docker CLI was not found" in capsys.readouterr().err


@pytest.mark.parametrize("unsupported", ["engine", "image"])
def test_non_linux_engine_or_image_never_runs_candidates(docker, tmp_path, unsupported):
    if unsupported == "engine":
        docker.engine_os = "windows"
    else:
        docker.image_os = "windows"
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output, "--image", "example/bench")) == 2
    report = manifest(output)
    assert report["status"] == "error"
    assert "Linux" in report["error"]
    assert not docker.commands("run")
    assert not docker.commands("rm")


def test_failed_build_preserves_diagnostic_without_starting_candidates(docker, tmp_path):
    docker.failure_phase = "build"
    docker.failure = subprocess.CalledProcessError(1, ["docker", "build"], stderr="image build failed")
    output = tmp_path / "reports"
    assert launcher.launch(arguments(output)) == 2
    report = manifest(output)
    assert report["status"] == "error"
    assert "image build failed" in report["error"]
    assert not docker.commands("run")


def test_repeated_invocations_retain_separate_manifests_and_containers(docker, tmp_path):
    output = tmp_path / "reports"
    for _ in range(2):
        assert launcher.launch(arguments(output)) == 0
    reports = [json.loads(path.read_text()) for path in output.glob("*/docker-run.json")]
    assert len(reports) == 2
    assert len({report["run_id"] for report in reports}) == 2
    assert len({report["container_name"] for report in reports}) == 2
    assert all(report["status"] == "completed" for report in reports)
