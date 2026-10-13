"""The container pipeline must validate first and preserve useful failure evidence."""
import importlib
import json
import tempfile
from pathlib import Path

import pytest

from runner import container_workflow, validation


@pytest.fixture
def corpus(make_valid_task):
    original = make_valid_task()
    root = original.parent
    (root / 'tasks').mkdir()
    task = original.rename(root / 'tasks' / original.name)
    reference = root / 'results/candidates/reference/task_001.py'
    reference.parent.mkdir(parents=True)
    reference.write_bytes((task / 'reference_solution.py').read_bytes())
    defect = root / 'results/baselines/task_001/flawed.py'
    defect.parent.mkdir(parents=True)
    defect.write_bytes((task / 'starter.py').read_bytes())
    return root, task


def successful_quality(**_):
    return {'quality_passed': True, 'corpus_sha256': 'a' * 64, 'problems': []}


def test_complete_workflow_validates_and_evaluates_reference(corpus, monkeypatch):
    root, _ = corpus
    quality_module = importlib.import_module('runner.check_quality')
    suite_calls = []
    original_runner = validation.run_solution_suites

    def capture(task, source, parent, timeout_seconds):
        suite_calls.append((parent.resolve(), timeout_seconds))
        return original_runner(task, source, parent, timeout_seconds)

    monkeypatch.setattr(validation, 'run_solution_suites', capture)
    monkeypatch.setattr(quality_module, 'run_solution_suites', capture)
    report = container_workflow.run_workflow(
        root, root / 'output', timeout_seconds=7, validation_timeout_seconds=9,
        minimum_tasks=1, minimum_tests=2,
    )
    assert report['status'] == 'completed'
    assert report['exit_code'] == 0
    assert report['require_all_pass'] is True
    assert report['summary']['overall_pass_count'] == 1
    assert report['summary']['missing_count'] == 0
    assert suite_calls == [(Path(tempfile.gettempdir()).resolve(), 9)] * 3
    quality = json.loads((root / 'output/quality.json').read_text())
    assert quality['reference_tasks_passed'] == 1
    assert quality['defect_fixtures_detected'] == 1
    assert quality['total_test_count'] == 2
    assert quality['timeout_seconds'] == 9
    manifest = json.loads((root / 'output/workflow.json').read_text())
    assert manifest == report
    assert manifest['completed_at_utc'] >= manifest['started_at_utc']
    assert (root / 'output' / report['summary_csv']).is_file()
    result_path, = (root / 'output/evaluation/runs').rglob('result.json')
    result = json.loads(result_path.read_text())
    assert result['timeout_seconds'] == 7
    assert result['public_execution']['status'] == 'passed'
    assert result['hidden_execution']['status'] == 'passed'


def test_failed_validation_never_executes_candidate(corpus, monkeypatch):
    root, _ = corpus

    def forbidden_execution(*args, **kwargs):
        raise AssertionError('Candidate must not execute after a failed quality gate')

    monkeypatch.setattr(container_workflow, 'evaluate_candidate', forbidden_execution)
    report = container_workflow.run_workflow(root, root / 'output',
                                           minimum_tasks=2, minimum_tests=2)
    assert report['status'] == 'validation_failed'
    assert report['exit_code'] == 1
    assert report['summary'] is None
    assert not (root / 'output/evaluation').exists()
    assert json.loads((root / 'output/quality.json').read_text())['quality_passed'] is False


@pytest.mark.parametrize('missing', [False, True])
@pytest.mark.parametrize('strict', [False, True])
def test_candidate_failures_are_scored_unless_all_pass_required(corpus, monkeypatch, missing, strict):
    root, task = corpus
    candidates = root / 'candidates'
    candidates.mkdir()
    if not missing:
        (candidates / 'task_001.py').write_bytes((task / 'starter.py').read_bytes())
    monkeypatch.setattr(container_workflow, 'check_quality', lambda *a, **kw: successful_quality())
    report = container_workflow.run_workflow(root, root / 'output', candidates,
                                           model='example', require_all_pass=strict)
    assert report['status'] == ('evaluation_failed' if strict else 'completed')
    assert report['exit_code'] == (1 if strict else 0)
    assert report['summary']['overall_pass_count'] == 0
    assert report['summary']['missing_count'] == int(missing)
    assert report['summary']['task_count'] == 1


def test_default_reference_always_requires_all_pass(corpus, monkeypatch):
    root, _ = corpus
    monkeypatch.setattr(container_workflow, 'check_quality', lambda *a, **kw: successful_quality())
    (root / 'results/candidates/reference/task_001.py').unlink()
    report = container_workflow.run_workflow(root, root / 'output', require_all_pass=False)
    assert report['require_all_pass'] is True
    assert report['status'] == 'evaluation_failed'
    assert report['exit_code'] == 1


def test_candidate_timeout_is_recorded_with_independent_validation_budget(corpus):
    root, _ = corpus
    candidates = root / 'candidates'
    candidates.mkdir()
    (candidates / 'task_001.py').write_text('while True:\n    pass\n', encoding='utf-8')
    report = container_workflow.run_workflow(
        root, root / 'output', candidates, timeout_seconds=0.5,
        validation_timeout_seconds=10, minimum_tasks=1, minimum_tests=2,
    )
    assert report['status'] == 'completed'
    assert report['summary']['overall_pass_count'] == 0
    quality = json.loads((root / 'output/quality.json').read_text())
    assert quality['quality_passed'] is True
    result_path, = (root / 'output/evaluation/runs').rglob('result.json')
    result = json.loads(result_path.read_text())
    assert result['public_execution']['status'] == 'timeout'
    assert result['hidden_execution']['status'] == 'timeout'


def test_workflow_errors_leave_a_failure_manifest(corpus, monkeypatch):
    root, _ = corpus
    monkeypatch.setattr(container_workflow, 'check_quality', lambda *a, **kw: successful_quality())
    report = container_workflow.run_workflow(root, root / 'output', root / 'nonexistent')
    assert report['status'] == 'error'
    assert report['exit_code'] == 2
    assert report['error']['type'] == 'ValueError'
    assert json.loads((root / 'output/workflow.json').read_text()) == report


@pytest.mark.parametrize('flag', ['--timeout-seconds', '--validation-timeout-seconds'])
@pytest.mark.parametrize('value', ['0', '-1', 'nan', 'inf'])
def test_cli_rejects_invalid_timeouts(flag, value):
    with pytest.raises(SystemExit) as error:
        container_workflow.parse_arguments(['--results-root', '/output', flag, value])
    assert error.value.code == 2


def test_cli_cannot_disable_published_quality_thresholds():
    with pytest.raises(SystemExit) as error:
        container_workflow.parse_arguments(['--results-root', '/output', '--minimum-tasks', '1'])
    assert error.value.code == 2
