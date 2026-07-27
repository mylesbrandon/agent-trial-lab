import json

from runner.validation import validate_task


def test_metadata_test_count_mismatch_is_error(
    make_valid_task,
):
    task_path = make_valid_task()
    metadata_path = task_path / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["public_tests"] = 2
    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "metadata public_tests says 2, but 1 tests were discovered"
        in result["errors"]
    )


def test_both_test_suites_must_contain_tests(make_valid_task):
    task_path = make_valid_task()
    (task_path / "test_hidden.py").write_text(
        "from starter import solve\n",
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "test_hidden.py must contain at least one test"
        in result["errors"]
    )


def test_identical_test_suites_are_error(make_valid_task):
    task_path = make_valid_task()
    public_source = (task_path / "test_public.py").read_text(
        encoding="utf-8"
    )
    (task_path / "test_hidden.py").write_text(
        public_source,
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "test_public.py and test_hidden.py are identical"
        in result["errors"]
    )
