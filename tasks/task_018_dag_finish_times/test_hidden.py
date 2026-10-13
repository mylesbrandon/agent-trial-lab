import copy
import math
import pytest
from starter import earliest_finish_times

def test_duplicate_edges_are_one_dependency():
    graph = {"a": ["b", "b"], "b": ["c", "c"], "c": []}
    assert earliest_finish_times(graph, {"a": 2, "b": 3, "c": 4}) == {"a": 2, "b": 5, "c": 9}

def test_disconnected_cycle_is_rejected():
    graph = {"a": [], "x": ["y"], "y": ["x"]}
    with pytest.raises(ValueError):
        earliest_finish_times(graph, {"a": 1, "x": 1, "y": 1})

def test_self_loop_is_rejected():
    with pytest.raises(ValueError):
        earliest_finish_times({"a": ["a"]}, {"a": 0})

def test_duration_keys_must_match_exactly():
    for durations in ({}, {"a": 1, "extra": 1}):
        with pytest.raises(ValueError):
            earliest_finish_times({"a": []}, durations)

def test_invalid_durations_are_rejected():
    for duration in (-1, math.nan, math.inf, -math.inf, True, "2", 10**1000, 1e101):
        with pytest.raises(ValueError):
            earliest_finish_times({"a": []}, {"a": duration})

def test_unknown_neighbor_is_rejected():
    with pytest.raises(ValueError):
        earliest_finish_times({"a": ["missing"]}, {"a": 1})

def test_empty_graph():
    assert earliest_finish_times({}, {}) == {}

def test_inputs_are_unchanged_and_predecessors_use_maximum():
    graph = {"c": [], "b": ["c"], "a": ["c", "c"]}
    durations = {"a": 2, "b": 5, "c": 3}
    before = copy.deepcopy((graph, durations))
    assert earliest_finish_times(graph, durations) == {"a": 2, "b": 5, "c": 8}
    assert (graph, durations) == before


def test_supported_duration_upper_boundary():
    assert earliest_finish_times({"a": []}, {"a": 1e100}) == {"a": 1e100}
