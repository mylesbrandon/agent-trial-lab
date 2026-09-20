"""Check the manually reviewed Pilot 001 labels against frozen evidence."""

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "results" / "experiments" / "pilot_001"
EXPECTED_CATEGORIES = {
    "passed",
    "syntax_error",
    "runtime_error",
    "spec_misunderstanding",
    "algorithmic_error",
    "edge_case_failure",
    "numerical_error",
    "data_validation_failure",
    "state_or_timing_error",
    "incomplete_solution",
    "evaluation_infrastructure_error",
}
ACTIONS = {
    "keep": "keep task unchanged",
    "clarify_prompt": "clarify prompt",
    "improve_test": "improve test",
    "fix_evaluator": "fix evaluator",
}
TASK_IDS = ["task_001", "task_002", "task_003", "task_004"]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def classifications():
    return read_json(PILOT / "classifications.json")


@pytest.fixture(params=TASK_IDS)
def record(request, classifications):
    matches = [
        item for item in classifications["classifications"]
        if item["task_id"] == request.param
    ]
    assert len(matches) == 1
    return matches[0]


def test_every_frozen_task_has_exactly_one_classification(classifications):
    manifest = read_json(PILOT / "manifest.json")
    assert classifications["experiment_id"] == manifest["experiment_id"]
    assert manifest["task_ids"] == TASK_IDS
    assert Counter(
        item["task_id"] for item in classifications["classifications"]
    ) == Counter(manifest["task_ids"])


def test_classification_schema_and_taxonomy(record):
    taxonomy = (ROOT / "docs" / "failure_taxonomy.md").read_text(
        encoding="utf-8"
    )
    categories = set(re.findall(r"^## ([a-z_]+)$", taxonomy, re.MULTILINE))
    assert categories == EXPECTED_CATEGORIES
    assert set(record) == {
        "task_id", "overall_passed", "primary_failure", "secondary_failures",
        "failed_tests", "evidence", "confidence", "task_action",
    }
    assert type(record["overall_passed"]) is bool
    assert record["primary_failure"] in categories
    assert isinstance(record["secondary_failures"], list)
    assert all(label in categories for label in record["secondary_failures"])
    assert len(record["secondary_failures"]) == len(set(record["secondary_failures"]))
    assert record["primary_failure"] not in record["secondary_failures"]
    assert "passed" not in record["secondary_failures"]
    assert record["confidence"] in {"high", "medium", "low"}
    assert record["task_action"] in ACTIONS
    assert isinstance(record["evidence"], str)
    assert isinstance(record["failed_tests"], list)
    assert all(isinstance(name, str) and name for name in record["failed_tests"])
    assert len(record["failed_tests"]) == len(set(record["failed_tests"]))

    assert (record["primary_failure"] == "passed") == record["overall_passed"]
    if record["overall_passed"]:
        assert record["secondary_failures"] == []
        assert record["failed_tests"] == []
    else:
        assert record["evidence"].strip()


def test_outcome_and_failure_names_match_evaluation_artifacts(record):
    evaluation = PILOT / "evaluation" / record["task_id"]
    result = read_json(evaluation / "result.json")
    assert record["overall_passed"] is result["overall_passed"]
    assert result["overall_passed"] == (
        result["public_passed"] and result["hidden_passed"]
    )

    recorded_names = set()
    for suite in ("public", "hidden"):
        output = (evaluation / f"{suite}_test_output.txt").read_text(
            encoding="utf-8"
        )
        # Module-level collection ERROR entries are not test-function failures.
        names_in_log = set(re.findall(
            r"^FAILED\s+\S+?::(\S+)", output, re.MULTILINE
        ))
        assert names_in_log == set(result[f"failed_{suite}_tests"])
        recorded_names.update(names_in_log)

    # Equality also catches omissions, not only fabricated failed test names.
    assert set(record["failed_tests"]) == recorded_names


