# Benchmark Validation

Benchmark scores are only meaningful when each task is complete,
internally consistent, and fair. The validator checks these properties
before candidate solutions are evaluated. It catches mechanical
problems automatically while leaving semantic fairness and test
quality subject to human review.

## Required Task Files

Every task directory must contain:

* `prompt.md`
* `starter.py`
* `reference_solution.py`
* `test_public.py`
* `test_hidden.py`
* `metadata.json`

Validation collects all discovered errors instead of stopping after the
first missing or malformed file.

## Metadata Schema

`metadata.json` must define:

* `task_id`: a string matching `task_###`; the folder must begin with
  the same ID
* `name`: a nonempty string
* `category`: a nonempty string
* `difficulty`: `easy`, `medium`, or `hard`
* `concepts`: a nonempty list of nonempty strings
* `public_tests`: a nonnegative integer
* `hidden_tests`: a nonnegative integer
* `failure_modes_targeted`: a nonempty list of nonempty strings
* `contract_keywords`: a nonempty list of important prompt phrases

The validator parses both test files with Python's AST and compares the
number of `test_` functions with the declared test counts. Task IDs
must be unique. A gap in the numerical ID sequence produces a warning.

## Executable Integrity Checks

For each task, the validator copies the task into temporary directories
and runs public and hidden tests twice:

1. with `reference_solution.py` copied over the temporary `starter.py`;
2. with the original `starter.py`.

The reference solution must pass both suites. The starter must fail at
least one test so that the task requires a meaningful repair. Only
temporary copies are executed, and the validator confirms that the
source task remains unchanged.

Public and hidden suites must each contain at least one test and must
not be byte-for-byte identical. Both must import `starter`. Neither may
import `reference_solution`, and public tests may not import hidden
tests.

## Prompt Contracts and Fairness

Each phrase in `contract_keywords` must appear in `prompt.md`.
Missing phrases are warnings because spelling and formatting can cause
false positives. These checks provide lightweight evidence that
important hidden-test requirements are disclosed, but they do not
replace human review of the prompt and tests.

## Running Validation

From the repository root:

```bash
python runner/validate_benchmark.py
```

The command prints every task result and writes the deterministic,
machine-readable report to:

```text
results/validation/benchmark_validation.json
```

An error makes the affected task and the benchmark invalid and causes
the command to exit nonzero. A warning identifies something worth
reviewing but does not invalidate the benchmark.
