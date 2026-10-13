# Task 013: Strongly Connected Components

Repair `strongly_connected_components(graph)` in `starter.py`.

`graph` maps string node names to lists of outgoing neighbors. Partition every
node into maximal groups where each node can reach every other node by directed
paths. Return a list of lists: sort the names inside each component, then sort
the component lists lexicographically. A one-way connection does not merge groups.

* An isolated node is a singleton component. Return `[]` for an empty graph.
* Self-loops and duplicate edges do not change the partition.
* All neighbor names must be keys. Raise `ValueError` for any unknown neighbor,
  including in a disconnected component. Input dictionary/list/string shapes are guaranteed.
* Do not mutate the graph or its neighbor lists.

Example: `{"a": ["b"], "b": ["a", "c"], "c": []}` returns
`[["a", "b"], ["c"]]`.
