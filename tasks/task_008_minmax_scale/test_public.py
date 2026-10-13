import pytest
from starter import minmax_scale

def test_ordinary_range():
    assert minmax_scale([2, 4, 6]) == _approx([0, 0.5, 1])

def test_unsorted_values():
    assert minmax_scale([8, 0, 2]) == _approx([1, 0, 0.25])

def test_negative_range():
    assert minmax_scale([-4, -2, 0]) == _approx([0, 0.5, 1])


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)
