# Task 019: Backward As-of Alignment

Implement backward_asof(query_times, observation_times, values,
max_age=None, allow_exact=True). Return one selected value per query
timestamp, preserving query order. Query timestamps may be unordered or
repeated. Observation timestamps must be nondecreasing; repeated
observations are allowed and the last eligible duplicate wins.

With allow_exact=True, select the latest observation with timestamp <=
the query. With allow_exact=False, require timestamp < the query; all
observations at the query timestamp are ineligible. Never select a future
observation. If no observation qualifies, return None for that query.

max_age is None (unbounded) or a nonnegative integer. A selected observation
is usable only when query minus observation timestamp <= max_age; the
staleness boundary is inclusive. A stale observation produces None.

All sequences are Python lists or tuples. Timestamps must be Python ints
excluding bool, and may be negative. Observation times and values must
have equal length. Values may be any Python objects, including None.
allow_exact must be bool. Raise ValueError for invalid timestamp types,
decreasing observation times, mismatched lengths, invalid max_age, or
invalid allow_exact. Validate inputs even when there are no queries.
Do not mutate any input. Empty observations yield None for every query.

Example: backward_asof([5, 1, 4], [2, 4, 4], ["a", "b", "c"])
returns ["c", None, "c"]. With allow_exact=False, query 4 returns "a".
