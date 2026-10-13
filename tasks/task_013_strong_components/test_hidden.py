import copy
import pytest
from starter import strongly_connected_components

def test_one_way_chain_is_not_one_component():
    graph = {"c": [], "b": ["c"], "a": ["b"]}
    assert strongly_connected_components(graph) == [["a"], ["b"], ["c"]]

def test_duplicate_edges_and_self_loops():
    graph = {"a": ["a", "b", "b"], "b": ["a", "b"], "c": ["c"]}
    assert strongly_connected_components(graph) == [["a", "b"], ["c"]]

def test_isolated_nodes_are_sorted_singletons():
    assert strongly_connected_components({"z": [], "a": [], "m": []}) == [["a"], ["m"], ["z"]]

def test_cross_edges_between_interleaved_components():
    graph = {"a": ["d", "b"], "d": ["a"], "b": ["c"], "c": ["b", "e"], "e": []}
    assert strongly_connected_components(graph) == [["a", "d"], ["b", "c"], ["e"]]

def test_unknown_neighbor_anywhere_is_rejected():
    with pytest.raises(ValueError):
        strongly_connected_components({"a": ["a"], "z": ["missing"]})

def test_inputs_are_unchanged():
    graph = {"c": ["b", "b"], "b": ["a"], "a": ["c"]}
    before = copy.deepcopy(graph)
    assert strongly_connected_components(graph) == [["a", "b", "c"]]
    assert graph == before

def test_reachable_cycle_does_not_absorb_its_predecessor():
    graph = {"start": ["a"], "a": ["b"], "b": ["a"]}
    assert strongly_connected_components(graph) == [["a", "b"], ["start"]]
