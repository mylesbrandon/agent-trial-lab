# Code Reliability Bench development notes

## October 12, 2026 expansion

The project was cloned from mylesbrandon/CodeAgentBench with its history intact
and renamed Code Reliability Bench. The original four tasks and frozen pilot were
retained. Twenty-eight additional contracts bring each category to eight tasks.

Development used AI assistance for implementation, test design, documentation,
and separate agent review. Numerical tasks, graph tasks, temporal tasks, and CSV
tasks were developed separately and checked with their references and deliberate
faults. The report records observed results; human review is still recommended
before making research conclusions or presenting design choices as personally
validated.

The runner previously copied a task's reference solution beside the candidate,
and considered process exit zero sufficient for a pass. Controlled reproductions
showed both a reference import and os._exit(0) could produce false passes. The
new runner isolates suite copies and requires structured executed-test evidence.
Regression tests also cover timeouts, environment contamination, skipped suites,
source mutation, and preserved artifact hashes.

Normal candidate generation previously reused and overwrote deterministic output
paths. Attempts now have unique directories, timestamps, and exact-byte hashes.
The latest clean candidate set remains convenient for batch evaluation while
prior evidence survives retries and parse failures.

An audit corrected inaccurate historical prose about which deliberate defects
passed public tests and which hidden tests failed. See reports/baseline-audit.md.
The underlying old results and pilot files were not rewritten. README now states
that Pilot 001's captured responses were syntactically invalid and cannot measure
behavioral coding performance.

The project now has an MIT license, a small UTF-8 hash-locked dependency set,
a repeatable quality command, and CI across three operating systems and two
Python versions. The current measured corpus totals and checks are recorded in
reports/quality.md and reports/quality.json.

## Next research work

Conduct a human contract review, add an independent reference oracle where
possible, and run a preregistered visible-only generation experiment. Preserve
all attempts and distinguish capture failures from behavioral failures. Add
secure execution isolation before accepting unknown submissions. Any adoption
or model-performance claim requires new evidence beyond this release.
