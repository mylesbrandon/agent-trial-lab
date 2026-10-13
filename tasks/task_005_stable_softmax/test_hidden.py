import math
import pytest
from starter import stable_softmax

def test_large_positive_scores():
    assert stable_softmax([1000, 1000]) == _approx([0.5, 0.5])

def test_large_negative_scores():
    assert stable_softmax([-1000, -1001]) == _approx([0.7310585786300049, 0.2689414213699951])

def test_positive_infinity_mass():
    assert stable_softmax([math.inf, 5, math.inf, -math.inf]) == [0.5, 0, 0.5, 0]

def test_all_negative_infinities():
    assert stable_softmax([-math.inf] * 4) == [0.25] * 4

def test_negative_infinity_and_finite():
    assert stable_softmax([-math.inf, -3]) == [0, 1]

def test_invalid_scores():
    for bad in (True, '1', None, math.nan):
        with pytest.raises(ValueError):
            stable_softmax([1, bad])

def test_shift_invariance_and_input_preservation():
    scores = [-3, 0, 2]
    assert stable_softmax(scores) == _approx(stable_softmax([997, 1000, 1002]))
    assert scores == [-3, 0, 2]

def test_tuple_and_singleton():
    assert stable_softmax((-10000,)) == [1.0]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        stable_softmax([10**1000])


def _approx(value, *, rel=1e-12, abs=1e-15):
    return pytest.approx(value, rel=rel, abs=abs)


def test_large_integer_differences_are_preserved():
    base = 10**20
    assert stable_softmax([base, base + 1]) == _approx([0.2689414213699951, 0.7310585786300049])
    assert stable_softmax([float(base), base + 1]) == _approx([0.2689414213699951, 0.7310585786300049])
