"""The portfolio counts must reflect executed cases and behavioral detections."""
from pathlib import Path

from runner.check_quality import check_quality


def prepare(root: Path, task: Path, baseline_source: str):
    candidate = root / 'results/candidates/reference/task_001.py'
    candidate.parent.mkdir(parents=True)
    candidate.write_bytes((task / 'reference_solution.py').read_bytes())
    baseline = root / 'results/baselines/task_001/flawed.py'
    baseline.parent.mkdir(parents=True)
    baseline.write_text(baseline_source)


def test_quality_report_counts_execution_and_detected_defect(make_valid_task):
    original = make_valid_task()
    root = original.parent
    (root / 'tasks').mkdir()
    task = original.rename(root / 'tasks' / original.name)
    prepare(root, task, 'def solve(value):\n    return value + 1\n')
    report = check_quality(root, minimum_tasks=1, minimum_tests=2)
    assert report['quality_passed']
    assert report['total_test_count'] == 2
    assert report['reference_tasks_passed'] == 1
    assert report['starter_tasks_rejected'] == 1
    assert report['defect_fixtures_detected'] == 1
    assert len(report['corpus_sha256']) == 64


def test_collection_failure_is_not_counted_as_behavioral_detection(make_valid_task):
    original = make_valid_task()
    root = original.parent
    (root / 'tasks').mkdir()
    task = original.rename(root / 'tasks' / original.name)
    prepare(root, task, 'def solve(:\n')
    report = check_quality(root, minimum_tasks=2, minimum_tests=3)
    assert not report['quality_passed']
    assert report['defect_fixtures_detected'] == 0
    assert len(report['problems']) == 3  # task threshold, test threshold, invalid fixture
