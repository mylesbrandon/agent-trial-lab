"""Validate the corpus and evaluate every task inside the Linux image."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

if __package__:
    from .check_quality import check_quality
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
    from check_quality import check_quality
    from evaluation import (
        DEFAULT_TIMEOUT_SECONDS,
        build_missing_result,
        discover_tasks,
        evaluate_candidate,
        load_metadata,
        positive_timeout,
        write_summary_files,
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    """Keep interrupted writes from replacing a complete earlier manifest."""
    temporary = path.with_name(f'.{path.name}.{uuid4().hex}.tmp')
    try:
        temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def run_workflow(
    root: Path,
    results_root: Path,
    solution_set: Path | None = None,
    model: str = 'reference',
    condition: str = 'docker',
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    validation_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    require_all_pass: bool = False,
    minimum_tasks: int = 32,
    minimum_tests: int = 200,
) -> dict[str, Any]:
    """Run the quality gate before scoring candidates and retain both reports.

    The shipped references always require a perfect score. Custom candidate
    failures are valid benchmark outcomes unless ``require_all_pass`` is set.
    The size thresholds are exposed for small integration fixtures; the CLI
    always enforces the published 32-task, 200-test minimums.
    """
    root = root.resolve()
    results_root = results_root.resolve()
    timeout_seconds = positive_timeout(timeout_seconds)
    validation_timeout_seconds = positive_timeout(validation_timeout_seconds)
    use_reference = solution_set is None
    solution_set = (root / 'results/candidates/reference' if use_reference else solution_set).resolve()
    require_all_pass = require_all_pass or use_reference
    results_root.mkdir(parents=True, exist_ok=True)
    manifest_path = results_root / 'workflow.json'
    started = time.monotonic()
    report: dict[str, Any] = {
        'schema_version': 1,
        'project': 'Code Reliability Bench',
        'workflow_id': uuid4().hex,
        'status': 'started',
        'phase': 'validation',
        'started_at_utc': _now(),
        'completed_at_utc': None,
        'runtime': {
            'python': platform.python_version(),
            'platform': platform.platform(),
            'pytest': importlib.metadata.version('pytest'),
        },
        'root': str(root),
        'solution_set': str(solution_set),
        'results_root': str(results_root),
        'model': model,
        'condition': condition,
        'timeout_seconds': timeout_seconds,
        'validation_timeout_seconds': validation_timeout_seconds,
        'reference_solution_set': use_reference,
        'require_all_pass': require_all_pass,
        'quality_report': 'quality.json',
        'summary': None,
        'exit_code': None,
    }
    _write_json(manifest_path, report)

    def finish(status: str, exit_code: int) -> dict[str, Any]:
        report.update(status=status, exit_code=exit_code, completed_at_utc=_now(),
                      duration_seconds=round(time.monotonic() - started, 6))
        _write_json(manifest_path, report)
        print(f"Workflow: {status}; report: {manifest_path}", flush=True)
        return report

    try:
        print('Validating references, starters, and deliberate defect fixtures...', flush=True)
        quality = check_quality(root, minimum_tasks=minimum_tasks, minimum_tests=minimum_tests,
                                timeout_seconds=validation_timeout_seconds)
        _write_json(results_root / 'quality.json', quality)
        report['corpus_sha256'] = quality['corpus_sha256']
        if not quality['quality_passed']:
            report['problems'] = quality['problems']
            return finish('validation_failed', 1)

        if not solution_set.is_dir():
            raise ValueError(f'Solution set is not a directory: {solution_set}')
        report['phase'] = 'evaluation'
        _write_json(manifest_path, report)
        evaluation_root = results_root / 'evaluation'
        results = []
        for task_path in discover_tasks(root / 'tasks'):
            task_id = load_metadata(task_path)['task_id']
            candidate = solution_set / f'{task_id}.py'
            if candidate.exists():
                result = evaluate_candidate(task_path, candidate, model, condition,
                                            evaluation_root, timeout_seconds=timeout_seconds)
            else:
                result = build_missing_result(task_path, model, condition, candidate)
            results.append(result)
            outcome = 'PASS' if result['overall_passed'] else result['status'].upper()
            if outcome == 'ATTEMPTED':
                outcome = 'FAIL'
            print(f'{task_id}: {outcome}', flush=True)

        csv_path, json_path, summary = write_summary_files(
            results, model, condition, evaluation_root / 'summaries',
        )
        report['summary'] = summary
        report['summary_csv'] = csv_path.relative_to(results_root).as_posix()
        report['summary_json'] = json_path.relative_to(results_root).as_posix()
        report['phase'] = 'complete'
        if require_all_pass and summary['overall_pass_count'] != summary['task_count']:
            return finish('evaluation_failed', 1)
        return finish('completed', 0)
    except Exception as error:
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
        return finish('error', 2)


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--solution-set', type=Path,
                        help='Candidate directory; defaults to the validated reference set.')
    parser.add_argument('--results-root', required=True, type=Path)
    parser.add_argument('--model', default='reference')
    parser.add_argument('--condition', default='docker')
    parser.add_argument('--timeout-seconds', type=positive_timeout, default=DEFAULT_TIMEOUT_SECONDS,
                        help='Maximum seconds per candidate public or hidden suite (default: 10).')
    parser.add_argument('--validation-timeout-seconds', type=positive_timeout,
                        default=DEFAULT_TIMEOUT_SECONDS,
                        help='Maximum seconds per reference, starter, or defect-fixture suite (default: 10).')
    parser.add_argument('--require-all-pass', action='store_true',
                        help='Exit nonzero for any missing or failing candidate; always enabled for default references.')
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    report = run_workflow(**vars(args))
    if report.get('error'):
        print(f"ERROR: {report['error']['message']}", file=sys.stderr)
    return report['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
