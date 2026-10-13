import pytest
from starter import topological_order

def test_chain():
    assert topological_order({"c": [], "b": ["c"], "a": ["b"]}) == ["a", "b", "c"]

def test_fork_and_disconnected_node():
    graph = {"root": ["right", "left"], "right": [], "left": [], "alone": []}
    assert topological_order(graph) == ["alone", "root", "left", "right"]

def test_directed_cycle_is_rejected():
    with pytest.raises(ValueError):
        topological_order({"a": ["b"], "b": ["a"]})
