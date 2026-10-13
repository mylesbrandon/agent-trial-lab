import pytest
from starter import backward_asof


def test_basic_backward_alignment():
    assert backward_asof([2, 5, 9], [1, 4, 8], ["a", "b", "c"]) == ["a", "b", "c"]


def test_empty_observations_and_queries():
    assert backward_asof([1, 2], [], []) == [None, None]
    assert backward_asof([], [], []) == []


def test_query_order_and_duplicate_observations():
    assert backward_asof([5, 1, 4], [2, 4, 4], ["a", "b", "c"]) == ["c", None, "c"]


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        backward_asof([2], [1], [])
