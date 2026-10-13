import math
import pytest
from starter import histogram_counts

def test_all_boundary_values():
    assert histogram_counts([0, 1, 2, 3], [0, 1, 2, 3]) == [1, 1, 2]

def test_repeated_final_edge():
    assert histogram_counts([2, 2, 2], [0, 1, 2]) == [0, 3]

def test_nonuniform_negative_bins():
    assert histogram_counts([-5, -4, -1, 0, 10], [-5, -1, 10]) == [2, 3]

def test_adjacent_float_boundaries():
    below = math.nextafter(1.0, 0.0)
    above = math.nextafter(1.0, 2.0)
    assert histogram_counts([below, 1, above], [0, 1, 2]) == [1, 2]

def test_invalid_edges():
    for edges in ([], [1], [0, 0], [2, 1], [0, math.inf], [False, 1]):
        with pytest.raises(ValueError):
            histogram_counts([], edges)

def test_invalid_samples():
    for bad in (math.nan, math.inf, True, '0.5'):
        with pytest.raises(ValueError):
            histogram_counts([bad], [0, 1])

def test_tuple_and_input_preservation():
    assert histogram_counts((0, 1), (0, 1)) == [2]
    values, edges = [2, 0, 1], [0, 1, 2]
    histogram_counts(values, edges)
    assert values == [2, 0, 1] and edges == [0, 1, 2]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        histogram_counts([10**1000], [0, 1])
