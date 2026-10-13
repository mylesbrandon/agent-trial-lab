import pytest
from starter import backward_asof


def test_strict_alignment_excludes_all_exact_duplicates():
    assert backward_asof([4, 5], [2, 4, 4], [10, 20, 30], allow_exact=False) == [10, 30]


def test_nearest_future_observation_is_never_selected():
    assert backward_asof([0, 99], [1, 100], ["old", "future"]) == [None, "old"]


def test_staleness_boundary_is_inclusive():
    assert backward_asof([13, 14], [10], [7], max_age=3) == [7, None]


def test_zero_age_and_strict_selection():
    assert backward_asof([3, 4], [3], [0], max_age=0) == [0, None]
    assert backward_asof([3], [3], [0], max_age=0, allow_exact=False) == [None]


def test_negative_times_and_none_values():
    assert backward_asof([-6, -4, -1], [-5, -2], [None, "x"]) == [None, None, "x"]


def test_validation_is_not_skipped_for_empty_queries():
    for times, values in [([2, 1], [0, 0]), ([True], [0]), ([1.0], [0]), ([1], [])]:
        with pytest.raises(ValueError):
            backward_asof([], times, values)


def test_invalid_query_age_and_exact_types_raise():
    for queries, age, exact in [([1.5], None, True), ([False], None, True),
                                ([1], -1, True), ([1], True, True),
                                ([1], 1.5, True), ([1], None, 1)]:
        with pytest.raises(ValueError):
            backward_asof(queries, [0], [2], max_age=age, allow_exact=exact)


def test_tuple_inputs_and_original_lists_remain_unchanged():
    observations, values, queries = [-2, 0], ["a", "b"], [1, -1, 1]
    assert backward_asof(tuple(queries), tuple(observations), tuple(values)) == ["b", "a", "b"]
    assert backward_asof(queries, observations, values) == ["b", "a", "b"]
    assert (observations, values, queries) == ([-2, 0], ["a", "b"], [1, -1, 1])
