import json
from pathlib import Path

from runner.evaluation import build_missing_result


def test_missing_candidate_is_recorded(
    workspace_tmp_path: Path,
):
    task_path = workspace_tmp_path / "task_001_example"
    task_path.mkdir()

    metadata = {
        "task_id": "task_001",
        "name": "example",
        "category": "testing",
        "difficulty": "easy",
    }

    (task_path / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    candidate_path = (
        workspace_tmp_path / "solutions" / "task_001.py"
    )

    result = build_missing_result(
        task_path=task_path,
        model="test-model",
        condition="one_shot",
        expected_candidate_path=candidate_path,
    )

    assert result["status"] == "missing_candidate"
    assert result["public_passed"] is False
    assert result["hidden_passed"] is False
    assert result["overall_passed"] is False
    assert result["run_id"] is None
