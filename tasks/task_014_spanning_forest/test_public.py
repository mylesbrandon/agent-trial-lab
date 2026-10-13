from starter import minimum_spanning_forest

def test_triangle_selects_two_lightest_connecting_edges():
    edges = [("a", "b", 3), ("b", "c", 1), ("a", "c", 2)]
    assert minimum_spanning_forest(["a", "b", "c"], edges) == (3, [("b", "c", 1), ("a", "c", 2)])

def test_disconnected_components_and_isolated_vertex():
    edges = [("b", "a", 2), ("d", "c", 4)]
    assert minimum_spanning_forest(["a", "b", "c", "d", "e"], edges) == (6, [("a", "b", 2), ("c", "d", 4)])

def test_empty_graph():
    assert minimum_spanning_forest([], []) == (0, [])
