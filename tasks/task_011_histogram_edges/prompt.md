# Task 011: Precise Histogram Edge Assignment

Implement `histogram_counts(values, edges)` in `starter.py`.

Return one integer count per bin for a list/tuple of values and a list/tuple
of at least two finite, strictly increasing bin edges. Values and edges must
be finite Python int/float excluding bool; invalid values, invalid edges, or
fewer than two edges raise ValueError. Do not mutate either input.
Every bin includes its left edge and excludes its right edge, except the
last bin also includes the final edge. Values outside the full edge range
are ignored. Repeated samples count separately. Empty values produce zeros
for all bins. Edge comparisons are exact; do not apply tolerances or round
samples before assigning bins.

Integers outside the finite float range raise ValueError.
