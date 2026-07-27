# CodeAgentBench

CodeAgentBench is a small, reproducible benchmark for evaluating how reliably LLM coding agents solve verifiable programming tasks.

The project focuses on more than whether generated code looks plausible. Each task is graded through executable tests, including hidden cases designed to expose shallow implementations, missed edge cases, and specification misunderstandings.

The benchmark currently contains three execution-graded Python tasks
across numerical robustness, algorithmic debugging, and time-series
correctness.

## Project Goals

CodeAgentBench is being built to explore questions such as:

* Can an LLM-generated solution pass both basic and adversarial tests?
* How often do coding agents pass visible tests but fail hidden tests?
* What types of errors occur most frequently?
* How do prompting and feedback strategies affect correctness?
* Can a small benchmark produce useful failure analysis rather than only a single score?

The project is also intended as an exercise in benchmark design, software testing, reproducible experimentation, and AI evaluation.

## Current Status

The project is in its initial development stage.

Currently implemented:

* Standardized benchmark task structure
* Public and hidden test separation
* Verified reference solutions
* Task metadata and failure-mode labels
* A task runner for evaluating candidate solutions
* Task 001: Rolling Z-Score
* Task 002: Shortest-Path Bug Repair
* Task 003: Lookahead-Safe Signal Alignment
* Initial benchmark-design and failure-analysis documentation

Planned next steps:

* Add additional benchmark tasks
* Add one-shot and test-feedback agent baselines
* Expand failure-mode analysis
* Add safer execution isolation for generated code

## Repository Structure

```text
CodeAgentBench/
├── agents/                  # LLM agent and prompting strategies
├── docs/                    # Benchmark design and methodology notes
├── reports/                 # Technical reports and project writeups
├── results/                 # Evaluation results and failure analyses
├── runner/                  # Benchmark execution scripts
├── tasks/                   # Individual benchmark tasks
│   └── task_001_rolling_zscore/
│       ├── prompt.md
│       ├── starter.py
│       ├── reference_solution.py
│       ├── test_public.py
│       ├── test_hidden.py
│       └── metadata.json
├── .gitignore
├── requirements.txt
└── README.md
```

## Benchmark Task Design

Each task contains six core files.

### `prompt.md`

The written specification shown to the coding agent.

The prompt defines the expected behavior, inputs, outputs, and relevant edge-case requirements.

### `starter.py`

The incomplete or incorrect implementation that the coding agent must modify.

### `reference_solution.py`

A known-good implementation used to verify that the task and its tests are internally consistent.

### `test_public.py`

Visible tests that check basic behavior and clarify the task.

Public tests are intentionally limited. Passing them does not guarantee that a candidate solution is correct.

### `test_hidden.py`

Private tests that check boundary conditions, numerical issues, robustness, and common implementation mistakes.

Hidden tests may test difficult cases, but they should never enforce requirements that are absent from the prompt.

### `metadata.json`

Structured information about the task, including:

* category
* difficulty
* concepts tested
* number of public and hidden tests
* targeted failure modes
* expected agent mistakes

## Current Benchmark Tasks

| Task | Category | Capability |
|---|---|---|
| `task_001_rolling_zscore` | Numerical robustness | Rolling windows, NaNs, zero variance, population standard deviation |
| `task_002_shortest_path` | Algorithmic debugging | Dijkstra repair, edge relaxation, graph edge cases, path reconstruction |
| `task_003_signal_alignment` | Time-series correctness | Return alignment, lookahead-bias prevention, turnover-based transaction costs |

## Task 001: Rolling Z-Score

The first task asks an agent to implement a rolling z-score function.

It evaluates whether the candidate can correctly handle:

* rolling-window selection
* population standard deviation
* zero-variance windows
* missing values represented by `NaN`
* invalid window sizes
* windows larger than the input
* negative values
* numerical edge cases

The task is designed to catch implementations that appear correct on simple increasing sequences but fail under less obvious conditions.

## Task 003: Lookahead-Safe Signal Alignment

Task 003 asks an agent to repair a strategy-return calculation that
uses the current signal for an already-realized price movement. A
signal at index `t - 1` is the latest position known before the return
from `t - 1` to `t`, so the aligned calculation uses
`signals[t - 1]`.

The task also checks proportional transaction costs, turnover timing,
long and short positions, flat prices, invalid prices, and boundary
behavior.

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd CodeAgentBench
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

The current project requires Python and `pytest`.

## Running a Task

Run Task 001 against the verified reference solution:

