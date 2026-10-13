import pytest
from starter import stable_softmax

def test_equal_scores():
    assert stable_softmax([2, 2]) == _approx([0.5, 0.5])

def test_ordinary_scores():
    assert stable_softmax([0, 1]) == _approx([0.2689414213699951, 0.7310585786300049])

def test_empty_scores():
    assert stable_softmax([]) == []


def _approx(value, *, rel=1e-12, abs=1e-15):
    return pytest.approx(value, rel=rel, abs=abs)
