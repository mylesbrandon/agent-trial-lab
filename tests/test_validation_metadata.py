import json
from pathlib import Path

from runner.validation import (
    validate_all_tasks,
    validate_metadata,
)


def _read_metadata(task_path: Path) -> dict:
    return json.loads(
        (task_path / "metadata.json").read_text(encoding="utf-8")
    )


def _write_metadata(task_path: Path, metadata: dict) -> None:
    (task_path / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )


def test_invalid_difficulty_is_error(make_valid_task):
    task_path = make_valid_task()
    metadata = _read_metadata(task_path)
    metadata["difficulty"] = "moderate"
    _write_metadata(task_path, metadata)

    _, errors = validate_metadata(task_path)

    assert (
        'difficulty must be easy, medium, or hard; '
        'received "moderate"'
    ) in errors


def test_malformed_metadata_is_error(make_valid_task):
    task_path = make_valid_task()
    (task_path / "metadata.json").write_text(
        "{not valid json",
        encoding="utf-8",
    )

    _, errors = validate_metadata(task_path)

    assert any("could not be parsed" in error for error in errors)


def test_duplicate_task_ids_are_errors(
    workspace_tmp_path: Path,
    make_valid_task,
):
    make_valid_task("task_001_first", "task_001")
    make_valid_task("task_001_second", "task_001")

    report = validate_all_tasks(workspace_tmp_path)

    assert report["benchmark_valid"] is False
    assert all(
        "Duplicate task_id: task_001" in task["errors"]
        for task in report["tasks"]
    )


def test_skipped_task_id_is_warning(
    workspace_tmp_path: Path,
    make_valid_task,
):
    make_valid_task("task_001_first", "task_001")
    make_valid_task("task_003_third", "task_003")

    report = validate_all_tasks(workspace_tmp_path)

    assert report["benchmark_valid"] is True
    assert report["warning_count"] == 1
    assert (
        "Task IDs skip from task_001 to task_003"
        in report["tasks"][1]["warnings"]
    )