```bash
python runner/run_task.py \
  --task tasks/task_001_rolling_zscore \
  --solution results/candidates/reference/task_001.py \
  --model reference \
  --condition validation
```

On Windows PowerShell, the same command can be written on one line:

```powershell
python runner/run_task.py --task tasks/task_001_rolling_zscore --solution results/candidates/reference/task_001.py --model reference --condition validation
```

Expected output for a correct solution:

```text
Task: task_001 — rolling_zscore
Model: reference
Condition: validation
Public tests: PASS
Hidden tests: PASS
Overall: PASS
```

## Run the full benchmark

```bash
python runner/run_benchmark.py \
  --solution-set results/candidates/reference \
  --model reference \
  --condition validation
```

See `docs/running_the_benchmark.md` for full instructions.

## Evaluation Workflow

The intended workflow for each candidate solution is:

1. Give the agent only the task prompt, starter code, and public tests.
2. Save the agent’s submitted solution.
3. Run the public tests.
4. Run the hidden tests.
5. Record the result.
6. Identify which hidden tests failed.
7. Categorize the failure.
8. Write a short qualitative analysis.

A candidate should not receive access to:

* `reference_solution.py`
* `test_hidden.py`
* prior hidden-test results during final evaluation

## Initial Metrics

The first version of the benchmark will track:

* public-test pass rate
* hidden-test pass rate
* overall task pass rate
* public-to-hidden performance gap
* runtime or syntax errors
* failure categories
* number of revisions used

As the benchmark grows, results will also be grouped by task category and capability.

## Failure Categories

Planned failure labels include:

* edge-case miss
* specification misunderstanding
* public-test overfitting
* runtime error
* incorrect algorithm
* numerical instability
* regression
* excessive time or memory usage
* missing input validation
* lookahead bias in time-series tasks

The goal is to explain why an agent failed, rather than reporting only a total score.

## Benchmark Principles

Tasks in CodeAgentBench should be:

* **Verifiable:** correctness can be determined through execution.
* **Fair:** hidden tests correspond to written requirements.
* **Focused:** each task tests a reasonably narrow set of capabilities.
* **Reproducible:** another person can run the same evaluation.
* **Diagnostic:** failures reveal something meaningful about the candidate.
* **Fresh when possible:** custom tasks reduce reliance on widely circulated coding problems.
* **Transparent:** task design and evaluation methodology are documented.

## Use of AI During Development

AI tools may be used for:

* brainstorming possible edge cases
* debugging test infrastructure
* explaining unfamiliar libraries
* reviewing documentation
* suggesting code refactors
* acting as benchmark participants

However, benchmark design decisions, task specifications, reference-solution verification, hidden-test selection, and failure analysis are manually reviewed.

The purpose of the project is not to avoid AI-assisted development. It is to ensure that the benchmark’s methodology and conclusions are understood and defensible.

## Security Notice

The current runner executes candidate Python code directly on the local machine.

Only trusted or manually reviewed candidate solutions should be evaluated in the current version.

Future versions should add stronger isolation through tools such as:

* Docker containers
* execution timeouts
* CPU and memory limits
* filesystem restrictions
* disabled network access

Do not run arbitrary untrusted code using the current runner.

## Roadmap

### Phase 1: Benchmark Foundation

* [x] Define repository structure
* [x] Establish task file format
* [x] Complete Task 001
* [x] Separate public and hidden tests
* [x] Add metadata and task-design notes
* [x] Complete and validate the task runner
* [x] Test intentionally flawed implementations

### Phase 2: Initial Evaluation

* [ ] Run a one-shot LLM baseline
* [ ] Record public and hidden test results
* [ ] Create a structured results format
* [ ] Write the first detailed failure analyses
* [ ] Add Tasks 004–005

### Phase 3: Benchmark Expansion

* [ ] Expand to at least 10 tasks
* [ ] Add multiple task categories
* [ ] Add a public-test feedback baseline
* [ ] Compare prompting strategies
* [ ] Produce an early technical report

### Phase 4: Reliability and Scale

* [ ] Add isolated execution
* [ ] Add runtime and resource limits
* [ ] Expand to 30–50 tasks
* [ ] Improve contamination documentation
* [ ] Publish reproducible benchmark results

## Contributing

The project is currently an early independent research and learning project.

Potential future contributions may include:

* new benchmark tasks
* stronger hidden tests
* additional agent baselines
* execution-safety improvements
* benchmark-design feedback
* failure-taxonomy improvements

All proposed tasks should include a clear specification, verified reference solution, public tests, hidden tests, and metadata.

## License

A license has not yet been selected.
