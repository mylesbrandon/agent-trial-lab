from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .evaluation import (
        DEFAULT_TIMEOUT_SECONDS,
        build_missing_result,
        discover_tasks,
        evaluate_candidate,
        load_metadata,
        positive_timeout,
        write_summary_files,
    )
else:
    from evaluation import (
        DEFAULT_TIMEOUT_SECONDS,
        build_missing_result,
        discover_tasks,
        evaluate_candidate,
        load_metadata,
        positive_timeout,
        write_summary_files,
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a solution set across all tasks."
    )

    parser.add_argument(
        "--solution-set",
        required=True,
        type=Path,
        help=(
            "Directory containing one candidate file per task, "
            "named task_001.py, task_002.py, and so on."
        ),
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Model or baseline name.",
    )

    parser.add_argument(
        "--condition",
        required=True,
        help="Evaluation condition, such as one_shot.",
    )

    parser.add_argument(
        "--tasks-directory",
        type=Path,
        default=Path("tasks"),
    )

    parser.add_argument(
        "--results-root",
        type=Path,
        default=Path("results"),
    )

    parser.add_argument(
        "--timeout-seconds", type=positive_timeout, default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum seconds per public or hidden suite (default: 10).",
    )
    return parser.parse_args()


def print_task_result(result: dict) -> None:
    print(f"{result['task_id']} — {result['task_name']}")

    if result["status"] == "missing_candidate":
        print("Status: MISSING CANDIDATE")
        print()
        return

    print(
        "Public:",
        "PASS" if result["public_passed"] else "FAIL",
    )
    print(
        "Hidden:",
        "PASS" if result["hidden_passed"] else "FAIL",
    )
    print(
        "Overall:",
        "PASS" if result["overall_passed"] else "FAIL",
    )
    print()


def main() -> None:
    args = parse_arguments()

    task_paths = discover_tasks(args.tasks_directory)

    if not task_paths:
        raise SystemExit(
            f"No benchmark tasks found in {args.tasks_directory}"
        )

    results: list[dict] = []

    print("Code Reliability Bench Evaluation")
    print(f"Model: {args.model}")
    print(f"Condition: {args.condition}")
    print()

    for task_path in task_paths:
        metadata = load_metadata(task_path)
        task_id = metadata["task_id"]

        candidate_path = args.solution_set / f"{task_id}.py"

        if not candidate_path.exists():
            result = build_missing_result(
                task_path=task_path,
                model=args.model,
                condition=args.condition,
                expected_candidate_path=candidate_path,
            )
        else:
            result = evaluate_candidate(
                task_path=task_path,
                solution_path=candidate_path,
                model=args.model,
                condition=args.condition,
                results_root=args.results_root,
                timeout_seconds=args.timeout_seconds,
            )

        results.append(result)
        print_task_result(result)

    summaries_directory = args.results_root / "summaries"

    csv_path, json_path, summary = write_summary_files(
        results=results,
        model=args.model,
        condition=args.condition,
        summaries_directory=summaries_directory,
    )

    print("Summary")
    print(
        f"Tasks attempted: "
        f"{summary['attempted_count']}/"
        f"{summary['task_count']}"
    )
    print(f"Missing candidates: {summary['missing_count']}")
    print(
        f"Public pass rate: "
        f"{summary['public_pass_rate']:.1%}"
    )
    print(
        f"Hidden pass rate: "
        f"{summary['hidden_pass_rate']:.1%}"
    )
    print(
        f"Overall pass rate: "
        f"{summary['overall_pass_rate']:.1%}"
    )
    print(
        f"Public-hidden gap: "
        f"{summary['public_hidden_gap']:.1%}"
    )
    print()
    print(f"CSV summary: {csv_path}")
    print(f"JSON summary: {json_path}")


if __name__ == "__main__":
    main()
