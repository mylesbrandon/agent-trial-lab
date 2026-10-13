# Task 007: Interpolated Quantiles

Implement `linear_quantile(values, q)` in `starter.py`.

For a nonempty list or tuple of finite Python int/float values, return the
linearly interpolated quantile q. Booleans and nonnumbers are invalid; q must
be finite and in [0, 1]. Empty values or invalid values/q raise ValueError.
Sort a copy, set h = (n - 1) * q, and interpolate between the floor and ceiling
indices of h. Endpoints select the minimum and maximum. Singletons return
their only value for every valid q. Do not mutate the input. Avoid overflow
from subtracting opposite-sign values near float limits; the convex
combination is representable. Tolerance: relative 1e-12 or absolute 1e-12.

Integers outside the finite float range raise ValueError.
