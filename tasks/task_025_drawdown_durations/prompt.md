# Task 025: Elapsed Drawdown Durations

Implement drawdown_durations(times, values), returning a list of elapsed
integer durations, one per observation. Track the running all-time
maximum value. At the first observation, output 0. Whenever a value
equals or exceeds the running maximum, the series is recovered: output
0 and reset the most recent recovered-peak timestamp to that observation.

At any value strictly below the running maximum, output current
timestamp minus the most recent recovered-peak timestamp. A local rise
that remains below the all-time high does not reset the clock. Equal peaks do reset it. Use elapsed time, not a count of rows. Equality means
ordinary exact numeric comparison; do not add a tolerance.

Inputs are Python lists or tuples of equal length. times must be strictly increasing Python ints excluding bool; negative timestamps are allowed.
values must be positive finite Python ints or floats excluding bool.
Raise ValueError for unequal lengths, invalid timestamp types, repeated
or decreasing times, or nonnumeric/nonfinite/nonpositive values.
Empty valid inputs return []. Do not mutate inputs.

Example: times=[0, 2, 7, 8, 10], values=[10, 8, 9, 10, 7] returns
[0, 2, 7, 0, 2]. The recovery at time 8 resets the clock.
