from pathlib import Path

from agents.prompt_builder import build_one_shot_prompt
from runner.evaluation import discover_tasks


def test_prompt_contains_only_agent_visible_task_material(
    workspace_tmp_path: Path,
):
    task_path = workspace_tmp_path / "task_001_example"
    task_path.mkdir()
    (task_path / "prompt.md").write_text(
        "VISIBLE TASK SPECIFICATION",
        encoding="utf-8",
    )
    (task_path / "starter.py").write_text(
        "# VISIBLE STARTER CODE\n",
        encoding="utf-8",
    )
    (task_path / "test_public.py").write_text(
        "# VISIBLE PUBLIC TESTS\n",
        encoding="utf-8",
    )
    (task_path / "reference_solution.py").write_text(
        "# PRIVATE REFERENCE SOLUTION\n",
        encoding="utf-8",
    )
    (task_path / "test_hidden.py").write_text(
        "# PRIVATE HIDDEN TESTS\n",
        encoding="utf-8",
    )
    (task_path / "baseline_solution.py").write_text(
        "# PRIVATE FLAWED BASELINE\n",
        encoding="utf-8",
    )

    prompt = build_one_shot_prompt(task_path)

    assert "VISIBLE TASK SPECIFICATION" in prompt
    assert "VISIBLE STARTER CODE" in prompt
    assert "VISIBLE PUBLIC TESTS" in prompt
    assert "PRIVATE REFERENCE SOLUTION" not in prompt
    assert "PRIVATE HIDDEN TESTS" not in prompt
    assert "PRIVATE FLAWED BASELINE" not in prompt


def test_all_benchmark_task_prompts_can_be_built():
    task_paths = discover_tasks(Path("tasks"))

    prompts = [
        build_one_shot_prompt(task_path)
        for task_path in task_paths
    ]

    assert len(prompts) == 4
    assert all("TASK SPECIFICATION" in prompt for prompt in prompts)
    assert all("STARTER CODE" in prompt for prompt in prompts)
    assert all("PUBLIC TESTS" in prompt for prompt in prompts)
    assert all(
        "reference_solution.py" not in prompt
        for prompt in prompts
    )
    assert all("test_hidden.py" not in prompt for prompt in prompts)
    assert all("baseline solution" not in prompt for prompt in prompts)
