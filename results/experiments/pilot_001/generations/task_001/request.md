You are solving a Python code-repair benchmark task.

Follow the written specification exactly.

Return only the complete contents of starter.py after your repair.
Do not include Markdown fences, explanations, tests, or commentary.

TASK SPECIFICATION
------------------
# Task 001: Rolling Z-Score

Implement `rolling_zscore(values, window)`.

The function takes a list of numbers and a positive integer `window`.

For each index `i`, compute the z-score of `values[i]` relative to the rolling window ending at `i`:

```python
values[max(0, i - window + 1): i + 1]
```

## Required Behavior

* `window` must be a positive integer. Raise `ValueError` when
  `window <= 0`.
* Ignore `NaN` values when calculating the window mean and standard
  deviation.
* If the current value is `NaN`, return `NaN` at that position.
* If a window contains no valid values, return `NaN` at that
  position.
* Use population standard deviation, dividing the variance by `n`.
* If the population standard deviation is zero, return `0.0` at that
  position.
* Return one result for every input value.


STARTER CODE
------------
import math

def rolling_zscore(values, window):
    """
    Compute rolling z-scores for a list of numeric values.

    Args:
        values: list of numbers, possibly including float("nan")
        window: positive integer window size

    Returns:
        list of floats

    Rules:
        - Raise ValueError if window <= 0.
        - For each index i, use values[max(0, i - window + 1): i + 1].
        - Ignore NaN values when computing the window mean and standard deviation.
        - If the current value is NaN, return NaN for that position.
        - If there are no valid non-NaN values in the window, return NaN for that position.
        - Use population standard deviation, dividing variance by n, not n - 1.
        - If the window standard deviation is 0, return 0.0 for that position.
    """
    pass

PUBLIC TESTS
------------
import math
from starter import rolling_zscore
import pytest

def test_invalid_window():
    with pytest.raises(ValueError):
        rolling_zscore([1, 2, 3], 0)

def almost_equal(a, b, tol=1e-6):
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < tol

def test_basic_increasing_sequence():
    result = rolling_zscore([1, 2, 3], 2)
    assert len(result) == 3
    assert almost_equal(result[0], 0.0)
    assert almost_equal(result[1], 1.0)
    assert almost_equal(result[2], 1.0)

def test_window_size_three():
    result = rolling_zscore([1, 2, 3, 4], 3)

    assert len(result) == 4
    assert almost_equal(result[0], 0.0)

