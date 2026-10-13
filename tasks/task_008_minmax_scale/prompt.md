# Task 008: Range Normalization Without Overflow

Implement `minmax_scale(values)` in `starter.py`.

Map a list or tuple of finite Python int/float values to [0, 1] using
(x - minimum) / (maximum - minimum). Return a new list, preserving order.
Empty input returns []; a constant sequence maps to all zeros. Booleans,
nonnumbers, NaN, and infinity raise ValueError. Do not mutate the input.
Compute robustly even if maximum - minimum would overflow, and preserve
small differences between nearby values. Answers use relative 1e-12 or
absolute 1e-12 tolerance.

Integers outside the finite float range raise ValueError.
