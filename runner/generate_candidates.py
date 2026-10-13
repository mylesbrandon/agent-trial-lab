from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.base import AgentResponse, CodingAgent
from agents.manual_agent import ManualAgent
from agents.mock_agent import MockAgent
from agents.prompt_builder import build_one_shot_prompt
from agents.response_parser import extract_python_source
from runner.evaluation import discover_tasks, load_metadata, slugify


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one-shot candidates without evaluating them."
    )
    parser.add_argument(
        "--agent",
        choices=("manual", "mock"),
        required=True,
        help="Agent adapter used to generate responses.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model name recorded for this generation.",
    )
    parser.add_argument(
        "--condition",
        choices=("one_shot",),
        default="one_shot",
        help="Generation condition.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=["all"],
        help="Task IDs to generate, or 'all'.",
    )
    parser.add_argument(
        "--tasks-directory",
        type=Path,
        default=Path("tasks"),
        help="Directory containing benchmark task folders.",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=Path("results"),
        help="Root directory for generation and candidate artifacts.",
    )
    parser.add_argument(
        "--mock-solutions",
        type=Path,
        help="Task-keyed solution directory required by the mock adapter.",
    )
    return parser.parse_args()


def select_tasks(
    tasks_directory: Path,
    requested_tasks: Sequence[str],
) -> list[Path]:
    """Resolve requested task IDs in benchmark order."""
    task_paths = discover_tasks(tasks_directory)
    tasks_by_id = {
        load_metadata(task_path)["task_id"]: task_path
        for task_path in task_paths
    }

    if requested_tasks == ["all"]:
        return task_paths

    if "all" in requested_tasks:
        raise ValueError(
            "'all' cannot be combined with individual task IDs."
        )

    unknown_tasks = sorted(set(requested_tasks) - tasks_by_id.keys())

    if unknown_tasks:
        raise ValueError(
            "Unknown task ID(s): " + ", ".join(unknown_tasks)
        )

    requested = set(requested_tasks)
    return [
        task_path
        for task_path in task_paths
        if load_metadata(task_path)["task_id"] in requested
    ]


def _call_agent(
    agent: CodingAgent,
    prompt: str,
    task_id: str,
) -> AgentResponse:
    if isinstance(agent, MockAgent):
        return agent.generate_for_task(task_id)

    return agent.generate(prompt)


def _write_generation_metadata(
    generation_directory: Path,
    metadata: dict[str, str],
) -> None:
    metadata["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    metadata_path = generation_directory / "generation.json"
    with metadata_path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(metadata, indent=2) + "\n")


def _write_evidence(path: Path, content: str) -> str:
    """Write exact UTF-8 bytes once and return their SHA-256 digest."""
    data = content.encode("utf-8")
    with path.open("xb") as output:
        output.write(data)
    return hashlib.sha256(data).hexdigest()


