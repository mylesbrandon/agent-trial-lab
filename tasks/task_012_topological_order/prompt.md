# Task 012: Lexicographic Topological Ordering

Repair `topological_order(graph)` in `starter.py`.

`graph` is a dictionary from string node names to lists of outgoing neighbor
names. Its keys include every valid node. Return the lexicographically smallest
topological order as a list of strings. At each step, choose the smallest name
among **all currently available** nodes with no remaining prerequisites.

* Each edge `u -> v` means `u` must precede `v`.
* Treat duplicate neighbors as one edge. Disconnected and isolated nodes belong
  in the result. For an empty graph, return `[]`.
* Raise `ValueError` if any edge names an unknown node, including in a
  disconnected component. The dictionary/list/string input shapes are guaranteed.
* Raise `ValueError` if any component contains a directed cycle, including a self-loop.
* Do not mutate the graph or its neighbor lists.

Example: `{"a": ["b"], "b": [], "z": []}` returns `["a", "b", "z"]`.
The newly available `b` must be chosen before the already available `z`.
