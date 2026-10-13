"""Regression coverage for scoring evidence and independent execution."""

import hashlib
import json
from pathlib import Path

import pytest

from runner.evaluation import evaluate_candidate, positive_timeout


def evaluate(task: Path, source: str, timeout: float = 10.0):
    candidate = task.parent / "candidate.py"
    candidate.write_text(source, encoding="utf-8")
    return evaluate_candidate(
        task, candidate, "test-model", "integrity",
        task.parent / "results", timeout_seconds=timeout,
    )


@pytest.mark.parametrize("source", [
    "from reference_solution import *\n",
    "import os\nos._exit(0)\n",
    "def solve(:\n",
])
def test_import_leak_early_exit_and_syntax_error_cannot_pass(make_valid_task, source):
    result = evaluate(make_valid_task(), source)
    assert not result["public_passed"]
    assert not result["hidden_passed"]
    assert not result["overall_passed"]
    assert result["public_execution"]["status"] == "error"


def test_timeout_is_a_recorded_failure_and_hidden_suite_still_runs(make_valid_task):
    result = evaluate(make_valid_task(), "while True:\n    pass\n", timeout=0.5)
    assert not result["overall_passed"]
    assert result["timeout_seconds"] == 0.5
    for suite in ("public", "hidden"):
        execution = result[f"{suite}_execution"]
        assert execution["status"] == "timeout"
        assert execution["diagnostic"] == "Test suite exceeded 0.5 seconds."
    assert (Path(result["run_path"]) / "result.json").is_file()


def test_suites_have_fresh_candidates_and_no_other_grading_files(make_valid_task):
    source = (
        "from pathlib import Path\n"
        "assert not Path('reference_solution.py').exists()\n"
        "assert Path('test_public.py').exists() != Path('test_hidden.py').exists()\n"
        "if Path('test_public.py').exists():\n"
        "    Path('starter.py').write_text('def solve(value): return 1000\\n')\n"
        "def solve(value):\n"
        "    return value\n"
    )
    result = evaluate(make_valid_task(), source)
    assert result["overall_passed"]
    assert result["public_execution"]["tests"] == 1
    assert result["hidden_execution"]["tests"] == 1


def test_parent_pytest_environment_and_conftest_cannot_change_grading(
    make_valid_task, monkeypatch,
):
    task = make_valid_task()
    (task.parent / "conftest.py").write_text(
        "raise RuntimeError('parent conftest must not run')\n", encoding="utf-8",
    )
    monkeypatch.setenv("PYTEST_ADDOPTS", "--invalid-benchmark-option")
    monkeypatch.setenv("PYTEST_PLUGINS", "missing_benchmark_plugin")
    monkeypatch.setenv("PYTHONPATH", str(task))
    result = evaluate(task, "def solve(value):\n    return value\n")
    assert result["overall_passed"]


def test_skipped_tests_do_not_count_as_a_pass(make_valid_task):
    task = make_valid_task()
    (task / "test_public.py").write_text(
        "import pytest\n"
        "from starter import solve\n"
        "def test_skipped():\n"
        "    pytest.skip('not executed')\n", encoding="utf-8",
    )
    result = evaluate(task, "def solve(value):\n    return value\n")
    assert not result["overall_passed"]
    assert result["public_execution"]["skipped"] == 1
    assert result["public_execution"]["status"] == "failed"


def test_empty_suites_do_not_count_as_a_pass(make_valid_task):
    task = make_valid_task()
    (task / "test_public.py").write_text("from starter import solve\n", encoding="utf-8")
    result = evaluate(task, "def solve(value):\n    return value\n")
    assert not result["public_passed"]
    assert result["public_execution"]["tests"] == 0
    assert result["public_execution"]["status"] == "error"


def test_artifacts_match_executed_bytes_even_if_source_changes(make_valid_task):
    task = make_valid_task()
    candidate = task.parent / "candidate.py"
    source = (
        "from pathlib import Path\n"
        f"Path({str(candidate)!r}).write_text('changed after execution began\\n')\n"
        "def solve(value):\n"
        "    return value\n"
    )
    result = evaluate(task, source)
    run = Path(result["run_path"])
    assert result["overall_passed"]
    assert candidate.read_text() == "changed after execution began\n"
    assert (run / "candidate_snapshot.py").read_bytes() == source.encode()
    assert result["candidate_sha256"] == hashlib.sha256(source.encode()).hexdigest()
    for name, digest in result["task_file_sha256"].items():
        saved = (run / "task_snapshot" / name).read_bytes()
        assert hashlib.sha256(saved).hexdigest() == digest
    assert (run / "public_test_results.xml").is_file()
    assert (run / "hidden_test_results.xml").is_file()
    assert result["runtime"]["pytest"]
    assert json.loads((run / "result.json").read_text()) == result


def test_failure_names_are_taken_from_structured_results(make_valid_task):
    result = evaluate(make_valid_task(), "def solve(value):\n    return value + 1\n")
    assert result["failed_public_tests"] == ["test_public_identity"]
    assert result["failed_hidden_tests"] == ["test_hidden_identity"]
    assert result["public_execution"]["failures"] == 1
    assert result["public_execution"]["status"] == "failed"


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan"), "-inf"])
def test_execution_timeout_must_be_finite_and_positive(value):
    with pytest.raises(ValueError, match="finite positive"):
        positive_timeout(value)
