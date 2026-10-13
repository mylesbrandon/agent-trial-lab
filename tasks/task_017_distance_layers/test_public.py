from starter import distance_layers

def test_single_source_branching():
    graph = {"a": ["c", "b"], "b": ["d"], "c": ["d"], "d": []}
    assert distance_layers(graph, ["a"]) == [["a"], ["b", "c"], ["d"]]

def test_multiple_sources_take_minimum_distance():
    graph = {"a": ["b"], "b": ["c"], "c": [], "x": ["c"]}
    assert distance_layers(graph, ["a", "x"]) == [["a", "x"], ["b", "c"]]

def test_no_sources():
    assert distance_layers({"a": ["b"], "b": []}, []) == []
