# Original-corpus controlled baseline audit

Audit date: October 12, 2026. Scope: Tasks 001–004 as checked out from GitHub.
This report does not include subsequently added tasks.

The audit used Python 3.14.6 and pytest 9.1.1 on macOS arm64. Task, candidate,
and frozen experiment files were unchanged.

| Task | Public cases | Hidden cases | Reference passed | Defects detected by hidden tests | Defects passing public tests |
|---|---:|---:|---:|---:|---:|
| 001 | 3 | 8 | 11/11 | 3/3 | 2/3 |
| 002 | 5 | 8 | 13/13 | 2/2 | 2/2 |
| 003 | 6 | 10 | 16/16 | 3/3 | 3/3 |
| 004 | 4 | 10 | 14/14 | 3/3 | 2/3 |
| **Total** | **18** | **36** | **54/54** | **11/11** | **9/11** |

Fifteen implementations, including four references, were evaluated in two
suites each: 30 suite runs and 203 test invocations. The corpus contains 54
distinct test cases; repeated execution does not increase corpus size.

Task 001's full-history baseline fails one public test, contradicting the
old claim that all three defects passed publicly. Its no-NaN baseline fails
one hidden test, not the three previously named. The corrected
[failure analysis](../results/failure_analysis.md) records exact failed names
and adds Task 004 results. Tests were not weakened to match old claims.

## Reproduce

With the repository Python environment active, run from the repository root:

```bash
python -B - <<'PYCODE'
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path.cwd()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
           PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
for number in range(1, 5):
    task_id = f"task_{number:03d}"
    group = root / "results/baselines" / task_id
    task = next((root / "tasks").glob(task_id + "_*"))
    for candidate in sorted(group.glob("*.py")):
        for suite in ("public", "hidden"):
            with tempfile.TemporaryDirectory() as directory:
                scratch = Path(directory)
                shutil.copyfile(candidate, scratch / "starter.py")
                filename = f"test_{suite}.py"
                shutil.copyfile(task / filename, scratch / filename)
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "-p",
                     "no:cacheprovider", filename],
                    cwd=scratch, env=env, capture_output=True,
                    text=True, timeout=30, check=False,
                )
                print(task_id, candidate.name, suite,
                      f"exit={result.returncode}")
                print(result.stdout, end="")
                print(result.stderr, end="")
PYCODE
```

Each suite receives a fresh temporary directory containing only the trusted
baseline as `starter.py` and that suite. This avoids cross-suite filesystem
state but is not a security sandbox. Exit 1 is expected for defective
baselines. References must exit 0. Collection errors or timeouts need
investigation and must not count as behavioral detections; none occurred.

## Evidence limits

These known fixtures do not establish general bug-detection coverage or
coding-agent accuracy. Published test files are "hidden" only in the sense
of being withheld from a generation prompt; they are not secret or known to
be absent from training data.

The preserved Pilot 001 contains no syntax-valid candidates. Manual capture
cannot establish whether formatting damage originated with the model or
copying. Its 0/4 result does not measure the intended behavioral capabilities.

The older single-task `model_001` result has a different schema and lacks a
preserved raw generation response. Its analysis and result record also give
different dates (July 15 versus July 17, 2026). Treat it as a historical record
with limited provenance, not a reproducible comparison with Pilot 001.

Future model comparisons need preserved original responses, explicit attempt
counts and stopping rules, versioned task/test inputs, and repeated independent
trials. Keep those observations separate from controlled validation fixtures.
