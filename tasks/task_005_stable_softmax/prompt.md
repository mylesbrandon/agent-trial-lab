# Task 005: Stable Softmax with Infinite Scores

Implement `stable_softmax(scores)` in `starter.py`.

Return a list of softmax probabilities for a list or tuple of Python int/float
scores. Booleans, nonnumbers, and NaN raise ValueError. Infinite scores are
allowed: if any scores are positive infinity, divide probability equally among
those entries and give every other entry zero. If all scores are negative
infinity, return a uniform distribution. An empty input returns [].
Otherwise compute exp(x - max(scores)) normalized by their sum; negative
infinity contributes zero. Avoid overflow for large finite scores. Outputs
must agree within relative tolerance 1e-12 or absolute tolerance 1e-15.
Do not mutate the input.

Integers outside the finite float range raise ValueError.
