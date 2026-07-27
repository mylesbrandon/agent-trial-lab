from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
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


def run_pytest(test_file: Path, working_directory: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            test_file.name,
        ],
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=False,
    )

    combined_output = completed.stdout

    if completed.stderr:
        combined_output += "\n--- STDERR ---\n"
        combined_output += completed.stderr

    return {
        "passed": completed.returncode == 0,
        "returncode": completed.returncode,
        "output": combined_output,
        "failed_tests": extract_failed_tests(combined_output),
    }


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
) -> dict[str, Any]:
    """
    Evaluate one candidate without modifying the original task.

    The candidate replaces starter.py only inside a temporary copy.
    """
    task_path = task_path.resolve()
    solution_path = solution_path.resolve()
    results_root = results_root.resolve()

    if not solution_path.exists():
        raise FileNotFoundError(
            f"Candidate solution does not exist: {solution_path}"
        )

    metadata = load_metadata(task_path)
    task_id = metadata["task_id"]

    run_id = create_run_id(task_id, model, condition)
    run_directory = results_root / "runs" / task_id / run_id
    run_directory.mkdir(parents=True, exist_ok=False)

    with workspace_temporary_directory(
        results_root,
        ".eval_",
    ) as temporary_directory:
        temporary_task = temporary_directory / task_path.name

        shutil.copytree(task_path, temporary_task)
        shutil.copy2(
            solution_path,
            temporary_task / "starter.py",
        )

        public_result = run_pytest(
            temporary_task / "test_public.py",
            temporary_task,
        )

        hidden_result = run_pytest(
            temporary_task / "test_hidden.py",
            temporary_task,
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

    shutil.copy2(
        solution_path,
        run_directory / "candidate_snapshot.py",
    )

    prompt_path = task_path / "prompt.md"

    if prompt_path.exists():
        shutil.copy2(
            prompt_path,
            run_directory / "prompt.md",
        )

    (run_directory / "public_test_output.txt").write_text(
        public_result["output"],
        encoding="utf-8",
    )

    (run_directory / "hidden_test_output.txt").write_text(
        hidden_result["output"],
        encoding="utf-8",
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
