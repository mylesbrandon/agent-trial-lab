# Contributing

Use Python 3.11+ and install the hash-locked requirements in a virtual environment.
Run `python -m pytest -q` for the harness and `python runner/check_quality.py`
for the complete corpus. Both must pass before proposing a change.

A new task needs prompt.md, starter.py, reference_solution.py, test_public.py,
test_hidden.py, and metadata.json. Include its matching reference candidate and
at least one named, plausible flawed implementation under results/baselines/.
Read [task guidelines](docs/task_guidelines.md) and [methodology](docs/methodology.md).

Make input types, ordering, ties, empty inputs, invalid inputs, and temporal or
numeric boundaries explicit. Hidden cases must follow the written contract.
Use literal worked expectations or a genuinely independent oracle; do not build
expected outputs by calling the reference implementation. Include diagnostic
failure names, not multiple copies of the same case to increase counts.

Review both the reference and the test's expected answer. A reference passing its
own suite is necessary but insufficient. Demonstrate that a plausible wrong
implementation fails meaningful hidden tests. Keep tests deterministic and small.

Changing a task changes the benchmark. Record the revision and regenerate the
current quality report; never rewrite frozen historical experiments. Preserve
raw model responses and distinguish model failures from capture or harness errors.
Do not describe automated or AI review as independent human review.

To refresh dependencies intentionally, edit requirements.in and run
`uv pip compile requirements.in --generate-hashes --universal --output-file requirements.txt`.
Review the dependency changes and rerun the checks.
