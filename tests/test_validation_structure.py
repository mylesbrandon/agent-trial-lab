from pathlib import Path

from runner.validation import validate_task_structure


def test_missing_hidden_tests_is_error(
    make_valid_task,
):
    task_path: Path = make_valid_task()
    (task_path / "test_hidden.py").unlink()

    errors = validate_task_structure(task_path)

    assert "Missing required file: test_hidden.py" in errors
