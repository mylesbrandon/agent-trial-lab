# One-Shot Candidate Generation

Agent Trial Lab separates candidate generation from candidate
evaluation. Generation produces a reproducible record of what an agent
saw and returned. Evaluation can then run the preserved candidate as
many times as needed without calling the agent again.

```text
task prompt + starter code + public tests
-> agent response
-> extracted Python candidate
-> benchmark evaluation
-> run artifacts
```

## Agent-visible information

For each task, the one-shot prompt contains exactly these task files:

* `prompt.md`
* `starter.py`
* `test_public.py`

The prompt builder does not read or include:

* `reference_solution.py`
* `test_hidden.py`
* prior benchmark results
* controlled or flawed baseline solutions

This boundary is essential to benchmark integrity. A candidate that
has seen hidden tests or the reference implementation is not a valid
one-shot benchmark result.

## One-shot condition

Under the `one_shot` condition, the agent receives one complete prompt
and returns one complete replacement for `starter.py`. It receives no
test feedback, repair turn, hidden-test result, or earlier candidate.
The generation command does not execute public or hidden tests.

## Artifact structure

For model `model_001`, the generated artifacts are organized as:

```text
results/
|-- candidates/
|   `-- generated/
|       `-- model_001/
|           `-- one_shot/
|               |-- task_001.py
|               |-- task_002.py
|               |-- task_003.py
|               `-- task_004.py
`-- generations/
    `-- model_001/
        `-- one_shot/
            `-- task_001/
                `-- <attempt_id>/
                    |-- request.md
                    |-- raw_response.txt
                    |-- extracted_solution.py
                    `-- generation.json
```

The three result categories have distinct purposes:

* `generations/` records how an answer was produced.
* `candidates/` contains clean Python files ready for evaluation.
* `runs/` records how candidates performed during evaluation.

`request.md` is the exact generated prompt. `raw_response.txt`
preserves the adapter response even when parsing fails.
`extracted_solution.py` is written only after successful parsing and
matches the corresponding clean candidate.

Every generation creates a fresh UUID attempt directory. Existing
attempts are never overwritten or deleted by the runner, including
failed attempts. Files created by earlier versions directly under the
task directory remain untouched.

`generation.json` records the attempt ID, task, requested model and
condition, adapter, adapter-reported model and condition when available,
artifact filenames, generation status, parse status, and any error. It
also records UTC start and completion timestamps, Python version and
implementation, and platform details. Each saved prompt, raw response,
and extracted candidate has a SHA-256 digest computed from its exact
UTF-8 file bytes. These hashes support integrity checks; they do not
prove the identity of the model or that the agent followed the protocol.
A failed parse remains a recorded generation but does not produce a
candidate. An adapter failure preserves the prompt and error, without
inventing a response or a response hash.

The clean `candidates/generated/<model>/<condition>/` directory remains
a task-keyed solution set compatible with the evaluator. It is a mutable
working copy: generating a task replaces that task's clean candidate,
or removes it if generation or parsing fails. Other task candidates are
unchanged. Keep attempt IDs with experimental results and copy preserved
`extracted_solution.py` files into a separate task-keyed solution set
when evaluating an earlier attempt. Do not select retries after seeing
hidden-test outcomes and report them as a one-shot result.

## Response parsing

The parser accepts either plain Python source or one Markdown code
block. A single fence is tolerated because models sometimes ignore the
output instruction.

The parser:

1. trims surrounding whitespace;
2. extracts a single fenced block when present;
3. rejects responses with multiple code blocks;
4. rejects empty responses;
5. compiles the extracted text to check Python syntax; and
6. emits the source with one trailing newline.

The parser never repairs or guesses at invalid output. Syntax errors
are part of agent performance, so the raw response and error are
recorded while no clean candidate is emitted. Regenerating a task also
removes a stale candidate at that task's output path before the new
response is parsed.

## Manual adapter

The manual adapter makes it possible to exercise the entire generation
pipeline without API credentials. Generate one task with:

```bash
python runner/generate_candidates.py \
  --agent manual \
  --model model_001 \
  --condition one_shot \
  --tasks task_001
```

The command prints the prompt. Paste that prompt into the model
interface of your choice, then paste the model's complete response
back into the terminal. End input with `Ctrl-D` on macOS/Linux or
`Ctrl-Z` followed by Enter on Windows.

Use `--tasks all` to process every task. The manual adapter will prompt
for one response at a time.

## Mock adapter

The mock adapter reads deterministic, task-keyed responses from a
directory. The directory must contain `task_001.py`, `task_002.py`, and
so on.

```bash
python runner/generate_candidates.py \
  --agent mock \
  --model mock-agent \
  --condition one_shot \
  --tasks all \
  --mock-solutions path/to/mock_solutions
```

This adapter is intended for testing artifact generation and parsing,
not for reporting model benchmark performance.

## Evaluate preserved candidates

Generation and evaluation remain separate commands:

```bash
python runner/run_benchmark.py \
  --solution-set results/candidates/generated/model_001/one_shot \
  --model model_001 \
  --condition one_shot
```

This design supports the reproducible workflow:

```text
generate once -> preserve exact outputs -> evaluate repeatedly
```

It also prevents generation code from accidentally exposing hidden
tests to an agent. Evaluation is the only phase that runs hidden tests.

## Adding an adapter

Every provider adapter must implement the common interface in
`agents/base.py`:

```python
from agents.base import AgentResponse, CodingAgent


class ExampleAgent(CodingAgent):
    def generate(self, prompt: str) -> AgentResponse:
        response_text = call_provider(prompt)
        return AgentResponse(
            text=response_text,
            model="example-model",
            condition="one_shot",
        )
```

Provider authentication, request formatting, retries, and response
decoding belong inside the adapter. The runner should depend only on
`CodingAgent.generate()`, so adding a provider does not couple the
benchmark pipeline to that provider's API.

`MockAgent.generate_for_task()` is a temporary task-aware helper for
deterministic fixtures. A future task-context interface can replace it
without changing the artifact or evaluation contracts.
