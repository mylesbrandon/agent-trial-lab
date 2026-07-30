import json
from pathlib import Path

from agents.base import AgentResponse, CodingAgent
from agents.manual_agent import ManualAgent
from agents.mock_agent import MockAgent
from agents.prompt_builder import build_one_shot_prompt
from runner.generate_candidates import (
    generate_candidate,
    generate_candidates,
    select_tasks,
)


class InvalidSyntaxAgent(CodingAgent):
    def generate(self, prompt: str) -> AgentResponse:
        return AgentResponse(
            text="def broken(:\n    pass",
            model="invalid-agent",
            condition="one_shot",
        )


def test_manual_agent_collects_input_until_eof(
    monkeypatch,
    capsys,
):
    responses = iter(["def solve(value):", "    return value"])

    def fake_input():
        try:
            return next(responses)
        except StopIteration as exc:
            raise EOFError from exc

    monkeypatch.setattr("builtins.input", fake_input)

    response = ManualAgent("manual-test").generate("PROMPT")

    assert response == AgentResponse(
        text="def solve(value):\n    return value",
        model="manual-test",
        condition="one_shot",
    )
    assert "PROMPT" in capsys.readouterr().out


def test_select_tasks_accepts_one_task_or_all(
    make_valid_task,
    workspace_tmp_path: Path,
):
    first = make_valid_task(
        folder_name="task_001_first",
        task_id="task_001",
    )
    second = make_valid_task(
        folder_name="task_002_second",
        task_id="task_002",
    )

    assert select_tasks(workspace_tmp_path, ["task_002"]) == [
        second
    ]
    assert select_tasks(workspace_tmp_path, ["all"]) == [
        first,
        second,
    ]


def test_mock_agent_generates_all_tasks(
    make_valid_task,
    workspace_tmp_path: Path,
):
    task_paths = [
        make_valid_task(
            folder_name=f"{task_id}_example",
            task_id=task_id,
        )
        for task_id in (
            "task_001",
            "task_002",
            "task_003",
            "task_004",
        )
    ]
    solution_directory = workspace_tmp_path / "mock_solutions"
    solution_directory.mkdir()

    for task_id in (
        "task_001",
        "task_002",
        "task_003",
        "task_004",
    ):
        (solution_directory / f"{task_id}.py").write_text(
            f"TASK_ID = {task_id!r}\n",
            encoding="utf-8",
        )

    results_root = workspace_tmp_path / "results"
    generation_results = generate_candidates(
        agent=MockAgent(solution_directory),
        agent_adapter="mock",
        task_paths=task_paths,
        model="mock-agent",
        condition="one_shot",
        results_root=results_root,
    )

    assert [
        result["generation_status"]
        for result in generation_results
    ] == ["success"] * 4

    for task_id in (
        "task_001",
        "task_002",
        "task_003",
        "task_004",
    ):
        expected_source = f"TASK_ID = {task_id!r}\n"
        generation_directory = (
            results_root
            / "generations"
            / "mock-agent"
            / "one_shot"
            / task_id
        )
        candidate_path = (
            results_root
            / "candidates"
            / "generated"
            / "mock-agent"
            / "one_shot"
            / f"{task_id}.py"
        )

        expected_prompt = build_one_shot_prompt(
            next(
                task_path
                for task_path in task_paths
                if task_path.name.startswith(task_id)
            )
        )
        assert (
            generation_directory / "request.md"
        ).read_bytes() == expected_prompt.encode("utf-8")
        assert (
            generation_directory / "raw_response.txt"
        ).read_text(encoding="utf-8") == expected_source
        assert (
            generation_directory / "extracted_solution.py"
        ).read_text(encoding="utf-8") == expected_source
        assert candidate_path.read_text(
            encoding="utf-8"
        ) == expected_source

        metadata = json.loads(
            (
                generation_directory / "generation.json"
            ).read_text(encoding="utf-8")
        )
        assert metadata == {
            "task_id": task_id,
            "model": "mock-agent",
            "condition": "one_shot",
            "agent_adapter": "mock",
            "prompt_file": "request.md",
            "parse_status": "success",
            "generation_status": "success",
            "raw_response_file": "raw_response.txt",
            "candidate_file": "extracted_solution.py",
        }


def test_syntax_error_preserves_response_without_candidate(
    make_valid_task,
    workspace_tmp_path: Path,
):
    task_path = make_valid_task()
    results_root = workspace_tmp_path / "results"
    stale_candidate = (
        results_root
        / "candidates"
        / "generated"
        / "invalid-agent"
        / "one_shot"
        / "task_001.py"
    )
    stale_candidate.parent.mkdir(parents=True)
    stale_candidate.write_text(
        "stale = True\n",
        encoding="utf-8",
    )

    result = generate_candidate(
        agent=InvalidSyntaxAgent(),
        agent_adapter="invalid",
        task_path=task_path,
        model="invalid-agent",
        condition="one_shot",
        results_root=results_root,
    )

    generation_directory = (
        results_root
        / "generations"
        / "invalid-agent"
        / "one_shot"
        / "task_001"
    )
    raw_response_path = (
        generation_directory / "raw_response.txt"
    )

    assert result["generation_status"] == "completed"
    assert result["parse_status"] == "failed"
    assert "not valid Python" in result["error"]
    assert raw_response_path.read_bytes() == (
        b"def broken(:\n    pass"
    )
    assert not (
        generation_directory / "extracted_solution.py"
    ).exists()
    assert not stale_candidate.exists()

    recorded_metadata = json.loads(
        (generation_directory / "generation.json").read_text(
            encoding="utf-8"
        )
    )
    assert recorded_metadata == result
