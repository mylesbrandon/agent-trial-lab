# Task 010: Merge Streaming Variance Summaries

Implement `merge_moments(left, right)` in `starter.py`.

Each input is a tuple (count, mean, m2), where m2 is the sum of squared
 deviations from that group's mean. Return a tuple of the same form for the
union. count must be a nonnegative Python int excluding bool; mean and m2
must be finite int/float excluding bool, and m2 must be nonnegative. An empty
group must be exactly (0, 0, 0). Raise ValueError for invalid summaries,
including tuples of the wrong length. Do not mutate the inputs.
For nonempty groups use the parallel variance rule:
  delta = mean_b - mean_a
  count = count_a + count_b
  mean = mean_a + delta * count_b / count
  m2 = m2_a + m2_b + delta**2 * count_a * count_b / count
Merging an empty group returns the other summary, and two empty groups return
(0, 0.0, 0.0). This is an unnormalized moment, not sample variance or population
variance. Inputs in valid evaluations have representable intermediate
arithmetic and counts no larger than 1,000,000. Relative/absolute tolerance
is 1e-10.

Integers outside the finite float range raise ValueError.
