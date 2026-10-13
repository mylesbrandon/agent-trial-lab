# Code Reliability Bench

An execution-graded benchmark for coding agents.

It tests whether agents implement a written contract correctly, including the
edge cases their visible tests miss.

The corpus contains **32 Python programming tasks and 373 public/hidden tests**, balanced across numerical
robustness, graph algorithms, time-series alignment, and CSV parsing. Each task
includes a specification, a flawed starter, a reference implementation, public
and hidden tests, metadata, and at least one deliberate defect fixture.

This project was previously named CodeAgentBench. It is now Code Reliability Bench to
avoid confusion with other projects using that name. The original Git history
and frozen experiment evidence are preserved.

## What it measures

The primary scores are the proportions of tasks passing every public test,
every hidden test, and both suites. Missing candidates count as unsolved and
remain separately identified. The public–hidden gap helps locate solutions
that handle the visible examples but miss requirements elsewhere in the prompt.

A reference implementation passing its tests verifies internal consistency;
it is not a coding-agent result. Known flawed implementations check that tests
can detect specific defects; they do not establish general detection coverage.

See the [task catalog](docs/task_catalog.md), [methodology](docs/methodology.md),
and [measured quality report](reports/quality.md). The report's machine-readable
companion includes a corpus fingerprint and exact failed tests for each defect.

## Quick start

Install Python 3.11 or newer and Docker with a running Linux container engine.
Then clone the repository and run the complete reference benchmark:

```bash
git clone https://github.com/mylesbrandon/code-reliability-bench.git
cd code-reliability-bench
python3 -m runner.docker_benchmark
```

The single command builds the Linux image, validates the corpus and reference
solutions, checks starters and deliberate defect fixtures, and evaluates all
32 reference candidates. It needs no model account or host Python packages.
The default run requires every reference candidate to pass both suites. Docker
needs network access to build the image; evaluation runs without a network.

Each invocation writes a separate directory under `work/docker-runs/` with
the image identity, validation report, task results, logs, and execution settings.
Public and hidden suites each have a 10-second deadline; the complete container
workflow has a separate 600-second deadline. See the [Docker workflow guide](docs/docker_workflow.md)
for custom candidates, resource limits, exit codes, and timeout cleanup.

For native development without Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python -m pytest -q
python runner/check_quality.py
```

On Windows, create the environment with `py -m venv .venv` and activate it
with `.venv\Scripts\Activate.ps1` in PowerShell. The harness uses Python's
standard library and pytest; no model account is needed for validation.

`check_quality.py` verifies the minimum 32 tasks / 200 executed tests target,
reference correctness, rejection of flawed starters, agreement between task
references and the reference candidate set, and hidden-test rejection of
known defect fixtures. It writes `work/quality.json` and exits nonzero if a
check fails. Counts exclude harness tests, repeated runs, and skipped cases.

CI runs the native checks on Linux, macOS, and Windows with Python 3.11 and 3.14.
A Linux Docker job exercises the complete workflow and its timeout controls.

## Evaluate a solution set

Place candidate files named `task_001.py` through `task_032.py` in a directory:

```bash
python3 -m runner.docker_benchmark \
  --solution-set /path/to/candidates \
  --model your-model \
  --condition one_shot \
  --timeout-seconds 10 \
  --results-root work/docker-runs
```

The candidate directory is mounted read-only. Candidate failures and missing
files affect the score; a completed evaluation still exits successfully unless
you add `--require-all-pass`. Corpus validation failures always stop the workflow.

Each public and hidden suite receives a fresh working directory containing
only its test module and the candidate as `starter.py`. A pass requires a
successful process exit and a nonempty JUnit report with no failures, errors,
or skips. Timeouts and collection errors are recorded separately from test
failures. Runs preserve candidate and task snapshots, SHA-256 hashes, runtime
versions, logs, structured suite counts, and timings.

**Execution is for trusted or reviewed candidate code.** The Docker workflow
uses a non-root user, a read-only root filesystem, no network, and bounded CPU,
memory, process count, and temporary space. It is not a grading service for
hostile submissions: the public corpus, including references, is readable in
the image, and candidates can alter writable reports. The native runner executes
with your account's filesystem and network access. See
[execution limits](docs/methodology.md#execution-boundary).

Full commands and result semantics are in the
[runner guide](docs/running_the_benchmark.md).

## Generate candidates

Generation includes only the specification, starter, and public tests:

```bash
python runner/generate_candidates.py \
  --agent manual --model your-model --condition one_shot --tasks task_005
```

The manual and deterministic mock adapters are included. Each generation
attempt gets a new evidence directory with its prompt, raw response, extracted
source when valid, timestamps, hashes, and environment information. Repeating
an attempt never overwrites earlier evidence. The clean solution-set directory
contains the latest attempt per task.

See [generation documentation](docs/agent_generation.md) for adapters,
syntax validation, failed-attempt handling, and information separation.

## Evidence and limitations

Pilot 001 is preserved under `results/experiments/pilot_001/`. All four captured
responses were syntax-invalid, so its recorded 0/4 score does **not** establish
behavioral model performance. Manual copy/paste leaves the origin of formatting
damage uncertain. See the [original analysis](results/experiments/pilot_001/analysis.md).

The test corpus is public. “Hidden” means withheld from the generation prompt,
not secret or guaranteed absent from training data. The tasks are focused
function-level repairs, not full repository development. No new multi-model
comparison or independent human validation is claimed by this release.

## Development and authorship

This is an independent, AI-assisted project. AI assistance was used to draft
and review code, task contracts, tests, and documentation. Automated reference
checks, deliberately flawed controls, and independent agent review support
this release; they do not substitute for human review or prove that every
specification is complete. See the [development notes](docs/development.md)
for the current release's scope and the [contributor guide](CONTRIBUTING.md)
for how to add or revise tasks without invalidating old evidence.

## License

[MIT](LICENSE). Copyright 2026 Myles Brandon.
