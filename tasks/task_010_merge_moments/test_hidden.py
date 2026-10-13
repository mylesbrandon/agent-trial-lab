import math
import pytest
from starter import merge_moments

def test_empty_group_identity():
    value = (3, -2.0, 8.0)
    assert merge_moments((0, 0, 0), value) == value
    assert merge_moments(value, (0, 0, 0)) == value
    assert merge_moments((0, 0, 0), (0, 0, 0)) == (0, 0, 0)

def test_large_offset_small_variance():
    assert merge_moments((2, 1e9 + 1, 2), (2, 1e9 + 5, 2)) == _approx((4, 1e9 + 3, 20))

def test_associative_partition_example():
    a, b, c = (2, 2, 2), (1, 5, 0), (1, 7, 0)
    expected = (4, 4, 20)
    assert merge_moments(merge_moments(a, b), c) == _approx(expected)
    assert merge_moments(a, merge_moments(b, c)) == _approx(expected)

def test_invalid_counts():
    for n in (-1, 1.5, True):
        with pytest.raises(ValueError):
            merge_moments((n, 0, 0), (1, 0, 0))

def test_invalid_moments():
    for value in ((1, math.nan, 0), (1, 0, math.inf), (1, 0, -1), (0, 1, 0), (0, 0, 1), (1, True, 0)):
        with pytest.raises(ValueError):
            merge_moments(value, (1, 0, 0))

def test_malformed_summary():
    for bad in ((1, 2), (1, 2, 3, 4), [1, 2, 3]):
        with pytest.raises(ValueError):
            merge_moments(bad, (1, 0, 0))

def test_commutative_merge():
    a, b = (3, -2, 6), (2, 5, 2)
    assert merge_moments(a, b) == _approx(merge_moments(b, a))


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        merge_moments((1, 10**1000, 0), (1, 0, 0))


def _approx(value, *, rel=1e-10, abs=1e-10):
    return pytest.approx(value, rel=rel, abs=abs)


def test_cancelling_integer_means_preserve_half_unit():
    count, mean, m2 = merge_moments((1, 10**20 + 1, 0), (1, -10**20, 0))
    assert count == 2
    assert mean == _approx(0.5)
    assert m2 == _approx(2e40)
