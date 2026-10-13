import math
import pytest
from starter import minmax_scale

def test_range_would_overflow():
    assert minmax_scale([-1e308, 0, 1e308]) == _approx([0, 0.5, 1])

def test_constant_and_singleton():
    assert minmax_scale([3, 3]) == [0, 0]
    assert minmax_scale((1,)) == [0]

def test_empty_input():
    assert minmax_scale([]) == []

def test_tiny_values():
    assert minmax_scale([0, 1e-300, 2e-300]) == _approx([0, 0.5, 1])

def test_large_offset_small_span():
    assert minmax_scale([1e15, 1e15 + 1, 1e15 + 2]) == _approx([0, 0.5, 1])

def test_invalid_entries():
    for bad in (True, math.nan, math.inf, '2', None):
        with pytest.raises(ValueError):
            minmax_scale([0, bad])

def test_preserves_input():
    values = [3, 1, 2]
    minmax_scale(values)
    assert values == [3, 1, 2]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        minmax_scale([0, 10**1000])


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)


def test_adjacent_large_integer_values():
    base = 10**20
    assert minmax_scale([base, base + 1, base + 2]) == _approx([0, 0.5, 1])
    assert minmax_scale([float(base), base + 1]) == [0, 1]
