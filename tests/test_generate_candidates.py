import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

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


class FailingAgent(CodingAgent):
    def generate(self, prompt: str) -> AgentResponse:
        raise RuntimeError("Provider unavailable")


def assert_generation_provenance(metadata, generation_directory):
    started = datetime.fromisoformat(metadata["started_at_utc"])
    completed = datetime.fromisoformat(metadata["completed_at_utc"])
    assert started.utcoffset() == completed.utcoffset() == timedelta(0)
    assert started <= completed
    assert metadata["python_version"]
    assert metadata["python_implementation"]
    assert metadata["platform"]
    for artifact in ("prompt", "raw_response", "candidate"):
        file_key = f"{artifact}_file"
        digest_key = f"{artifact}_sha256"
        if file_key not in metadata:
            assert digest_key not in metadata
            continue
        artifact_bytes = (
            generation_directory / metadata[file_key]
        ).read_bytes()
        assert metadata[digest_key] == hashlib.sha256(
            artifact_bytes
        ).hexdigest()


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

    for result in generation_results:
        task_id = result["task_id"]
        expected_source = f"TASK_ID = {task_id!r}\n"
        generation_directory = (
            results_root
            / "generations"
            / "mock-agent"
            / "one_shot"
            / task_id
            / result["attempt_id"]
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
        assert metadata == result
        assert_generation_provenance(metadata, generation_directory)
        expected_metadata = {
            "task_id": task_id,
            "model": "mock-agent",
            "condition": "one_shot",
            "agent_adapter": "mock",
            "prompt_file": "request.md",
            "parse_status": "success",
            "generation_status": "success",
            "raw_response_file": "raw_response.txt",
            "candidate_file": "extracted_solution.py",
            "response_model": "mock-agent",
            "response_condition": "one_shot",
        }
        assert expected_metadata.items() <= metadata.items()


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
        / result["attempt_id"]
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
    assert_generation_provenance(result, generation_directory)


def test_repeated_generation_preserves_prior_evidence(
    make_valid_task,
    workspace_tmp_path: Path,
):
    task_path = make_valid_task()
    solution_directory = workspace_tmp_path / "mock_solutions"
    solution_directory.mkdir()
    solution_path = solution_directory / "task_001.py"
    results_root = workspace_tmp_path / "results"
    arguments = {
        "agent": MockAgent(solution_directory),
        "agent_adapter": "mock",
        "task_path": task_path,
        "model": "mock-agent",
        "condition": "one_shot",
        "results_root": results_root,
    }
    solution_path.write_text("value = 'first'\n", encoding="utf-8")
    first = generate_candidate(**arguments)
    task_generations = (
        results_root / "generations" / "mock-agent" / "one_shot" / "task_001"
    )
    first_directory = task_generations / first["attempt_id"]
    original_evidence = {
        path.name: path.read_bytes() for path in first_directory.iterdir()
    }

    # Different prompt and response ensure hashes identify actual content.
    (task_path / "prompt.md").write_text("A revised prompt.", encoding="utf-8")
    solution_path.write_text("value = 'second'\n", encoding="utf-8")
    second = generate_candidate(**arguments)

    assert first["attempt_id"] != second["attempt_id"]
    assert len(list(task_generations.iterdir())) == 2
    assert {
        path.name: path.read_bytes() for path in first_directory.iterdir()
    } == original_evidence
    for artifact in ("prompt", "raw_response", "candidate"):
        assert first[f"{artifact}_sha256"] != second[f"{artifact}_sha256"]
    assert_generation_provenance(second, task_generations / second["attempt_id"])
    candidate_directory = (
        results_root / "candidates" / "generated" / "mock-agent" / "one_shot"
    )
    assert [path.name for path in candidate_directory.iterdir()] == ["task_001.py"]
    assert (candidate_directory / "task_001.py").read_bytes() == b"value = 'second'\n"


@pytest.mark.parametrize("failing_agent", [InvalidSyntaxAgent(), FailingAgent()])
def test_failed_retry_preserves_successful_attempt_and_clears_latest_candidate(
    make_valid_task,
    workspace_tmp_path: Path,
    failing_agent,
):
    task_path = make_valid_task()
    solution_directory = workspace_tmp_path / "mock_solutions"
    solution_directory.mkdir()
    (solution_directory / "task_001.py").write_text(
        "value = 'café'\n", encoding="utf-8"
    )
    results_root = workspace_tmp_path / "results"
    arguments = {
        "agent_adapter": "mock",
        "task_path": task_path,
        "model": "mock-agent",
        "condition": "one_shot",
        "results_root": results_root,
    }
    first = generate_candidate(agent=MockAgent(solution_directory), **arguments)
    task_generations = (
        results_root / "generations" / "mock-agent" / "one_shot" / "task_001"
    )
    first_directory = task_generations / first["attempt_id"]
    original_evidence = {
        path.name: path.read_bytes() for path in first_directory.iterdir()
    }

    second = generate_candidate(agent=failing_agent, **arguments)
    failed_directory = task_generations / second["attempt_id"]
    assert first["attempt_id"] != second["attempt_id"]
    assert second["generation_status"] != "success"
    assert "candidate_sha256" not in second
    assert not (failed_directory / "extracted_solution.py").exists()
    assert not (
        results_root / "candidates" / "generated" / "mock-agent"
        / "one_shot" / "task_001.py"
    ).exists()
    assert {
        path.name: path.read_bytes() for path in first_directory.iterdir()
    } == original_evidence
    assert_generation_provenance(first, first_directory)
    assert_generation_provenance(second, failed_directory)
    assert json.loads(
        (failed_directory / "generation.json").read_text(encoding="utf-8")
    ) == second
    if isinstance(failing_agent, FailingAgent):
        assert second["error"] == "Provider unavailable"
        assert second["parse_status"] == "not_attempted"
        assert not (failed_directory / "raw_response.txt").exists()


def test_attempt_id_collision_does_not_overwrite_evidence(
    make_valid_task,
    workspace_tmp_path: Path,
    monkeypatch,
):
    from uuid import UUID

    monkeypatch.setattr(
        "runner.generate_candidates.uuid4", lambda: UUID(int=1)
    )
    arguments = {
        "agent": FailingAgent(),
        "agent_adapter": "failing",
        "task_path": make_valid_task(),
        "model": "test-agent",
        "condition": "one_shot",
        "results_root": workspace_tmp_path / "results",
    }
    first = generate_candidate(**arguments)
    generation_directory = (
        arguments["results_root"] / "generations" / "test-agent"
        / "one_shot" / "task_001" / first["attempt_id"]
    )
    original_evidence = {
        path.name: path.read_bytes() for path in generation_directory.iterdir()
    }
    with pytest.raises(FileExistsError):
        generate_candidate(**arguments)
    assert {
        path.name: path.read_bytes() for path in generation_directory.iterdir()
    } == original_evidence
