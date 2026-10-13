import copy
import pytest
from starter import distance_layers

def test_duplicates_cycles_and_self_loops():
    graph = {"a": ["a", "b", "b"], "b": ["a", "c"], "c": ["c"]}
    assert distance_layers(graph, ["a", "a"]) == [["a"], ["b"], ["c"]]

def test_edges_are_directed_and_unreachable_nodes_are_omitted():
    graph = {"a": ["b"], "b": [], "x": []}
    assert distance_layers(graph, ["b"]) == [["b"]]

def test_sources_stay_in_layer_zero_when_connected():
    graph = {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}
    assert distance_layers(graph, ["b", "a"]) == [["a", "b"], ["c"], ["d"]]

def test_shortcut_beats_longer_path():
    graph = {"a": ["b", "d"], "b": ["c"], "c": ["e"], "d": ["e"], "e": []}
    assert distance_layers(graph, ["a"]) == [["a"], ["b", "d"], ["c", "e"]]

def test_unknown_source_is_rejected():
    with pytest.raises(ValueError):
        distance_layers({"a": []}, ["missing"])

def test_unknown_neighbor_is_checked_even_without_sources():
    with pytest.raises(ValueError):
        distance_layers({"a": [], "z": ["missing"]}, [])

def test_empty_graph():
    assert distance_layers({}, []) == []

def test_inputs_are_unchanged_and_layer_members_sorted():
    graph = {"z": [], "a": ["z", "m"], "m": []}
    sources = ["a", "a"]
    before = copy.deepcopy((graph, sources))
    assert distance_layers(graph, sources) == [["a"], ["m", "z"]]
    assert (graph, sources) == before
