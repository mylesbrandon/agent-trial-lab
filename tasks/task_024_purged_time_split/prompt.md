# Task 024: Purged Temporal Train/Test Split

Implement purged_time_split(intervals, test_start, test_end, embargo=0).
Each sample has an information-exposure interval [start, end), including
start and excluding end. Return (train_indices, test_indices), two lists
of zero-based original indices in input order. Inputs need not be sorted.

A sample is in the test set exactly when its start is in
[test_start, test_end). Compute protected_end as the maximum of test_end
and every selected test sample's end, then add embargo. The protected
interval is [test_start, protected_end), including any test label that
extends beyond test_end plus the post-test embargo.

A non-test sample can be in training only if its entire exposure interval
is disjoint from the protected interval: end <= test_start or
start >= protected_end. Other samples are purged and appear in neither
output. Touching half-open endpoints do not overlap. Apply the protected
interval even if no samples were selected for testing.

intervals is a Python list or tuple of two-element lists or tuples.
Each endpoint, test_start, test_end and embargo must be a Python int,
excluding bool; timestamps can be negative. Every sample must have
start < end, test_start must be < test_end, and embargo must be >= 0.
Raise ValueError for invalid types, malformed interval pairs, invalid
bounds, or negative embargo, including on empty input. Do not mutate
inputs. Valid empty intervals return ([], []).

Example: intervals=[(0, 2), (1, 4), (3, 5), (5, 6), (6, 7)],
test_start=3, test_end=5, embargo=1 returns ([0, 4], [2]).
Sample 1 overlaps the test window; sample 3 falls inside the embargo.
