import pytest
from starter import purged_time_split


def test_purge_overlap_and_post_test_embargo():
    intervals = [(0, 2), (1, 4), (3, 5), (5, 6), (6, 7)]
    assert purged_time_split(intervals, 3, 5, embargo=1) == ([0, 4], [2])


def test_half_open_test_selection():
    assert purged_time_split([(0, 1), (1, 2), (2, 3)], 1, 2) == ([0, 2], [1])


def test_empty_intervals():
    assert purged_time_split([], 1, 2) == ([], [])


def test_invalid_split_bounds_raise():
    with pytest.raises(ValueError):
        purged_time_split([], 2, 2)
