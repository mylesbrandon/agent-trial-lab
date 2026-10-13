# Task 016: Bridge Edges in an Undirected Multigraph

Repair `bridges(nodes, edges)` in `starter.py`.

`nodes` is a list of string names and `edges` is a list of `(u, v)` tuples.
Each tuple is a separate undirected edge, so repeated pairs represent parallel
edges. An edge is a **bridge** exactly when removing that one edge increases the
number of connected components, counting the whole graph.

Return all bridges as a sorted list of tuples. Within each tuple put the smaller
endpoint first. The result is independent of input edge or node ordering.

* Parallel edges, including reversed duplicate pairs, are separate edges: none
  of a parallel group is a bridge. Self-loops are never bridges.
* Include bridges in every disconnected component. Isolated nodes contribute
  no bridge; empty inputs return `[]`.
* Raise `ValueError` for duplicate node names or unknown endpoints, including
  endpoints of self-loops. Other input shapes are guaranteed.
* Do not mutate `nodes`, `edges`, or their contents.

Example: nodes `["a", "b", "c"]` and edges
`[("a", "b"), ("b", "a"), ("b", "c")]` return `[("b", "c")]`.
