# Task 015: Canonical Bipartite Coloring

Repair `bipartite_coloring(graph)` in `starter.py`.

`graph` maps string node names to lists of neighbor names. Each listed edge is
**undirected**, even if the reverse entry is absent. Return a dictionary assigning
every node color `0` or `1` so endpoints of every edge have different colors.
In each connected component, the lexicographically smallest node must have color
`0`; this fixes the otherwise arbitrary choice between the two colorings.

* Return `None` when no valid coloring exists, including for a self-loop or an
  odd cycle in any component. An even cycle is valid.
* Include isolated nodes with color `0`; an empty graph returns `{}`.
* Ignore duplicate edges. Dictionary/list/string input shapes are guaranteed.
* Raise `ValueError` if any listed neighbor is not a graph key. Check the whole
  graph for unknown neighbors before deciding whether it is bipartite.
* Do not mutate the graph or its lists. Dictionary insertion order is irrelevant.

Example: `{"a": [], "b": ["a"], "z": []}` returns
`{"a": 0, "b": 1, "z": 0}`.
