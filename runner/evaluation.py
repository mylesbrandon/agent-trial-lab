from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


FAILED_TEST_PATTERN = re.compile(
    r"^FAILED\s+.+?::([^\s]+)",
    re.MULTILINE,
)
DEFAULT_TIMEOUT_SECONDS = 10.0


@contextmanager
def workspace_temporary_directory(
    parent: Path,
    prefix: str,
):
    """
    Create an inherited-permission temporary directory.

    Python 3.14's Windows tempfile permissions can conflict with a
    sandbox ACL, so benchmark copies use an explicit workspace child.
    """
    temporary_path = (
        parent.resolve() / f"{prefix}{uuid4().hex}"
    )
    temporary_path.mkdir(parents=True, exist_ok=False)

    try:
        yield temporary_path
    finally:
        shutil.rmtree(temporary_path)


def slugify(value: str) -> str:
    """Convert a model/condition name into a filename-safe string."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    return cleaned.strip("_").lower() or "unknown"


def load_metadata(task_path: Path) -> dict[str, Any]:
    metadata_path = task_path / "metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Missing metadata file: {metadata_path}"
        )

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    required_fields = {
        "task_id",
        "name",
        "category",
        "difficulty",
    }

    missing_fields = required_fields - metadata.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(
            f"{metadata_path} is missing required fields: {missing}"
        )

    return metadata


def discover_tasks(tasks_directory: Path) -> list[Path]:
    """Return task directories in deterministic order."""
    if not tasks_directory.exists():
        raise FileNotFoundError(
            f"Tasks directory does not exist: {tasks_directory}"
        )

    return sorted(
        (
            path
            for path in tasks_directory.iterdir()
            if path.is_dir() and path.name.startswith("task_")
        ),
        key=lambda path: path.name,
    )


def extract_failed_tests(output: str) -> list[str]:
    """Extract pytest test names from its terminal output."""
    return FAILED_TEST_PATTERN.findall(output)


def positive_timeout(value: str | float) -> float:
    """Reject unbounded, zero, or negative execution deadlines."""
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")
    return timeout


def run_pytest(
    test_file: Path,
    working_directory: Path,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run a suite with a deadline and require evidence of executed tests.

    These controls make trusted-code evaluation repeatable. They are not a
    security sandbox: candidate code still has the current user's privileges.
    """
    timeout_seconds = positive_timeout(timeout_seconds)
    working_directory = working_directory.resolve()
    report_path = working_directory / f".pytest_report_{uuid4().hex}.xml"
    environment = {
        key: value for key, value in os.environ.items()
        if not key.startswith("PYTEST_")
    }
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    started = time.monotonic()
    timed_out = False
    with subprocess.Popen(
        [
            sys.executable, "-I", "-B", "-m", "pytest", "-q",
            "-p", "no:cacheprovider", "-c", os.devnull,
            f"--confcutdir={working_directory}",
            f"--junitxml={report_path}", test_file.name,
        ],
        cwd=working_directory,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=os.name == "posix",
    ) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            stdout, stderr = process.communicate()
        returncode = process.returncode

    combined_output = stdout
    if stderr:
        combined_output += "\n--- STDERR ---\n"
        combined_output += stderr

    counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    failed_tests: list[str] = []
    junit_xml = None
    diagnostic = None
    try:
        junit_xml = report_path.read_text(encoding="utf-8")
        report = ET.fromstring(junit_xml)
        if report.tag not in {"testsuites", "testsuite"}:
            raise ValueError("unexpected JUnit report root")
        cases = report.findall(".//testcase")
        counts["tests"] = len(cases)
        for case in cases:
            for kind, field in (
                ("failure", "failures"), ("error", "errors"),
                ("skipped", "skipped"),
            ):
                if case.find(kind) is not None:
                    counts[field] += 1
            if case.find("failure") is not None or case.find("error") is not None:
                failed_tests.append(case.get("name", "unknown"))
        if not cases:
            diagnostic = "No tests were recorded in the JUnit report."
    except (OSError, UnicodeError, ET.ParseError, ValueError) as error:
        diagnostic = f"Missing or invalid JUnit report: {error}"
    finally:
        report_path.unlink(missing_ok=True)

    if timed_out:
        diagnostic = f"Test suite exceeded {timeout_seconds:g} seconds."
        combined_output += f"\n--- TIMEOUT ---\n{diagnostic}\n"

    passed = (
        not timed_out and returncode == 0 and diagnostic is None
        and counts["tests"] > 0
        and not any(counts[field] for field in ("failures", "errors", "skipped"))
    )
    status = (
        "timeout" if timed_out else "passed" if passed
        else "error" if diagnostic or counts["errors"] or returncode not in (0, 1)
        else "failed"
    )

    return {
        "passed": passed,
        "status": status,
        "returncode": returncode,
        "duration_seconds": time.monotonic() - started,
        **counts,
        "diagnostic": diagnostic,
        "output": combined_output,
        "failed_tests": failed_tests or extract_failed_tests(combined_output),
        "junit_xml": junit_xml,
    }


