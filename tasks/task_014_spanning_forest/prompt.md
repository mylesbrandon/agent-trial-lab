# Task 014: Deterministic Minimum Spanning Forest

Repair `minimum_spanning_forest(nodes, edges)` in `starter.py`.

`nodes` is a list of string names. `edges` is a list of `(u, v, weight)` tuples
representing an undirected multigraph. Return `(total_weight, forest_edges)`:
the sum of selected weights and a list of selected edge tuples.

Use this deterministic Kruskal rule: normalize each edge so `u <= v`, sort all
edges by `(weight, u, v)`, and scan in that order. Select an edge exactly when
its endpoints are not yet connected by selected edges. Return selected edges
in that scan order. This specifies tie-breaking as well as the minimum weight.

* Build a minimum spanning tree for **each** connected component. Isolated
  nodes contribute no edges. Empty inputs return `(0, [])`.
* Negative and zero weights are valid. Self-loops are never selected. Parallel
  and duplicate edges are valid, but cannot create a cycle in the forest.
* Raise `ValueError` for duplicate node names, unknown endpoints, or weights
  outside the supported range `[-1e100, 1e100]` or that are not finite
  `int` or `float` values. Booleans are invalid weights.
  Validate even edges that would never be selected. Other input shapes are guaranteed.
* Do not mutate either input or their contents.

Example: nodes `["a", "b", "c"]` and edges
`[("a", "b", 3), ("b", "c", 1), ("a", "c", 2)]` return
`(3, [("b", "c", 1), ("a", "c", 2)])`.
