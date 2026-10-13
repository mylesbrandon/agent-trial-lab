# Task 020: Duration-weighted Causal Means

Implement time_weighted_mean(times, values, queries, window), returning a
list of means, one per query in its original order. Each observation
becomes effective at its timestamp and remains constant until the next
observation. The last value remains effective indefinitely. There is no
known value before the first observation.

For each query q, integrate that piecewise constant signal over the
half-open interval [q - window, q). Divide by the duration with a known
value, not by the number of samples or by an uncovered part of the window.
Return None if there is no positive covered duration. An observation
exactly at q contributes zero duration and must not affect the result.
Queries may be unordered and repeated. Empty observations give None for
every query.

All sequences are lists or tuples. Observation times must be strictly increasing Python ints excluding bool. Queries must also be Python ints
excluding bool; negative timestamps are valid. window must be a positive
Python int excluding bool. times and values must have equal length.
Values must be finite Python ints or floats excluding bool; None, NaN,
infinity, and nonnumeric values are invalid. Raise ValueError for every
stated validation failure, even when queries is empty. Do not mutate inputs.

For this task, the absolute value of every observation timestamp, query
timestamp, and numeric value must be <= 10**12, and window must be
<= 10**12. Raise ValueError outside these supported magnitude bounds.

Example: observations times=[0, 2], values=[10, 20], query=5, window=5
have mean (10*2 + 20*3)/5 = 16. A query of 1 with window=5 gives 10,
because only the known duration [0, 1) is included in the denominator.
