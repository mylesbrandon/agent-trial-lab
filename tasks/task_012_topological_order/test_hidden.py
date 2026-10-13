import copy
import pytest
from starter import topological_order

def test_newly_ready_node_competes_with_existing_frontier():
    assert topological_order({"a": ["b"], "b": [], "z": []}) == ["a", "b", "z"]

def test_duplicate_edges_are_one_constraint():
    assert topological_order({"a": ["b", "b"], "b": ["c", "c"], "c": []}) == ["a", "b", "c"]

def test_empty_graph():
    assert topological_order({}) == []

def test_cycle_in_a_disconnected_component():
    with pytest.raises(ValueError):
        topological_order({"a": [], "x": ["y"], "y": ["x"]})

def test_self_loop_is_a_cycle():
    with pytest.raises(ValueError):
        topological_order({"a": ["a"]})

def test_unknown_neighbor_is_rejected():
    with pytest.raises(ValueError):
        topological_order({"a": [], "z": ["missing"]})

def test_graph_and_neighbor_lists_are_unchanged():
    graph = {"z": ["x", "x"], "a": ["x"], "x": []}
    before = copy.deepcopy(graph)
    assert topological_order(graph) == ["a", "z", "x"]
    assert graph == before
