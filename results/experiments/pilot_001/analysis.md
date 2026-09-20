# Pilot 001

## Setup

- Model: GPT-5.6 Sol
- Interface: ChatGPT manual copy/paste
- Condition: one-shot
- Tasks: 001-004
- Repetitions: 1
- Regeneration after valid response: none
- Hidden tests shown during generation: no
- Reference solutions shown during generation: no

## Results

- Attempts: 4/4; syntax-valid extracted responses: 0/4
- Public pass rate: 0.0%
- Hidden pass rate: 0.0%
- Overall pass rate: 0.0%
- Public-hidden gap: 0.0%

All eight suite invocations stopped during collection with candidate
`SyntaxError`s (exit code 2). No test function executed. These are task-level
failures, not evidence of wrong numerical, graph, timing, or CSV outputs.
The zero public-hidden gap does not establish equal behavioral coverage.

## Per-task

| Task | Public | Hidden | Overall | Primary | Secondary | Action |
|---|---|---|---|---|---|---|
| [001](analysis/task_001.md) | Collection error | Collection error | Fail | syntax_error | incomplete_solution | keep |
| [002](analysis/task_002.md) | Collection error | Collection error | Fail | syntax_error | incomplete_solution | keep |
| [003](analysis/task_003.md) | Collection error | Collection error | Fail | syntax_error | incomplete_solution | keep |
| [004](analysis/task_004.md) | Collection error | Collection error | Fail | syntax_error | incomplete_solution | keep |

## Failure distribution

Primary categories only; each task is counted once. Definitions are in the
[failure taxonomy](../../../docs/failure_taxonomy.md).

| Failure category | Count |
|---|---:|
| Passed | 0 |
| Syntax error | 4 |
| Runtime error | 0 |
| Specification misunderstanding | 0 |
| Algorithmic error | 0 |
| Edge-case failure | 0 |
| Numerical error | 0 |
| Data-validation failure | 0 |
| State/timing error | 0 |
| Incomplete solution | 0 |
| Evaluation infrastructure error | 0 |

All four tasks additionally have `incomplete_solution` as a secondary
classification: the extracted modules omit their required function
definitions and imports. This is not four additional failed attempts.
Confidence is high about the code/log diagnosis, not about the origin of
the damaged response formatting.

## Public-hidden failures

There are no public-pass/hidden-fail tasks. In every task, both suites
failed to import the same candidate before their behavioral checks ran.
The following describes the intended coverage, not observed successes:

| Task | Public suite checks | Hidden suite adds | Explicitly specified? |
|---|---|---|---|
| 001 | Invalid window, increasing sequence, output length and initial zero | Constant windows, NaNs, negative values, long windows, rolling selection, population variance | Yes: the window formula and numerical rules cover these cases. |
| 002 | Basic/indirect paths, same-node result, missing keys | Unreachable nodes, zero/duplicate edges, later improvement, cycles, directionality, nonmutation | Yes: the graph assumptions and required behaviors cover these cases. |
| 003 | Constant positions, lengths, negative cost, empty input, tuples | Changing signals, turnover timing/size, flat-price costs, input validation, boundaries | Yes: previous-signal alignment and the cost convention are explicit. |
| 004 | Basic conversion, symbol cleanup, empty input, invalid price | Quoted commas, missing numbers, blank rows, whitespace, headers, extra fields, invalid integer volume, multiple records | Yes: the input and normalization contracts specify these cases. |

For example, Task 003's constant-position public cases cannot distinguish
current from previous-signal alignment, while the hidden changing-signal
cases can. That is an intentional, disclosed distinction; this pilot never
reached it. No hidden behavioral assertion explains any of these four failures.

## Benchmark findings

The complete generation requests explicitly require the full contents of
`starter.py`, without Markdown fences. All four captured responses instead
mix an unfenced function header with a fenced body fragment. The extraction
pattern selects that fragment, losing the function header and imports; in
Tasks 001 and 002 it also retains the `yaml`/`lua` fence label. This explains
why the evaluated candidates look different from the beginning of the raw
responses.

The raw responses themselves also fail compilation: their docstrings are
not indented under the function definitions. This is not evidence that a
valid captured solution was wrongly failed by extraction. Neither the
artifacts nor their hashes can determine whether the original model output
or the manual transfer caused the damage. Treat this pilot as evidence about
the captured submission pipeline, with task-level scores preserved, rather
than a measurement of the four intended coding capabilities.

Manual review found no hidden requirement outside the supplied prompts and
no incorrect reference or evaluator outcome responsible for these results.
The candidates are invalid modules, so rejecting them is appropriate. Keep
all four tasks unchanged; no candidate repair, regeneration, or retrospective
replacement is justified. This review does not establish exhaustive coverage
or universal correctness of the reference solutions.

The existing `result.json` failure label `public_and_hidden_test_failure`
and empty failed-test arrays are too coarse for causal analysis. The logs
explain the distinction: collection errors prevented test execution.
[classifications.json](classifications.json) and
[failure_summary.csv](failure_summary.csv) now record that cause without
rewriting the frozen evaluation records. Their `failed_tests: []` and
`failed_test_count: 0` count individual failed tests, not collection errors
or successful tests. There are two collection errors per task.

## Model findings

- Task 001's fragment contains population variance, NaN filtering, and a
  zero-standard-deviation branch, but fails to compile at its unmatched
  triple quote. There is no observed zero-variance or numerical-output failure.
- Task 002's fragment contains strict relaxation and predecessor tracking,
  but its first `return` is outside a function. No graph case was evaluated.
- Task 003's fragment uses the specified previous signal and lagged turnover
  expressions, but has a module-level `return`. No timing behavior was tested.
- Task 004's fragment uses `csv.reader` and explicit conversion/validation
  logic, but ends with a module-level `return`. No CSV record was parsed.

These four captured one-shot attempts produced no executable complete
candidate. They support neither a general claim about GPT-5.6 Sol's reasoning
nor a ranking of its numerical, algorithmic, timing, and parsing abilities.
Even attribution of the formatting errors to the model remains uncertain
because the capture method was manual copy/paste.

## Changes before Pilot 002

1. Verify that the capture method preserves the first response's exact text
   and indentation, with source/export provenance when available. The four
   raw responses all contain unindented function bodies. Record malformed
   first responses as failures; do not fix them or request replacement attempts.
2. Make extraction diagnostics explicit when fences contain only fragments
   or use non-Python labels. Preserve the full raw text and report what was
   selected. Pilot 001 shows why an extracted fragment alone cannot establish
   what a model originally supplied; no re-extraction of this pilot is needed.
3. Carry the new taxonomy and integrity checks forward, distinguishing
   pre-execution collection errors from individual failed tests. Require
   executable attempts before interpreting a public-hidden behavioral gap.
4. Keep these task prompts, tests, and references unchanged. This pilot
   provides no behavioral evidence justifying a change in task difficulty.

## Evidence integrity

All four raw responses, extracted candidates, evaluation snapshots, prompts,
public/hidden logs, and reference/test contracts were reviewed. Preserved
generation hashes were verified, and each candidate matches both its
extracted solution and evaluation snapshot. No generation or original
evaluation artifacts were edited. Classification checks additionally verify
the CSV against the JSON/results and validate failure names against the logs.

Verification for this analysis: `python -m pytest tests -q` passed all 61
tests. Benchmark validation passed all four tasks with zero errors and zero
warnings; every reference passed both suites. Fresh evaluations of the four
unchanged candidates in temporary directories reproduced both collection
failures, exit codes, and empty failed-test lists for each task. The temporary
rechecks did not overwrite the frozen results.
