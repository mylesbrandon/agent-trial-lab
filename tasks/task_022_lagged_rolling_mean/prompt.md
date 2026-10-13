# Task 022: Lagged Rolling Means with Missing Observations

Implement lagged_rolling_mean(values, window, min_periods=1). At index i,
use only values[max(0, i - window):i], excluding the current observation.
window counts rows, not the number of nonmissing observations; do not
extend a window to replace missing data. Ignore None within the window.

Return the arithmetic mean of the nonmissing observations when at least
min_periods are present; otherwise return None. The first output is
always None. Zero is an ordinary observation, not missing. Return a list
with the same length as values. Empty valid input returns [].

values is a Python list or tuple containing None or finite Python ints
or floats excluding bool. NaN, infinity, strings and bool are invalid.
window must be a positive Python int excluding bool; min_periods must
be a Python int excluding bool between 1 and window inclusive.
Raise ValueError on all invalid values or parameters, even when values
is empty. Do not mutate the input. Numeric values must also have absolute value
<= 10**12; raise ValueError outside this supported magnitude bound.

Example: lagged_rolling_mean([10, 20, 30, 40], 2) returns
[None, 10.0, 15.0, 25.0]. lagged_rolling_mean([None, 8, None, 4], 2)
returns [None, None, 8.0, 8.0].
