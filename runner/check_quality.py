"""Reproduce the corpus-size, reference-correctness, and defect-detection claims."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .evaluation import discover_tasks, load_metadata, run_solution_suites
    from .validation import validate_all_tasks
else:
    from evaluation import discover_tasks, load_metadata, run_solution_suites
    from validation import validate_all_tasks


def check_quality(root: Path, minimum_tasks: int = 32, minimum_tests: int = 200) -> dict:
    root = root.resolve()
    validation = validate_all_tasks(root / 'tasks')
    problems = []
    if not validation['benchmark_valid']:
        problems.append('Task integrity validation failed; see validation details.')
    tasks = discover_tasks(root / 'tasks')
    categories = defaultdict(lambda: {'tasks': 0, 'public_tests': 0, 'hidden_tests': 0})
    public_count = sum(t.get('reference_public_test_count') or 0 for t in validation['tasks'])
    hidden_count = sum(t.get('reference_hidden_test_count') or 0 for t in validation['tasks'])
    if len(tasks) < minimum_tasks:
        problems.append(f'Need at least {minimum_tasks} tasks; found {len(tasks)}.')
    if public_count + hidden_count < minimum_tests:
        problems.append(f'Need at least {minimum_tests} executed reference tests; found {public_count + hidden_count}.')
    baselines = []
    corpus_hash = hashlib.sha256()
    results_by_folder = {r['task_folder']: r for r in validation['tasks']}
    for task in tasks:
        metadata = load_metadata(task)
        task_id = metadata['task_id']
        row = categories[metadata['category']]
        row['tasks'] += 1
        validated = results_by_folder[task.name]
        for suite in ('public', 'hidden'):
            row[f'{suite}_tests'] += validated.get(f'reference_{suite}_test_count') or 0
        for source in sorted(task.iterdir()):
            if source.is_file() and source.name in {'prompt.md', 'metadata.json', 'starter.py', 'reference_solution.py', 'test_public.py', 'test_hidden.py'}:
                corpus_hash.update(source.relative_to(root).as_posix().encode() + b'\0')
                corpus_hash.update(hashlib.sha256(source.read_bytes()).digest())
        candidate_reference = root / 'results' / 'candidates' / 'reference' / f'{task_id}.py'
        if not candidate_reference.is_file() or candidate_reference.read_bytes() != (task / 'reference_solution.py').read_bytes():
            problems.append(f'{task_id}: reference candidate is missing or differs from task reference.')
        flawed = sorted((root / 'results' / 'baselines' / task_id).glob('*.py'))
        flawed = [path for path in flawed if path.name != 'reference_solution.py']
        if not flawed:
            problems.append(f'{task_id}: no deliberate defect fixture.')
        for path in flawed:
            with tempfile.TemporaryDirectory(prefix='agent-trial-audit-') as directory:
                public, hidden = run_solution_suites(task, path.read_bytes(), Path(directory))
            # A syntax/collection/timeout failure is not evidence that a behavioral test caught the intended bug.
            detected = hidden['status'] == 'failed' and hidden['failures'] > 0 and hidden['errors'] == 0
            baselines.append({
                'task_id': task_id,
                'candidate': path.relative_to(root).as_posix(),
                'candidate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'public_passed': public['passed'],
                'hidden_status': hidden['status'],
                'hidden_failed_tests': hidden['failed_tests'],
                'detected': detected,
            })
            if not detected:
                problems.append(f'{task_id}/{path.name}: hidden tests did not demonstrate behavioral defect detection.')
    return {
        'project': 'Agent Trial Lab',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(),
        'platform': platform.platform(),
        'pytest': importlib.metadata.version('pytest'),
        'corpus_sha256': corpus_hash.hexdigest(),
        'quality_passed': not problems,
        'thresholds': {'minimum_tasks': minimum_tasks, 'minimum_tests': minimum_tests},
        'task_count': len(tasks),
        'public_test_count': public_count,
        'hidden_test_count': hidden_count,
        'total_test_count': public_count + hidden_count,
        'categories': dict(sorted(categories.items())),
        'reference_tasks_passed': sum(t['reference_public_passed'] is True and t['reference_hidden_passed'] is True for t in validation['tasks']),
        'starter_tasks_rejected': sum(t['starter_overall_passed'] is False for t in validation['tasks']),
        'defect_fixture_count': len(baselines),
        'defect_fixtures_detected': sum(b['detected'] for b in baselines),
        'problems': problems,
        'validation': validation,
        'defect_fixtures': baselines,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--report-path', type=Path, default=Path('work/quality.json'))
    parser.add_argument('--minimum-tasks', type=int, default=32)
    parser.add_argument('--minimum-tests', type=int, default=200)
    args = parser.parse_args()
    report = check_quality(args.root, args.minimum_tasks, args.minimum_tests)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"Agent Trial Lab: {report['task_count']} tasks; {report['public_test_count']} public + {report['hidden_test_count']} hidden = {report['total_test_count']} tests")
    print(f"References passing: {report['reference_tasks_passed']}/{report['task_count']}")
    print(f"Deliberate defects detected: {report['defect_fixtures_detected']}/{report['defect_fixture_count']}")
    for problem in report['problems']:
        print(f'ERROR: {problem}')
    print(f'Report: {args.report_path}')
    if not report['quality_passed']:
        sys.exit(1)


if __name__ == '__main__':
    main()
