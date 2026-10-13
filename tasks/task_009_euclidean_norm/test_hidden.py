import math
import pytest
from starter import euclidean_norm

def test_large_representable_norm():
    assert euclidean_norm([3e200, 4e200]) == _approx(5e200)

def test_small_representable_norm():
    assert euclidean_norm([3e-200, 4e-200]) == _approx(5e-200, rel=1e-12, abs=0)

def test_subnormal_singleton():
    smallest = math.ulp(0.0)
    assert euclidean_norm([-smallest]) == smallest

def test_all_zeros():
    assert euclidean_norm([0, -0.0, 0]) == 0

def test_invalid_numbers():
    for bad in (math.inf, -math.inf, math.nan):
        with pytest.raises(ValueError):
            euclidean_norm([1, bad])

def test_invalid_types():
    for bad in (True, '3', None):
        with pytest.raises(ValueError):
            euclidean_norm([bad])

def test_tuple_and_preserved_input():
    assert euclidean_norm((5, 12)) == _approx(13)
    values = [12, 5]
    euclidean_norm(values)
    assert values == [12, 5]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        euclidean_norm([10**1000])


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)
