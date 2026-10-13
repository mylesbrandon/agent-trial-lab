# Methodology and evidence boundaries

## Task design

A task is one observable programming contract, not one assertion. The four
areas each contain eight tasks. New tasks separate different failure mechanisms:
float overflow versus quantile interpolation, graph reachability versus minimum
spanning forests, observation-time alignment versus interval leakage, and CSV
record decoding versus relational cardinality.

Each prompt states the accepted types, result shape, invalid-input behavior,
ordering rules, and boundary conventions tested. Public tests provide examples;
hidden tests probe additional requirements in the same contract. Expected values
come from worked examples and invariants. No hidden requirement should be added
only to defeat a particular candidate.

## Counting and validation

The published test count is the number of pytest cases actually executed by the
reference suites across distinct tasks. The validator also compares this count
with the source's named test functions and metadata. Current task suites use
ordinary functions, without parametrization or skipped cases. Multiple asserts
or a loop over invalid inputs inside one function still count as **one** test.
Harness regressions, repeated reference runs, and defect-fixture runs do not
inflate corpus size.

The quality command checks every reference, every starter, and every checked-in
flawed baseline. A defect is counted as detected only when a hidden test fails
behaviorally: syntax/collection errors, timeouts, and missing execution evidence
are excluded from that success count. Fixtures demonstrate sensitivity to those
particular mistakes. They are not a random sample or an estimate of general
mutation coverage.

## Scoring

For N tasks, public pass rate = tasks passing the entire public suite / N.
Hidden and overall pass rates use the same denominator. Overall requires both
suites to pass. Missing submissions remain in the denominator and receive a
separate status. Per-test counts are diagnostic and are not mixed with task
pass rates. A small public–hidden gap does not establish broad competence.

The four-task pilot remains a historical experiment. It is not rerun silently
against the expanded corpus. Any future comparison must freeze the task revision,
model identifier, prompts, generation settings, sampling count, feedback budget,
and stopping rule before evaluating the hidden tests.

## Generation boundary

Only prompt.md, starter.py, and test_public.py enter the generation prompt.
Withhold task references, hidden tests, baseline implementations, and prior hidden
results from model participants. This is a protocol: an agent with repository
access can read public files, so a genuine blind trial must run generation from
an exported visible-only bundle or a similarly restricted context.

Each request creates a separate immutable attempt directory. Raw response hashes
and extracted candidate hashes distinguish source capture from execution. A
failed latest attempt clears its clean candidate so an old success is not
silently evaluated in its place. Attempt directories preserve prior evidence.

## Execution boundary

The local runner uses fresh directories per suite, omits reference files, ignores
external Python/pytest configuration, disables third-party plugin autoload, and
requires structured nonempty execution evidence. The default deadline is 10
seconds per suite. On POSIX, timeout termination targets the process group; on
Windows it terminates the pytest process, so child-process containment is weaker.

These measures prevent common accidental scoring corruption. They do not defend
against deliberate test/report tampering or filesystem access outside the test
directory. There is no network isolation, memory limit, or hostile-code sandbox.
Output is captured in memory. Only run trusted or reviewed code locally. A future
untrusted-submission service needs a separately designed isolation boundary.

## Reproducibility and release claims

The dependency lock contains hashes. Each evaluation records the Python/pytest
versions, OS, candidate bytes, grading files, and hashes. The corpus report hashes
all six canonical files for every task in deterministic path order. Original
experiment artifacts are retained rather than edited into better outcomes.

Claims supported by this release concern corpus size and checks performed. They
do not imply external adoption, broad model accuracy, publication, novelty of
underlying algorithms, contamination resistance, or independent human review.
