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
