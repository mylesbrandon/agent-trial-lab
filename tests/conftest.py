from __future__ import annotations

import json
from pathlib import Path

import pytest

from runner.evaluation import workspace_temporary_directory


@pytest.fixture
def workspace_tmp_path():
    with workspace_temporary_directory(
        Path.cwd(),
        ".pytest_workspace_",
    ) as temporary_path:
        yield temporary_path


@pytest.fixture
def make_valid_task(workspace_tmp_path: Path):
    def make_task(
        folder_name: str = "task_001_example",
        task_id: str = "task_001",
    ) -> Path:
        task_path = workspace_tmp_path / folder_name
        task_path.mkdir()

        metadata = {
            "task_id": task_id,
            "name": "example",
            "category": "testing",
            "difficulty": "easy",
            "concepts": ["identity"],
            "public_tests": 1,
            "hidden_tests": 1,
            "failure_modes_targeted": ["wrong_value"],
            "contract_keywords": ["identity"],
        }

        (task_path / "metadata.json").write_text(
            json.dumps(metadata),
            encoding="utf-8",
        )
        (task_path / "prompt.md").write_text(
            "Repair the identity function.",
            encoding="utf-8",
        )
        (task_path / "starter.py").write_text(
            "def solve(value):\n    return value + 1\n",
            encoding="utf-8",
        )
        (task_path / "reference_solution.py").write_text(
            "def solve(value):\n    return value\n",
            encoding="utf-8",
        )
        (task_path / "test_public.py").write_text(
            "from starter import solve\n\n"
            "def test_public_identity():\n"
            "    assert solve(1) == 1\n",
            encoding="utf-8",
        )
        (task_path / "test_hidden.py").write_text(
            "from starter import solve\n\n"
            "def test_hidden_identity():\n"
            "    assert solve(-1) == -1\n",
            encoding="utf-8",
        )
        return task_path

    return make_task
