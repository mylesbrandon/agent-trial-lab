# Task 009: Overflow-Safe Euclidean Norm

Implement `euclidean_norm(values)` in `starter.py`.

Return sqrt(sum(x*x)) for a list or tuple of finite Python int/float values.
An empty input returns 0.0. Reject booleans, nonnumbers, NaN, and infinities
with ValueError. Do not mutate the input. Avoid premature overflow from
squaring and underflow that discards a representable nonzero norm. If the
true norm itself exceeds the float range, positive infinity is allowed.
Accuracy is checked with relative tolerance 1e-12; small nonzero results are
also checked with zero absolute tolerance.

Integers outside the finite float range raise ValueError.
