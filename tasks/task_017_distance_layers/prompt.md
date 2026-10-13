# Task 017: Multi-Source Directed Distance Layers

Repair `distance_layers(graph, sources)` in `starter.py`.

`graph` maps string node names to lists of outgoing neighbor names. `sources`
is a list of starting node names. For every reachable node, its distance is the
**minimum number of directed edges from any source**. Return a list of layers:
layer `d` contains exactly the nodes at distance `d`, sorted lexicographically.
A node appears once, at its smallest distance. Omit unreachable nodes.

* Layer zero is the sorted set of sources. Ignore duplicate sources and edges.
  Cycles and self-loops are valid. Sources always have distance zero even when
  another source has a path to them.
* Empty sources return `[]`, as does an empty graph with no sources.
* Raise `ValueError` for any unknown source or neighbor, including unreachable
  neighbors. Validate graph references even when `sources` is empty.
  Dictionary/list/string input shapes are guaranteed.
* Do not mutate the graph, its neighbor lists, or sources.

Example: `{"a": ["b"], "b": ["c"], "c": [], "x": ["c"]}` with
sources `["a", "x"]` returns `[["a", "x"], ["b", "c"]]`.
