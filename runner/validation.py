from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

if __package__:
    from .evaluation import (
        discover_tasks,
        run_pytest,
        workspace_temporary_directory,
    )
else:
    from evaluation import (
        discover_tasks,
        run_pytest,
        workspace_temporary_directory,
    )


REQUIRED_FILES = (
    "prompt.md",
    "starter.py",
    "reference_solution.py",
    "test_public.py",
    "test_hidden.py",
    "metadata.json",
)

REQUIRED_METADATA_FIELDS = (
    "task_id",
    "name",
    "category",
    "difficulty",
    "concepts",
    "public_tests",
    "hidden_tests",
    "failure_modes_targeted",
    "contract_keywords",
)

TASK_ID_PATTERN = re.compile(r"^task_\d{3}$")
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_task_structure(task_path: Path) -> list[str]:
    """Return errors for required task files that are absent."""
    return [
        f"Missing required file: {filename}"
        for filename in REQUIRED_FILES
        if not (task_path / filename).is_file()
    ]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(
    metadata: dict[str, Any],
    field: str,
    errors: list[str],
) -> None:
    value = metadata.get(field)

    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a nonempty list of strings")
        return

    if any(not _is_nonempty_string(item) for item in value):
        errors.append(f"{field} must contain only nonempty strings")


def validate_metadata(
    task_path: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Parse and validate one task's metadata schema."""
    metadata_path = task_path / "metadata.json"

    if not metadata_path.is_file():
        return None, []

    try:
        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, [f"metadata.json could not be parsed: {error}"]

    if not isinstance(metadata, dict):
        return None, ["metadata.json must contain a JSON object"]

    errors: list[str] = []

    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required metadata field: {field}")

    task_id = metadata.get("task_id")

    if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(
        task_id
    ):
        errors.append('task_id must be a string matching "task_###"')
    elif not task_path.name.startswith(task_id):
        errors.append(
            f'folder name must start with task_id "{task_id}"'
        )

    for field in ("name", "category"):
        if not _is_nonempty_string(metadata.get(field)):
            errors.append(f"{field} must be a nonempty string")

    difficulty = metadata.get("difficulty")

    if difficulty not in VALID_DIFFICULTIES:
        errors.append(
            "difficulty must be easy, medium, or hard; "
            f"received {json.dumps(difficulty)}"
        )

    _validate_string_list(metadata, "concepts", errors)
    _validate_string_list(
        metadata,
        "failure_modes_targeted",
        errors,
    )
    _validate_string_list(metadata, "contract_keywords", errors)

    for field in ("public_tests", "hidden_tests"):
        value = metadata.get(field)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            errors.append(
                f"{field} must be a nonnegative integer"
            )

    return metadata, errors


def _parse_python(path: Path) -> ast.AST:
    return ast.parse(
        path.read_text(encoding="utf-8"),
        filename=str(path),
    )


def _test_function_names(tree: ast.AST) -> list[str]:
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def count_pytest_tests(test_file: Path) -> int:
    """Count pytest-style test functions using Python's AST."""
    return len(_test_function_names(_parse_python(test_file)))


def count_test_functions(test_file: Path) -> int:
    """Backward-friendly alias for the explicit pytest counter."""
    return count_pytest_tests(test_file)


def _imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
                modules.update(
                    f"{node.module}.{alias.name}"
                    for alias in node.names
                )
            else:
                modules.update(alias.name for alias in node.names)

    return modules


def _imports_module(modules: set[str], target: str) -> bool:
    return any(target in module.split(".") for module in modules)


def validate_test_suites(
    task_path: Path,
    metadata: dict[str, Any] | None,
) -> tuple[int | None, int | None, list[str]]:
    """Validate test counts, uniqueness, imports, and separation."""
    errors: list[str] = []
    counts: dict[str, int | None] = {
        "public": None,
        "hidden": None,
    }
    trees: dict[str, ast.AST] = {}

    for suite in ("public", "hidden"):
        path = task_path / f"test_{suite}.py"

        if not path.is_file():
            continue

        try:
            tree = _parse_python(path)
        except (OSError, UnicodeError, SyntaxError) as error:
            errors.append(
                f"test_{suite}.py could not be parsed: {error}"
            )
            continue

        trees[suite] = tree
        names = _test_function_names(tree)
        counts[suite] = len(names)

        if not names:
            errors.append(
                f"test_{suite}.py must contain at least one test"
            )

        duplicates = sorted(
            name
            for name, count in Counter(names).items()
            if count > 1
        )

        for name in duplicates:
            errors.append(
                f"test_{suite}.py defines duplicate test name: {name}"
            )

        if metadata is not None:
            field = f"{suite}_tests"
            declared = metadata.get(field)

            if (
                isinstance(declared, int)
                and not isinstance(declared, bool)
                and declared >= 0
                and declared != len(names)
            ):
                errors.append(
                    f"metadata {field} says {declared}, but "
                    f"{len(names)} tests were discovered"
                )

    public_path = task_path / "test_public.py"
    hidden_path = task_path / "test_hidden.py"

    if public_path.is_file() and hidden_path.is_file():
        try:
            if public_path.read_bytes() == hidden_path.read_bytes():
                errors.append(
                    "test_public.py and test_hidden.py are identical"
                )
        except OSError as error:
            errors.append(f"test files could not be compared: {error}")

    for suite, tree in trees.items():
        modules = _imported_modules(tree)
        filename = f"test_{suite}.py"

        if not _imports_module(modules, "starter"):
            errors.append(f"{filename} must import starter")

        if _imports_module(modules, "reference_solution"):
            errors.append(
                f"{filename} imports reference_solution instead of "
                "starter"
            )

        if suite == "public" and _imports_module(
            modules,
            "test_hidden",
        ):
            errors.append("test_public.py imports hidden tests")

    return counts["public"], counts["hidden"], errors


def _directory_snapshot(directory: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}

    for path in sorted(
        (item for item in directory.rglob("*") if item.is_file()),
        key=lambda item: item.as_posix(),
    ):
        relative_path = path.relative_to(directory).as_posix()
        snapshot[relative_path] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    return snapshot


def _run_solution(
    task_path: Path,
    solution_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    with workspace_temporary_directory(
        Path.cwd(),
        ".codeagentbench_validation_",
    ) as temporary_directory:
        temporary_task = temporary_directory / task_path.name
        shutil.copytree(task_path, temporary_task)
        shutil.copy2(
            solution_path,
            temporary_task / "starter.py",
        )

        public_result = run_pytest(
            temporary_task / "test_public.py",
            temporary_task,
        )
        hidden_result = run_pytest(
            temporary_task / "test_hidden.py",
            temporary_task,
        )

    return public_result, hidden_result


def _pytest_failure_summary(result: dict[str, Any]) -> str:
    lines = [
        line.strip()
        for line in result["output"].splitlines()
        if line.strip()
    ]

    for line in reversed(lines):
        if re.search(
            r"\b(failed|error|errors)\b",
            line,
            flags=re.IGNORECASE,
        ):
            return line

    return f"pytest exited with code {result['returncode']}"


def validate_reference_solution(
    task_path: Path,
) -> dict[str, Any]:
    """
    Run the reference and starter in isolated task copies.

    The original task is hashed before and after execution so an
    accidental mutation is also an integrity error.
    """
    result: dict[str, Any] = {
        "reference_public_passed": None,
        "reference_hidden_passed": None,
        "starter_overall_passed": None,
        "errors": [],
    }
    execution_files = (
        "starter.py",
        "reference_solution.py",
        "test_public.py",
        "test_hidden.py",
    )
    missing = [
        filename
        for filename in execution_files
        if not (task_path / filename).is_file()
    ]

    if missing:
        result["errors"].append(
            "Cannot validate solutions; missing required files: "
            + ", ".join(missing)
        )
        return result

    try:
        before = _directory_snapshot(task_path)
        reference_public, reference_hidden = _run_solution(
            task_path,
            task_path / "reference_solution.py",
        )
        starter_public, starter_hidden = _run_solution(
            task_path,
            task_path / "starter.py",
        )
    except (OSError, UnicodeError) as error:
        result["errors"].append(
            f"Could not execute validation tests: {error}"
        )
        return result

    result["reference_public_passed"] = reference_public["passed"]
    result["reference_hidden_passed"] = reference_hidden["passed"]
    result["starter_overall_passed"] = (
        starter_public["passed"] and starter_hidden["passed"]
    )

    if not reference_public["passed"]:
        result["errors"].append(
            "reference_solution.py failed public tests "
            f"({_pytest_failure_summary(reference_public)})"
        )

    if not reference_hidden["passed"]:
        result["errors"].append(
            "reference_solution.py failed hidden tests "
            f"({_pytest_failure_summary(reference_hidden)})"
        )

    if result["starter_overall_passed"]:
        result["errors"].append(
            "starter.py passes all tests; task requires no repair"
        )

    after = _directory_snapshot(task_path)

    if before != after:
        result["errors"].append(
            "validation modified the original task directory"
        )

    return result


def validate_prompt_contract(
    task_path: Path,
    metadata: dict[str, Any] | None,
) -> list[str]:
    """Return warnings for declared contract phrases absent from prompt."""
    prompt_path = task_path / "prompt.md"

    if not prompt_path.is_file() or metadata is None:
        return []

    keywords = metadata.get("contract_keywords")

    if not isinstance(keywords, list):
        return []

    try:
        prompt = prompt_path.read_text(encoding="utf-8").casefold()
    except (OSError, UnicodeError):
        return ["prompt.md could not be read for contract validation"]

    return [
        f'Contract keyword "{keyword}" not found in prompt.md'
        for keyword in keywords
        if isinstance(keyword, str)
        and keyword.strip()
        and keyword.casefold() not in prompt
    ]


def validate_task(task_path: Path) -> dict[str, Any]:
    """Collect every validation issue for one benchmark task."""
    errors = validate_task_structure(task_path)
    metadata, metadata_errors = validate_metadata(task_path)
    errors.extend(metadata_errors)

    public_count, hidden_count, suite_errors = (
        validate_test_suites(task_path, metadata)
    )
    errors.extend(suite_errors)

    execution_result: dict[str, Any] = {
        "reference_public_passed": None,
        "reference_hidden_passed": None,
        "starter_overall_passed": None,
        "errors": [],
    }

    if all(
        (task_path / filename).is_file()
        for filename in (
            "starter.py",
            "reference_solution.py",
            "test_public.py",
            "test_hidden.py",
        )
    ):
        execution_result = validate_reference_solution(task_path)
        errors.extend(execution_result["errors"])

    warnings = validate_prompt_contract(task_path, metadata)
    task_id = (
        metadata.get("task_id")
        if isinstance(metadata, dict)
        else None
    )

    if not isinstance(task_id, str):
        task_id = task_path.name

    return {
        "task_id": task_id,
        "task_folder": task_path.name,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "public_test_count": public_count,
        "hidden_test_count": hidden_count,
        "reference_public_passed": execution_result[
            "reference_public_passed"
        ],
        "reference_hidden_passed": execution_result[
            "reference_hidden_passed"
        ],
        "starter_overall_passed": execution_result[
            "starter_overall_passed"
        ],
    }


def _append_cross_task_checks(
    task_results: list[dict[str, Any]],
) -> None:
    results_by_id: dict[str, list[dict[str, Any]]] = {}

    for result in task_results:
        task_id = result["task_id"]

        if TASK_ID_PATTERN.fullmatch(task_id):
            results_by_id.setdefault(task_id, []).append(result)

    for task_id, matching_results in results_by_id.items():
        if len(matching_results) > 1:
            for result in matching_results:
                result["errors"].append(
                    f"Duplicate task_id: {task_id}"
                )

    ordered_ids = sorted(
        results_by_id,
        key=lambda task_id: int(task_id.removeprefix("task_")),
    )

    for previous, current in zip(ordered_ids, ordered_ids[1:]):
        previous_number = int(previous.removeprefix("task_"))
        current_number = int(current.removeprefix("task_"))

        if current_number - previous_number > 1:
            results_by_id[current][0]["warnings"].append(
                f"Task IDs skip from {previous} to {current}"
            )

    for result in task_results:
        result["valid"] = not result["errors"]


def validate_all_tasks(tasks_directory: Path) -> dict[str, Any]:
    """Validate all discovered tasks and return a JSON-ready report."""
    global_errors: list[str] = []

    try:
        task_paths = discover_tasks(tasks_directory)
    except FileNotFoundError as error:
        task_paths = []
        global_errors.append(str(error))

    if not task_paths and not global_errors:
        global_errors.append(
            f"No benchmark tasks found in {tasks_directory}"
        )

    task_results = [
        validate_task(task_path)
        for task_path in task_paths
    ]
    _append_cross_task_checks(task_results)

    error_count = len(global_errors) + sum(
        len(result["errors"]) for result in task_results
    )
    warning_count = sum(
        len(result["warnings"]) for result in task_results
    )

    return {
        "benchmark_valid": error_count == 0,
        "task_count": len(task_results),
        "error_count": error_count,
        "warning_count": warning_count,
        "global_errors": global_errors,
        "tasks": task_results,
    }
