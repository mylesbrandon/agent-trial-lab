from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__:
    from .validation import validate_all_tasks
else:
    from validation import validate_all_tasks


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate benchmark task integrity."
    )
    parser.add_argument(
        "--tasks-directory",
        type=Path,
        default=Path("tasks"),
        help="Directory containing benchmark task folders.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path(
            "results/validation/benchmark_validation.json"
        ),
        help="Path for the machine-readable validation report.",
    )
    return parser.parse_args()


def write_report(report: dict, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


def print_report(report: dict) -> None:
    print("Validating CodeAgentBench-Lite...")
    print()

    for error in report["global_errors"]:
        print(f"ERROR: {error}")

    if report["global_errors"]:
        print()

    for task in report["tasks"]:
        status = "PASS" if task["valid"] else "FAIL"
        print(f"{task['task_folder']}: {status}")

        for error in task["errors"]:
            print(f"  ERROR: {error}")

        for warning in task["warnings"]:
            print(f"  WARNING: {warning}")

    print()
    print(f"Tasks validated: {report['task_count']}")
    print(f"Errors: {report['error_count']}")
    print(f"Warnings: {report['warning_count']}")
    print(
        "Benchmark status:",
        "VALID" if report["benchmark_valid"] else "INVALID",
    )


def main() -> None:
    args = parse_arguments()
    report = validate_all_tasks(args.tasks_directory)
    write_report(report, args.report_path)
    print_report(report)

    if not report["benchmark_valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
