import copy
import pytest
from starter import bipartite_coloring

def test_reverse_only_edge_is_still_undirected():
    assert bipartite_coloring({"a": [], "b": ["a"]}) == {"a": 0, "b": 1}

def test_self_loop_is_not_bipartite():
    assert bipartite_coloring({"a": ["a"]}) is None

def test_empty_and_isolated_nodes():
    assert bipartite_coloring({}) == {}
    assert bipartite_coloring({"z": [], "a": []}) == {"a": 0, "z": 0}

def test_duplicate_edges_do_not_change_coloring():
    graph = {"a": ["b", "b"], "b": ["a", "c", "c"], "c": []}
    assert bipartite_coloring(graph) == {"a": 0, "b": 1, "c": 0}

def test_component_orientation_does_not_follow_insertion_order():
    graph = {"z": ["m"], "m": ["a"], "a": []}
    assert bipartite_coloring(graph) == {"a": 0, "m": 1, "z": 0}

def test_unknown_neighbor_is_validated_before_odd_cycle():
    with pytest.raises(ValueError):
        bipartite_coloring({"a": ["a"], "z": ["missing"]})

def test_odd_cycle_in_later_component_is_detected():
    graph = {"a": [], "x": ["y", "z"], "y": ["z"], "z": []}
    assert bipartite_coloring(graph) is None

def test_inputs_are_unchanged():
    graph = {"c": ["b", "b"], "b": ["a"], "a": []}
    before = copy.deepcopy(graph)
    assert bipartite_coloring(graph) == {"a": 0, "b": 1, "c": 0}
    assert graph == before
