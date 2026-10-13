# Running Code Reliability Bench

## Complete Linux workflow

With Python 3.11 or newer and Docker's Linux engine running, execute this command
from the repository root:

```bash
python3 -m runner.docker_benchmark
```

It builds the image, runs the full corpus quality audit, and evaluates all
reference candidates with an all-pass requirement. Each invocation preserves its
own results under `work/docker-runs/`. To evaluate another solution set:

```bash
python3 -m runner.docker_benchmark \
  --solution-set /path/to/candidates \
  --model my-model \
  --condition one_shot
```

The [Docker workflow guide](docker_workflow.md) documents validation, resource
limits, suite and whole-workflow deadlines, output files, and exit semantics.
The commands below use the native runner after installing the dependencies.

## Candidate solution sets

A solution set contains one Python candidate per benchmark task.

Example:

```text
results/candidates/reference/
├── task_001.py
└── task_002.py
```

Candidate filenames must match the `task_id` in each task's
`metadata.json`.

## Run one task

```bash
python runner/run_task.py \
  --task tasks/task_001_rolling_zscore \
  --solution results/candidates/reference/task_001.py \
  --model reference \
  --condition validation
```

## Run the full benchmark

```bash
python runner/run_benchmark.py \
  --solution-set results/candidates/reference \
  --model reference \
  --condition validation
```

## Individual run artifacts

Each attempted task produces a directory under:

```text
results/runs/<task_id>/<run_id>/
```

It contains:

* `result.json`
* `candidate_snapshot.py`
* `prompt.md`
* `public_test_output.txt`
* `hidden_test_output.txt`

## Aggregate results

Each full benchmark run creates:

```text
results/summaries/<model>_<condition>_results.csv
results/summaries/<model>_<condition>_summary.json
```

## Metrics

### Public pass rate

The fraction of benchmark tasks for which the candidate passes all
public tests.

### Hidden pass rate

The fraction of benchmark tasks for which the candidate passes all
hidden tests.

### Overall pass rate

The fraction of benchmark tasks for which the candidate passes both
public and hidden tests.

### Public-hidden gap

```text
public pass rate - hidden pass rate
```

A large gap suggests that candidate solutions pass obvious examples
but fail less visible edge cases.

## Missing candidates

If a solution set does not contain a candidate for a task, the batch
runner records the task as `missing_candidate`.

Missing candidates count as unsolved in aggregate pass rates, but they
remain distinct from attempted candidates that failed.

## Deadlines and execution evidence

Both native evaluation commands accept `--timeout-seconds` (default 10 seconds per
suite). It must be finite and positive. The validator uses the same default.
Timeouts produce a failed result with `public_execution.status` or
`hidden_execution.status` equal to `timeout`, then evaluation continues.

A zero process exit alone is insufficient: a passing suite needs a nonempty
JUnit report with no failures, errors, or skipped tests. Collection errors and
missing reports are marked `error`. An ordinary assertion failure is `failed`.
JUnit failure names and separate failure/error/skip counts are saved in each
result. Empty or skipped suites never count as passing.

Each run also stores:

* `task_snapshot/` with the executed tests, prompt, starter, and metadata;
* `public_test_results.xml` and `hidden_test_results.xml` when reports exist;
* the candidate and task SHA-256 hashes;
* Python, pytest, and platform versions, suite timings, and deadline settings.

Snapshots are captured before candidate execution. Public and hidden suites run
in separate directories without a reference solution. Ambient pytest options
and third-party plugins are disabled. These controls do not sandbox hostile
code; see the [execution boundary](methodology.md#execution-boundary).

Native summary paths are convenience files and are replaced for a repeated
model/condition. The individual run directories retain detailed evidence. Use a
new `--results-root` per frozen native experiment and preserve its configuration
and summary alongside the runs. The Docker wrapper creates a unique invocation
directory automatically, keeping each invocation's summaries separate.

## Verify the published corpus

```bash
python runner/check_quality.py --report-path work/quality.json
```

This validates the tasks, confirms the reference candidate set, counts executed
reference tests, and evaluates every deliberately flawed baseline. The default
gates require at least 32 tasks and 200 tests. Failing hidden assertions count
as defect detection; collection errors and timeouts do not. The command returns
a nonzero exit status if any gate fails. Its report includes exact baseline
failure names and a deterministic corpus fingerprint.
