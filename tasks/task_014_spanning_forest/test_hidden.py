import copy
import math
import pytest
from starter import minimum_spanning_forest

def test_negative_and_zero_weights():
    edges = [("a", "b", -3), ("b", "c", 0), ("a", "c", 2)]
    assert minimum_spanning_forest(["a", "b", "c"], edges) == (-3, [("a", "b", -3), ("b", "c", 0)])

def test_parallel_edges_and_self_loops():
    edges = [("a", "a", -100), ("b", "a", 5), ("a", "b", 1), ("a", "b", 1)]
    assert minimum_spanning_forest(["a", "b"], edges) == (1, [("a", "b", 1)])

def test_ties_have_canonical_endpoint_order():
    edges = [("c", "b", 1), ("c", "a", 1), ("b", "a", 1), ("d", "c", 1), ("d", "b", 1)]
    assert minimum_spanning_forest(["d", "c", "b", "a"], edges) == (3, [("a", "b", 1), ("a", "c", 1), ("b", "d", 1)])

def test_unknown_endpoint_even_on_self_loop_is_invalid():
    with pytest.raises(ValueError):
        minimum_spanning_forest(["a"], [("missing", "missing", 0)])

def test_duplicate_nodes_are_invalid():
    with pytest.raises(ValueError):
        minimum_spanning_forest(["a", "a"], [])

def test_invalid_weights_are_rejected_even_on_ignored_edges():
    for weight in (math.nan, math.inf, -math.inf, True, "1", 10**1000, 1e101, -1e101):
        with pytest.raises(ValueError):
            minimum_spanning_forest(["a"], [("a", "a", weight)])

def test_inputs_are_unchanged():
    nodes = ["c", "b", "a"]
    edges = [("c", "b", 2), ("a", "b", 1), ("a", "c", 7)]
    before = copy.deepcopy((nodes, edges))
    assert minimum_spanning_forest(nodes, edges) == (3, [("a", "b", 1), ("b", "c", 2)])
    assert (nodes, edges) == before


def test_supported_weight_boundaries():
    edges = [("a", "b", -1e100), ("b", "c", 1e100)]
    assert minimum_spanning_forest(["a", "b", "c"], edges) == (0, edges)