def generate_candidate(
    *,
    agent: CodingAgent,
    agent_adapter: str,
    task_path: Path,
    model: str,
    condition: str,
    results_root: Path,
) -> dict[str, str]:
    """Preserve a new attempt and refresh the task's clean candidate."""
    task_id = load_metadata(task_path)["task_id"]
    model_directory = slugify(model)
    condition_directory = slugify(condition)
    attempt_id = uuid4().hex
    started_at_utc = datetime.now(timezone.utc).isoformat()
    generation_directory = (
        results_root
        / "generations"
        / model_directory
        / condition_directory
        / task_id
        / attempt_id
    )
    candidate_directory = (
        results_root
        / "candidates"
        / "generated"
        / model_directory
        / condition_directory
    )
    # A collision must fail rather than risk altering an existing attempt.
    generation_directory.mkdir(parents=True, exist_ok=False)
    candidate_directory.mkdir(parents=True, exist_ok=True)

    request_path = generation_directory / "request.md"
    raw_response_path = generation_directory / "raw_response.txt"
    extracted_path = generation_directory / "extracted_solution.py"
    candidate_path = candidate_directory / f"{task_id}.py"

    prompt = build_one_shot_prompt(task_path)
    prompt_sha256 = _write_evidence(request_path, prompt)

    # The clean solution set represents the current attempt. A failed retry
    # must not silently evaluate an older candidate; its evidence stays intact.
    candidate_path.unlink(missing_ok=True)

    generation_metadata = {
        "attempt_id": attempt_id,
        "started_at_utc": started_at_utc,
        "task_id": task_id,
        "model": model,
        "condition": condition,
        "agent_adapter": agent_adapter,
        "prompt_file": request_path.name,
        "prompt_sha256": prompt_sha256,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "parse_status": "not_attempted",
        "generation_status": "failed",
    }

    try:
        response = _call_agent(agent, prompt, task_id)
    except Exception as exc:
        generation_metadata["error"] = str(exc)
        _write_generation_metadata(
            generation_directory,
            generation_metadata,
        )
        return generation_metadata

    generation_metadata["raw_response_sha256"] = _write_evidence(
        raw_response_path, response.text
    )
    generation_metadata["raw_response_file"] = raw_response_path.name
    generation_metadata["response_model"] = response.model
    generation_metadata["response_condition"] = response.condition
    generation_metadata["generation_status"] = "completed"

    try:
        source = extract_python_source(response.text)
    except ValueError as exc:
        generation_metadata["parse_status"] = "failed"
        generation_metadata["error"] = str(exc)
        _write_generation_metadata(
            generation_directory,
            generation_metadata,
        )
        return generation_metadata

    generation_metadata["candidate_sha256"] = _write_evidence(
        extracted_path, source
    )
    candidate_path.write_bytes(source.encode("utf-8"))
    generation_metadata.update(
        {
            "candidate_file": extracted_path.name,
            "parse_status": "success",
            "generation_status": "success",
        }
    )
    _write_generation_metadata(
        generation_directory,
        generation_metadata,
    )
    return generation_metadata


def generate_candidates(
    *,
    agent: CodingAgent,
    agent_adapter: str,
    task_paths: Sequence[Path],
    model: str,
    condition: str,
    results_root: Path,
) -> list[dict[str, str]]:
    """Generate each selected task, continuing after recoverable failures."""
    return [
        generate_candidate(
            agent=agent,
            agent_adapter=agent_adapter,
            task_path=task_path,
            model=model,
            condition=condition,
            results_root=results_root,
        )
        for task_path in task_paths
    ]


def _build_agent(args: argparse.Namespace) -> CodingAgent:
    if args.agent == "manual":
        return ManualAgent(model_name=args.model)

    if args.mock_solutions is None:
        raise ValueError(
            "--mock-solutions is required when --agent mock is used."
        )

    return MockAgent(args.mock_solutions)


def main() -> None:
    args = parse_arguments()

    try:
        task_paths = select_tasks(
            args.tasks_directory,
            args.tasks,
        )
        agent = _build_agent(args)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    if not task_paths:
        raise SystemExit(
            f"No benchmark tasks found in {args.tasks_directory}"
        )

    results = generate_candidates(
        agent=agent,
        agent_adapter=args.agent,
        task_paths=task_paths,
        model=args.model,
        condition=args.condition,
        results_root=args.results_root,
    )

    print("Agent Trial Lab Candidate Generation")
    print(f"Model: {args.model}")
    print(f"Condition: {args.condition}")
    print()

    for result in results:
        status = (
            "SUCCESS"
            if result["generation_status"] == "success"
            else "FAILED"
        )
        print(f"{result['task_id']}: {status}")
        print(f"  Attempt: {result['attempt_id']}")

        if "error" in result:
            print(f"  {result['error']}")

    successful = sum(
        result["generation_status"] == "success"
        for result in results
    )
    print()
    print(f"Candidates generated: {successful}/{len(results)}")

    if successful != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
