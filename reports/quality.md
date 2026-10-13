# Measured corpus quality

Verified locally on October 12, 2026. These are harness and corpus validation results, not model-performance scores.

| Area | Tasks | Public tests | Hidden tests |
|---|---:|---:|---:|
| Graph algorithms | 8 | 26 | 63 |
| CSV parsing | 8 | 25 | 60 |
| Numerical robustness | 8 | 24 | 72 |
| Time-series alignment | 8 | 34 | 69 |
| **Total** | **32** | **109** | **264** |

**373 executed reference tests**, excluding infrastructure tests and repeated baseline runs.

- 32/32 reference implementations pass both suites.
- 32/32 flawed starters are rejected.
- 39/39 deliberate defect fixtures fail behavioral hidden tests.
- 0 task-validation errors; 0 warnings.
- The separate infrastructure suite passes 73 cases, including scoring-integrity regressions and deterministic numerical oracle comparisons.

## Reproduce

```bash
python -m pytest -q
python runner/check_quality.py --report-path work/quality.json
```

Local environment: Python 3.14.6, pytest 9.1.1, macOS-26.6.2-arm64-arm-64bit-Mach-O.

The [JSON evidence](quality.json) records per-task validation, exact failed test names for each deliberate defect, thresholds, runtime, and the corpus fingerprint. The command returns a failing exit code if the 32-task / 200-test minimum or another quality check is not met.

Corpus SHA-256:

```text
867a01e71d7930dd7edb966d629e86bfcf7f9126458735835324114b4a03d4a5
```

## Interpretation

Detecting these known faults supports the specific test cases, not a general defect-detection rate. Reference correctness is checked through tests, additional numerical oracles, and agent review, not a formal proof or independent human certification. The published corpus is small and function-focused; it does not establish model rankings, real-world agent reliability, or contamination resistance.

Pilot 001 has zero syntax-valid captured candidates; no behavioral model-performance claim follows from its 0/4 result. See the [methodology](../docs/methodology.md) for generation and execution boundaries.