def run_solution_suites(
    task_path: Path,
    candidate_source: bytes,
    temporary_parent: Path,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Use independent suite copies containing only candidate and test code."""
    suites = {
        suite: (task_path / f"test_{suite}.py").read_bytes()
        for suite in ("public", "hidden")
    }
    results = []
    for suite, test_source in suites.items():
        with workspace_temporary_directory(temporary_parent, ".eval_") as temporary:
            (temporary / "starter.py").write_bytes(candidate_source)
            test_file = temporary / f"test_{suite}.py"
            test_file.write_bytes(test_source)
            results.append(run_pytest(test_file, temporary, timeout_seconds))
    return results[0], results[1]


def create_run_id(
    task_id: str,
    model: str,
    condition: str,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    return "_".join(
        [
            timestamp,
            slugify(task_id),
            slugify(model),
            slugify(condition),
        ]
    )


def evaluate_candidate(
    task_path: Path,
    solution_path: Path,
    model: str,
    condition: str,
    results_root: Path,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """
    Evaluate one candidate without modifying the original task.

    The exact candidate and grading files are saved before execution.
    """
    task_path = task_path.resolve()
    solution_path = solution_path.resolve()
    results_root = results_root.resolve()
    timeout_seconds = positive_timeout(timeout_seconds)

    if not solution_path.exists():
        raise FileNotFoundError(
            f"Candidate solution does not exist: {solution_path}"
        )

    metadata = load_metadata(task_path)
    task_id = metadata["task_id"]
    candidate_source = solution_path.read_bytes()
    task_sources = {
        filename: (task_path / filename).read_bytes()
        for filename in (
            "metadata.json", "test_public.py", "test_hidden.py",
            "prompt.md", "starter.py",
        )
        if (task_path / filename).is_file()
    }
    for filename in ("test_public.py", "test_hidden.py"):
        if filename not in task_sources:
            raise FileNotFoundError(f"Missing required test file: {task_path / filename}")

    run_id = create_run_id(task_id, model, condition)
    run_directory = results_root / "runs" / task_id / run_id
    run_directory.mkdir(parents=True, exist_ok=False)
    (run_directory / "candidate_snapshot.py").write_bytes(candidate_source)
    task_snapshot = run_directory / "task_snapshot"
    task_snapshot.mkdir()
    for filename, source in task_sources.items():
        (task_snapshot / filename).write_bytes(source)
    if "prompt.md" in task_sources:
        (run_directory / "prompt.md").write_bytes(task_sources["prompt.md"])

    public_result, hidden_result = run_solution_suites(
        task_snapshot, candidate_source, results_root, timeout_seconds,
    )

    public_passed = public_result["passed"]
    hidden_passed = hidden_result["passed"]

    result = {
        "run_id": run_id,
        "task_id": task_id,
        "task_name": metadata["name"],
        "category": metadata["category"],
        "difficulty": metadata["difficulty"],
        "model": model,
        "condition": condition,
        "status": "attempted",
        "candidate_path": str(solution_path),
        "candidate_sha256": hashlib.sha256(candidate_source).hexdigest(),
        "task_file_sha256": {
            filename: hashlib.sha256(source).hexdigest()
            for filename, source in task_sources.items()
        },
        "runtime": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "pytest": importlib.metadata.version("pytest"),
        },
        "timeout_seconds": timeout_seconds,
        "public_execution": {
            key: value for key, value in public_result.items()
            if key not in {"output", "junit_xml"}
        },
        "hidden_execution": {
            key: value for key, value in hidden_result.items()
            if key not in {"output", "junit_xml"}
        },
        "public_passed": public_passed,
        "hidden_passed": hidden_passed,
        "overall_passed": public_passed and hidden_passed,
        "failed_public_tests": public_result["failed_tests"],
        "failed_hidden_tests": hidden_result["failed_tests"],
        "public_returncode": public_result["returncode"],
        "hidden_returncode": hidden_result["returncode"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_path": str(run_directory),
    }

    (run_directory / "public_test_output.txt").write_text(
        public_result["output"],
        encoding="utf-8",
    )

    (run_directory / "hidden_test_output.txt").write_text(
        hidden_result["output"],
        encoding="utf-8",
    )
    for suite, suite_result in (("public", public_result), ("hidden", hidden_result)):
        if suite_result["junit_xml"] is not None:
            (run_directory / f"{suite}_test_results.xml").write_text(
                suite_result["junit_xml"], encoding="utf-8",
            )

    with (run_directory / "result.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(result, file, indent=2)

    return result


def build_missing_result(
    task_path: Path,
    model: str,
    condition: str,
    expected_candidate_path: Path,
) -> dict[str, Any]:
    metadata = load_metadata(task_path)

    return {
        "run_id": None,
        "task_id": metadata["task_id"],
        "task_name": metadata["name"],
        "category": metadata["category"],
        "difficulty": metadata["difficulty"],
        "model": model,
        "condition": condition,
        "status": "missing_candidate",
        "candidate_path": str(expected_candidate_path),
        "public_passed": False,
        "hidden_passed": False,
        "overall_passed": False,
        "failed_public_tests": [],
        "failed_hidden_tests": [],
        "public_returncode": None,
        "hidden_returncode": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_path": None,
    }


def build_summary(
    results: list[dict[str, Any]],
    model: str,
    condition: str,
) -> dict[str, Any]:
    task_count = len(results)
    attempted_count = sum(
        result["status"] == "attempted"
        for result in results
    )
    missing_count = sum(
        result["status"] == "missing_candidate"
        for result in results
    )

    public_pass_count = sum(
        bool(result["public_passed"])
        for result in results
    )
    hidden_pass_count = sum(
        bool(result["hidden_passed"])
        for result in results
    )
    overall_pass_count = sum(
        bool(result["overall_passed"])
        for result in results
    )

    denominator = task_count or 1

    public_pass_rate = public_pass_count / denominator
    hidden_pass_rate = hidden_pass_count / denominator
    overall_pass_rate = overall_pass_count / denominator

    category_results: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "tasks": 0,
            "attempted": 0,
            "passed": 0,
        }
    )

    for result in results:
        category = result["category"]
        category_results[category]["tasks"] += 1

        if result["status"] == "attempted":
            category_results[category]["attempted"] += 1

        if result["overall_passed"]:
            category_results[category]["passed"] += 1

    return {
        "model": model,
        "condition": condition,
        "task_count": task_count,
        "attempted_count": attempted_count,
        "missing_count": missing_count,
        "public_pass_count": public_pass_count,
        "hidden_pass_count": hidden_pass_count,
        "overall_pass_count": overall_pass_count,
        "public_pass_rate": public_pass_rate,
        "hidden_pass_rate": hidden_pass_rate,
        "overall_pass_rate": overall_pass_rate,
        "public_hidden_gap": public_pass_rate - hidden_pass_rate,
        "category_results": dict(category_results),
    }


def write_summary_files(
    results: list[dict[str, Any]],
    model: str,
    condition: str,
    summaries_directory: Path,
) -> tuple[Path, Path, dict[str, Any]]:
    summaries_directory.mkdir(parents=True, exist_ok=True)

    file_stem = slugify(f"{model}_{condition}")

    csv_path = summaries_directory / f"{file_stem}_results.csv"
    json_path = summaries_directory / f"{file_stem}_summary.json"

    columns = [
        "run_id",
        "task_id",
        "task_name",
        "category",
        "difficulty",
        "model",
        "condition",
        "status",
        "public_passed",
        "hidden_passed",
        "overall_passed",
        "failed_public_test_count",
        "failed_hidden_test_count",
        "run_path",
    ]

    with csv_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "run_id": result["run_id"],
                    "task_id": result["task_id"],
                    "task_name": result["task_name"],
                    "category": result["category"],
                    "difficulty": result["difficulty"],
                    "model": result["model"],
                    "condition": result["condition"],
                    "status": result["status"],
                    "public_passed": result["public_passed"],
                    "hidden_passed": result["hidden_passed"],
                    "overall_passed": result["overall_passed"],
                    "failed_public_test_count": len(
                        result["failed_public_tests"]
                    ),
                    "failed_hidden_test_count": len(
                        result["failed_hidden_tests"]
                    ),
                    "run_path": result["run_path"],
                }
            )

    summary = build_summary(results, model, condition)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return csv_path, json_path, summary
