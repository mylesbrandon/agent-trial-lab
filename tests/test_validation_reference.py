from runner.validation import validate_task


def test_failing_reference_invalidates_task(make_valid_task):
    task_path = make_valid_task()
    (task_path / "reference_solution.py").write_text(
        "def solve(value):\n    return value + 1\n",
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert result["valid"] is False
    assert any(
        "reference_solution.py failed hidden tests" in error
        for error in result["errors"]
    )


def test_starter_that_passes_everything_is_error(make_valid_task):
    task_path = make_valid_task()
    reference = (task_path / "reference_solution.py").read_text(
        encoding="utf-8"
    )
    (task_path / "starter.py").write_text(
        reference,
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "starter.py passes all tests; task requires no repair"
        in result["errors"]
    )


def test_public_tests_cannot_import_reference_solution(
    make_valid_task,
):
    task_path = make_valid_task()
    (task_path / "test_public.py").write_text(
        "from reference_solution import solve\n\n"
        "def test_public_identity():\n"
        "    assert solve(1) == 1\n",
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "test_public.py imports reference_solution instead of starter"
        in result["errors"]
    )


def test_hidden_tests_cannot_import_reference_solution(
    make_valid_task,
):
    task_path = make_valid_task()
    (task_path / "test_hidden.py").write_text(
        "from reference_solution import solve\n\n"
        "def test_hidden_identity():\n"
        "    assert solve(-1) == -1\n",
        encoding="utf-8",
    )

    result = validate_task(task_path)

    assert (
        "test_hidden.py imports reference_solution instead of starter"
        in result["errors"]
    )
