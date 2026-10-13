from starter import histogram_counts

def test_interior_samples():
    assert histogram_counts([0.2, 0.5, 1.1], [0, 1, 2]) == [2, 1]

def test_ignored_outside_samples():
    assert histogram_counts([-10, 0.5, 10], [0, 1]) == [1]

def test_empty_samples():
    assert histogram_counts([], [0, 1, 2]) == [0, 0]
