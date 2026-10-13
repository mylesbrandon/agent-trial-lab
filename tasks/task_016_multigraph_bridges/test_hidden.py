import copy
import pytest
from starter import bridges

def test_parallel_edges_are_not_bridges():
    edges = [("a", "b"), ("b", "a"), ("b", "c")]
    assert bridges(["a", "b", "c"], edges) == [("b", "c")]

def test_self_loops_do_not_hide_a_bridge():
    edges = [("a", "a"), ("a", "b"), ("b", "b")]
    assert bridges(["a", "b"], edges) == [("a", "b")]

def test_cycle_with_a_chain_attached():
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d"), ("d", "e")]
    assert bridges(["e", "d", "c", "b", "a"], edges) == [("c", "d"), ("d", "e")]

def test_empty_graph_and_isolated_nodes():
    assert bridges([], []) == []
    assert bridges(["a", "b"], []) == []

def test_unknown_endpoint_is_invalid():
    with pytest.raises(ValueError):
        bridges(["a"], [("unknown", "unknown")])

def test_duplicate_node_names_are_invalid():
    with pytest.raises(ValueError):
        bridges(["a", "a"], [])

def test_inputs_and_tuple_directions_are_unchanged():
    nodes = ["c", "a", "b"]
    edges = [("c", "b"), ("b", "a")]
    before = copy.deepcopy((nodes, edges))
    assert bridges(nodes, edges) == [("a", "b"), ("b", "c")]
    assert (nodes, edges) == before

def test_parallel_pair_in_a_disconnected_component():
    edges = [("a", "b"), ("x", "y"), ("x", "y")]
    assert bridges(["a", "b", "x", "y"], edges) == [("a", "b")]
