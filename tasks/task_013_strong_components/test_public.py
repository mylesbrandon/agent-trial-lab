from starter import strongly_connected_components

def test_cycle_with_one_way_tail():
    graph = {"a": ["b"], "b": ["a", "c"], "c": []}
    assert strongly_connected_components(graph) == [["a", "b"], ["c"]]

def test_separate_cycles():
    graph = {"d": ["c"], "c": ["d"], "b": ["a"], "a": ["b"]}
    assert strongly_connected_components(graph) == [["a", "b"], ["c", "d"]]

def test_empty_graph():
    assert strongly_connected_components({}) == []
