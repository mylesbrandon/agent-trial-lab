import pytest
from starter import time_weighted_mean


def test_partial_coverage_uses_only_known_duration():
    assert time_weighted_mean([10], [6], [11, 12], 5) == pytest.approx([6, 6])


def test_observation_at_query_has_zero_weight():
    assert time_weighted_mean([0, 5], [2, 1000], [5], 5) == pytest.approx([2])


def test_left_boundary_clips_previous_segment():
    assert time_weighted_mean([0, 3, 8], [2, 10, 99], [6], 4) == pytest.approx([8])


def test_last_observation_persists_without_future_data():
    assert time_weighted_mean([0, 2], [10, 4], [100], 7) == pytest.approx([4])


def test_query_order_negative_times_and_repetition():
    assert time_weighted_mean([-5, -1], [2, 10], [1, -3, 1], 4) == pytest.approx([6, 2, 6])


def test_invalid_observations_even_without_queries():
    for times, values in [([0, 0], [1, 2]), ([2, 1], [1, 2]),
                          ([True], [1]), ([0], []), ([0], [None]),
                          ([0], [float("nan")]), ([0], [float("inf")]),
                          ([0], [False]), ([0], ["1"])]:
        with pytest.raises(ValueError):
            time_weighted_mean(times, values, [], 3)


def test_invalid_query_and_window_types():
    for queries, window in [([1.0], 2), ([False], 2), ([2], -1), ([2], True), ([2], 1.5)]:
        with pytest.raises(ValueError):
            time_weighted_mean([0], [1], queries, window)


def test_inputs_are_unchanged_and_tuple_sequences_work():
    times, values, queries = [0, 3], [-2, 4], [6, 1]
    assert time_weighted_mean(times, values, queries, 3) == pytest.approx([4, -2])
    assert (times, values, queries) == ([0, 3], [-2, 4], [6, 1])
    assert time_weighted_mean((0, 3), (-2, 4), (6,), 3) == pytest.approx([4])


def test_supported_magnitude_bounds_are_inclusive():
    bound = 10**12
    assert time_weighted_mean([-bound, 0], [-bound, bound], [bound], bound) == pytest.approx([bound])
    for times, values, queries, window in [
        ([0], [10**400], [1], 1),
        ([0], [-bound - 1], [1], 1),
        ([bound + 1], [1], [0], 1),
        ([0], [1], [-bound - 1], 1),
        ([0], [1], [1], bound + 1),
    ]:
        with pytest.raises(ValueError):
            time_weighted_mean(times, values, queries, window)
