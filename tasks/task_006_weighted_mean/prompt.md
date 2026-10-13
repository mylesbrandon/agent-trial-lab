# Task 006: Scale-Safe Weighted Mean

Implement `weighted_mean(values, weights)` in `starter.py`.

Return the weighted arithmetic mean of equally sized lists or tuples values
and weights. Every entry must be a finite Python int/float representable as a
float; booleans are invalid. Weights must be nonnegative with at least one
positive weight. Empty inputs, unequal lengths, invalid entries, negative
weights, or all-zero weights raise ValueError. Zero-weight entries contribute
nothing but their values must still be valid. Do not mutate either input.
Avoid overflow from summing large weights or multiplying large values by
weights when the mean is representable. Answers are checked to relative
1e-12 / absolute 1e-12 tolerance. Values whose magnitude or weight ratios
underflow to zero may make a negligible zero contribution.

Integers outside the finite float range raise ValueError.
