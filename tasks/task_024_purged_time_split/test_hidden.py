import pytest
from starter import purged_time_split


def test_pretest_start_with_overlapping_label_is_purged():
    assert purged_time_split([(-10, 5), (3, 4), (8, 9)], 3, 6) == ([2], [1])


def test_selected_test_labels_extend_protected_interval():
    intervals = [(3, 10), (6, 7), (10, 11), (12, 13)]
    assert purged_time_split(intervals, 3, 5, embargo=2) == ([3], [0])


def test_touching_protected_endpoints_are_allowed():
    assert purged_time_split([(0, 3), (3, 6), (7, 9)], 3, 5, embargo=1) == ([0, 2], [1])


def test_no_selected_test_samples_still_apply_protection():
    assert purged_time_split([(0, 8), (5, 6), (7, 8)], 2, 4, embargo=2) == ([2], [])


def test_unsorted_input_preserves_original_indices():
    intervals = [(9, 10), (3, 4), (-4, -2), (2, 8), (1, 2)]
    assert purged_time_split(intervals, 2, 5) == ([0, 2, 4], [1, 3])


def test_malformed_or_invalid_intervals_raise():
    for interval in [(1,), (1, 2, 3), "12", None, (1, 1), (3, 2), (True, 2), (0, 1.5)]:
        with pytest.raises(ValueError):
            purged_time_split([interval], 4, 5)


def test_invalid_bounds_or_embargo_types_raise():
    for start, end, embargo in [(True, 3, 0), (0, 2.5, 0), (0, 2, True),
                                (0, 2, -1), (3, 2, 0), (0, 2, 0.5)]:
        with pytest.raises(ValueError):
            purged_time_split([], start, end, embargo)


def test_negative_times_tuple_input_and_no_mutation():
    intervals = [[-5, -3], [-3, -1], [0, 1]]
    assert purged_time_split(intervals, -3, -1, embargo=1) == ([0, 2], [1])
    assert intervals == [[-5, -3], [-3, -1], [0, 1]]
    assert purged_time_split(tuple(map(tuple, intervals)), -3, -1, 1) == ([0, 2], [1])


def test_invalid_interval_container():
    for invalid in (None, {}, "", iter([])):
        with pytest.raises(ValueError):
            purged_time_split(invalid, 1, 2)
