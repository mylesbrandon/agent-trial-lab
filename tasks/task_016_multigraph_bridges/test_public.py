from starter import bridges

def test_chain_edges_are_bridges():
    assert bridges(["a", "b", "c"], [("a", "b"), ("b", "c")]) == [("a", "b"), ("b", "c")]

def test_triangle_has_no_bridge():
    assert bridges(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]) == []

def test_disconnected_components_and_isolate():
    assert bridges(["a", "b", "c", "d", "e"], [("b", "a"), ("d", "c")]) == [("a", "b"), ("c", "d")]
