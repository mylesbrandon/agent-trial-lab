# Failure taxonomy

Classify the preserved candidate using its code, the prompt, and recorded
evaluation evidence. Choose one primary category for the observed outcome;
add secondary categories only when there is concrete supporting evidence.
Task-domain labels such as `numerical_robustness` describe the benchmark,
not the cause of a particular candidate's failure.

## passed

The candidate passed both the public and hidden suites. This establishes
correctness on the evaluated cases, not on every possible input.

## syntax_error

The candidate cannot compile as Python, including indentation errors,
unterminated strings, and statements such as `return` outside a function.
Collection failures caused by this invalid candidate belong here, not under
evaluation infrastructure errors.

## runtime_error

The candidate compiles but raises an unexpected exception during import or
execution. Prefer a more specific category when the evidence establishes
a numerical, validation, algorithmic, or state-related root cause.

## spec_misunderstanding

The implementation follows a rule that conflicts with an explicit prompt
requirement. Cite the requirement and conflicting code; a failed assertion
alone does not establish that the specification was misunderstood.

## algorithmic_error

The core algorithm or its invariants are incorrect for the specified
problem. Examples include incorrect edge relaxation or path reconstruction.

## edge_case_failure

The candidate's main approach is substantially correct, but it fails one
or more explicitly specified boundary, degenerate, or robustness cases.

## numerical_error

The implementation computes an incorrect numerical quantity or mishandles
arithmetic stability, precision, or numerical degeneracy. Examples include
using sample instead of population variance or dividing by zero variance.

## data_validation_failure

The implementation accepts invalid data, rejects valid data, or fails the
specified parsing, normalization, conversion, or error-handling contract.

## state_or_timing_error

The implementation uses information from the wrong point in a sequence or
maintains state incorrectly. Examples include lookahead bias and incorrect
transaction-cost alignment.

## incomplete_solution

The submitted module omits required implementation or structure, such as
the callable function, necessary imports, or a required branch. A fragment
with otherwise plausible logic is still incomplete when it cannot provide
the requested interface.

## evaluation_infrastructure_error

A defect in the benchmark prompt/test contract, reference, evaluator, or
artifact handling prevents a trustworthy assessment or produces an incorrect
grade. Identify the defect directly; a candidate-induced collection error
is not by itself evidence of an infrastructure defect.

### Recording conventions

- `primary_failure` contains one category above. A passed task must use
  `passed`, with empty `secondary_failures` and `failed_tests` lists.
- `failed_tests` contains exact failed test names from evaluation artifacts.
  If import/collection fails before any test executes, use `[]` and cite the
  collection error in `evidence`. A zero `failed_test_count` then means no
  individual test failures were recorded; it does **not** mean the task passed.
- Confidence is `high` for directly reproduced or unambiguous code/log evidence,
  `medium` for supported but partly inferred causes, and `low` when evidence is
  insufficient to distinguish plausible causes. Confidence in an artifact's
  failure does not imply confidence about who introduced it.
- `task_action` maps `keep` to "keep task unchanged", `clarify_prompt` to
  "clarify prompt", `improve_test` to "improve test", and `fix_evaluator` to
  "fix evaluator". Explain the choice in the task analysis.
- In summary CSVs, booleans are lowercase and multiple secondary categories
  are separated by semicolons; an empty list is an empty field. Distribution
  tables count primary categories once per task unless stated otherwise.
