from starter import bipartite_coloring

def test_even_cycle():
    graph = {"a": ["b", "d"], "b": ["c"], "c": ["d"], "d": []}
    assert bipartite_coloring(graph) == {"a": 0, "b": 1, "c": 0, "d": 1}

def test_disconnected_components():
    graph = {"a": ["b"], "b": [], "c": ["d"], "d": [], "z": []}
    assert bipartite_coloring(graph) == {"a": 0, "b": 1, "c": 0, "d": 1, "z": 0}

def test_triangle_cannot_be_colored():
    assert bipartite_coloring({"a": ["b", "c"], "b": ["c"], "c": []}) is None
