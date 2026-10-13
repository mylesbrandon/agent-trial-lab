# Task 023: Forward Fill with Observation Age Limits

Implement bounded_forward_fill(times, values, max_gap). Return a new list
with one value per timestamp. Keep every originally observed non-None
value. For a missing value (None), use the latest earlier original observation only when its elapsed age is <= max_gap; otherwise keep None.
The boundary is inclusive. Never use a future value and never replace a
valid observed zero.

Filled rows do not refresh the observation timestamp. Staleness always
measures time since the last original non-None value, not time since the
last filled row. Leading missing values remain None; a fresh observation
becomes the new source even after earlier rows have become stale.

Inputs are Python lists or tuples of equal length. times must be strictly increasing Python ints excluding bool; negative timestamps are allowed.
values may be None or finite Python ints or floats excluding bool. NaN,
infinity, strings and bool are invalid. max_gap must be a nonnegative
Python int excluding bool. Raise ValueError for invalid values, timestamps,
ordering, lengths, or max_gap, including invalid parameters on empty input.
Do not mutate inputs. Empty valid inputs return [].

Example: times=[0, 2, 4, 6], values=[7, None, None, None], max_gap=4
returns [7, 7, 7, None].
