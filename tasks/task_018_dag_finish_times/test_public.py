import pytest
from starter import earliest_finish_times

def test_fork_and_join_waits_for_longest_prerequisite():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    durations = {"a": 2, "b": 3, "c": 5, "d": 1}
    assert earliest_finish_times(graph, durations) == {"a": 2, "b": 5, "c": 7, "d": 8}

def test_disconnected_tasks_start_independently():
    graph = {"a": ["b"], "b": [], "x": []}
    assert earliest_finish_times(graph, {"a": 4, "b": 1, "x": 10}) == {"a": 4, "b": 5, "x": 10}

def test_fractional_and_zero_durations():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    result = earliest_finish_times(graph, {"a": 0, "b": 0.25, "c": 0.5})
    assert result == pytest.approx({"a": 0, "b": 0.25, "c": 0.75})