def test_syntax_classification_has_reproducible_collection_evidence(record):
    task_id = record["task_id"]
    candidate = PILOT / "candidates" / f"{task_id}.py"
    generation = PILOT / "generations" / task_id
    evaluation = PILOT / "evaluation" / task_id
    metadata = read_json(generation / "generation.json")
    result = read_json(evaluation / "result.json")

    # Compile only: do not repair, import, execute, or regenerate candidates.
    with pytest.raises(SyntaxError) as failure:
        compile(candidate.read_text(encoding="utf-8"), str(candidate), "exec")

    error = failure.value
    assert record["primary_failure"] == "syntax_error"
    assert record["secondary_failures"] == ["incomplete_solution"]
    assert record["failed_tests"] == []
    assert f"candidates/{task_id}.py:{error.lineno}" in record["evidence"]
    assert metadata["parse_status"] == "failed"
    assert error.msg in metadata["error"]
    for suite in ("public", "hidden"):
        relative_log = f"evaluation/{task_id}/{suite}_test_output.txt"
        output = (PILOT / relative_log).read_text(encoding="utf-8")
        assert relative_log in record["evidence"]
        assert result[f"{suite}_passed"] is False
        assert result[f"{suite}_returncode"] == 2
        assert f"SyntaxError: {error.msg}" in output
        assert f"line {error.lineno}" in output
        assert f"ERROR test_{suite}.py" in output
        assert "1 error during collection" in output

    # The attribution caveat is supported by the captured raw text too.
    with pytest.raises(IndentationError):
        compile(
            (generation / "raw_response.txt").read_text(encoding="utf-8"),
            "<preserved raw response>",
            "exec",
        )


def test_classification_uses_unchanged_preserved_artifacts(record):
    task_id = record["task_id"]
    generation = PILOT / "generations" / task_id
    metadata = read_json(generation / "generation.json")
    for filename, hash_field in (
        ("request.md", "prompt_sha256"),
        ("raw_response.txt", "raw_response_sha256"),
        ("extracted_solution.py", "candidate_sha256"),
    ):
        # Generation hashes normalize line endings by hashing decoded text.
        text = (generation / filename).read_text(encoding="utf-8")
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == metadata[hash_field]

    candidate = (PILOT / "candidates" / f"{task_id}.py").read_bytes()
    assert candidate == (generation / "extracted_solution.py").read_bytes()
    assert candidate == (
        PILOT / "evaluation" / task_id / "candidate_snapshot.py"
    ).read_bytes()
    assert metadata["regenerated"] is False


def test_every_task_has_consistent_analysis(record):
    analysis = (PILOT / "analysis" / f"{record['task_id']}.md").read_text(
        encoding="utf-8"
    )
    for heading in (
        "Result", "Candidate approach", "Failed tests", "Root cause",
        "Primary classification", "Secondary classification", "Public-hidden gap",
        "Benchmark quality", "Action",
    ):
        assert f"## {heading}\n" in analysis
    assert f"## Primary classification\n\n`{record['primary_failure']}`" in analysis
    for label in record["secondary_failures"]:
        assert f"`{label}`" in analysis
    assert f"## Action\n\n- {ACTIONS[record['task_action']]}" in analysis


def test_failure_summary_matches_classifications_and_results(classifications):
    with (PILOT / "failure_summary.csv").open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == [
            "task_id", "task_name", "category", "public_passed", "hidden_passed",
            "overall_passed", "primary_failure", "secondary_failures",
            "failed_test_count", "confidence", "task_action",
        ]
        rows = list(reader)

    assert Counter(row["task_id"] for row in rows) == Counter(TASK_IDS)
    by_task = {item["task_id"]: item for item in classifications["classifications"]}
    for row in rows:
        item = by_task[row["task_id"]]
        result = read_json(PILOT / "evaluation" / row["task_id"] / "result.json")
        for field in ("task_name", "category"):
            assert row[field] == result[field]
        for field in ("public_passed", "hidden_passed", "overall_passed"):
            assert row[field] == str(result[field]).lower()
        for field in ("primary_failure", "confidence", "task_action"):
            assert row[field] == item[field]
        assert row["secondary_failures"] == ";".join(item["secondary_failures"])
        assert row["failed_test_count"] == str(len(item["failed_tests"]))


def test_overall_analysis_distribution_matches_primary_labels(classifications):
    labels = {
        "passed": "Passed", "syntax_error": "Syntax error",
        "runtime_error": "Runtime error",
        "spec_misunderstanding": "Specification misunderstanding",
        "algorithmic_error": "Algorithmic error", "edge_case_failure": "Edge-case failure",
        "numerical_error": "Numerical error", "data_validation_failure": "Data-validation failure",
        "state_or_timing_error": "State/timing error", "incomplete_solution": "Incomplete solution",
        "evaluation_infrastructure_error": "Evaluation infrastructure error",
    }
    analysis = (PILOT / "analysis.md").read_text(encoding="utf-8")
    distribution = analysis.split("## Failure distribution\n", 1)[1].split("\n## ", 1)[0]
    counts = Counter(item["primary_failure"] for item in classifications["classifications"])
    for category, label in labels.items():
        assert f"| {label} | {counts[category]} |" in distribution
