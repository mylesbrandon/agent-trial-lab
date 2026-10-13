# Docker evaluation workflow

The Docker workflow runs the complete benchmark on Linux from one command. It
builds the execution image, audits the corpus, evaluates the solution set, and
preserves each invocation's evidence in a new directory.

## Requirements and first run

Use Python 3.11 or newer on the host, Docker on `PATH`, and a running Docker
engine configured for Linux containers. Docker Desktop provides such an engine
on macOS and Windows. The host command uses only Python's standard library;
pytest and the locked dependencies are installed inside the image.

From the repository root:

```bash
python3 -m runner.docker_benchmark
```

On Windows, use `py -m runner.docker_benchmark` if `python3` is unavailable.
Building needs network access to obtain the base image and dependencies.
Evaluation itself has no network access and needs no model account.

The default solution set is the repository's reference candidates. Before
evaluation, the workflow validates every task's reference and flawed starter,
checks agreement with the reference candidate set, and runs the deliberate
defect fixtures. The quality gates require at least 32 tasks and 200 executed
corpus tests. The current corpus has 32 tasks, 373 tests, and 39 deliberate
defects. The complete default evaluation then requires all reference candidates
to pass both public and hidden suites.

Reference results establish that the benchmark is internally consistent; they
are not model performance measurements.

## Evaluate your own candidates

Use one Python file per task, named `task_001.py` through `task_032.py`:

```bash
python3 -m runner.docker_benchmark \
  --solution-set /path/to/candidates \
  --model my-model \
  --condition one_shot \
  --results-root work/docker-runs
```

The solution set is mounted read-only. Missing files count as unsolved tasks.
Ordinary failed tests, syntax errors, missing candidates, and candidate suite
timeouts are recorded in the score. They do not stop the other tasks from being
evaluated. Add `--require-all-pass` when every task must pass, such as a CI gate
for a known-good solution set.

Corpus validation must succeed for any solution set. A broken reference,
unexpectedly passing starter, or undetected deliberate defect fails that gate
before candidate evaluation starts.

## Deadlines

All deadline arguments must be finite, positive numbers.

| Argument | Default | Applies to |
| --- | --- | --- |
| `--timeout-seconds` | 10 seconds | Each candidate's public suite and hidden suite independently |
| `--validation-timeout-seconds` | 10 seconds | Each suite executed during the corpus quality audit |
| `--run-timeout-seconds` | 600 seconds | The entire container workflow, including validation and candidate evaluation |
| `--build-timeout-seconds` | 600 seconds | The image build, before the container workflow |

A task can therefore use up to two candidate suite deadlines. A suite timeout
terminates its pytest process group on Linux, records `timeout`, and continues
evaluation. The whole-workflow deadline is separate: it stops and removes the
container and leaves the available partial evidence. An interrupted workflow
also attempts container cleanup. The host report records cleanup status; inspect
that status after a daemon failure or an interrupted run.

For example, allow a slower validation host while keeping candidate deadlines
short:

```bash
python3 -m runner.docker_benchmark \
  --solution-set /path/to/candidates \
  --model my-model --condition one_shot \
  --timeout-seconds 5 \
  --validation-timeout-seconds 20 \
  --run-timeout-seconds 900
```

Partial results from a whole-workflow timeout are not a complete benchmark
score. Check both the process exit status and the workflow report before
publishing a run.

## Results and reproducibility

Every invocation creates a timestamp-and-UUID directory under `--results-root`
(default `work/docker-runs`). Repeating the same model and condition does not
replace an earlier invocation's evidence.

```text
work/docker-runs/<invocation>/
├── docker-run.json
├── quality.json
├── workflow.json
└── evaluation/
    ├── runs/<task_id>/<run_id>/
    └── summaries/
```

`docker-run.json` records the host orchestration, image identity, platform,
resource limits, deadlines, completion status, and cleanup outcome. `quality.json`
records the corpus validation, fingerprint, executed test counts, and deliberate
defect results. `workflow.json` records the container workflow's outcome. The
evaluation directories contain per-task candidate and grading-file snapshots,
hashes, logs, JUnit reports when available, timings, and aggregate scores.
Files produced later in the workflow may be absent after an early failure.

The Dockerfile pins the Python 3.14.6 slim-bookworm base image by digest and
installs dependencies using the checked-in hash lock. The build context excludes
local environments, credentials, Git history, and old experiment outputs. The
wrapper runs the resolved image ID and records it, so a subsequently moved image
tag does not change an in-progress run.

To reuse an already-built image, pass its image ID with `--image`. That skips the
build, so it also skips incorporating subsequent source changes. Preserve the
report's image ID and corpus fingerprint when comparing results from different
machines. A pinned image does not make execution timings identical across CPUs
or Docker hosts.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Corpus validation succeeded and evaluation completed; any required all-pass gate succeeded |
| `124` | A host-controlled build, setup, or whole-workflow deadline was exceeded; inspect `docker-run.json` for the phase |
| `130` | The host command was interrupted |
| Other nonzero status | Invalid configuration, build/runtime failure, corpus validation failure, or an all-pass gate failure |

For custom candidates, exit status zero means the evaluation completed, not that
the candidates solved every task. Read the scores, or enable `--require-all-pass`.
The default reference run always requires all tasks to pass.

## Execution boundary

The evaluation container uses a non-root user, a read-only root filesystem,
`--network none`, dropped Linux capabilities, and `no-new-privileges`. Its limits
are two CPUs, 1 GiB of memory, 128 processes, and 256 MiB of temporary space.
The custom candidate directory is read-only; only the dedicated output directory
is a writable host mount. No Docker socket or full repository checkout is mounted.
On POSIX hosts with a non-root account, the wrapper maps the host user's numeric
identity so generated reports are owned by that user. It uses container UID/GID
10001 when the host account is root or does not expose a POSIX identity.

These controls bound common failures and reduce host exposure for reviewed code.
They are not a complete defense against hostile submissions. The image contains
the public corpus, including reference solutions and hidden tests. Candidates
can discover those files or modify writable reports. Captured output can also
consume memory and output storage. This workflow cannot certify an adversarial
submission's score, promise secret tests, or guarantee host security. A service
accepting unknown submissions needs a separately designed execution and grading
boundary.

## Continuous integration

The Linux Docker CI job builds the image and runs the same default CLI workflow.
It checks the expected 32-task, 373-test, 39-defect corpus and the complete
reference evaluation, and exercises timeout handling and container cleanup.
Validation and execution reports are uploaded as CI artifacts.

The native CI matrix separately runs the harness and full quality audit on
Linux, macOS, and Windows with Python 3.11 and 3.14. Workflow configuration
describes the required checks; a successful run on a particular commit is the
evidence that those checks passed for that revision. Consult the repository's
[Actions history](https://github.com/mylesbrandon/code-reliability-bench/actions)
for that evidence.
