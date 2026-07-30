from pathlib import Path


def build_one_shot_prompt(task_path: Path) -> str:
    """Build a prompt using only agent-visible task files."""
    task_prompt = (task_path / "prompt.md").read_text(
        encoding="utf-8"
    )
    starter_code = (task_path / "starter.py").read_text(
        encoding="utf-8"
    )
    public_tests = (task_path / "test_public.py").read_text(
        encoding="utf-8"
    )

    return f"""You are solving a Python code-repair benchmark task.

Follow the written specification exactly.

Return only the complete contents of starter.py after your repair.
Do not include Markdown fences, explanations, tests, or commentary.

TASK SPECIFICATION
------------------
{task_prompt}

STARTER CODE
------------
{starter_code}

PUBLIC TESTS
------------
{public_tests}
"""
