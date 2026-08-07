# Task 002: Repair a Shortest-Path Function

Repair the `shortest_path(graph, start, target)` function in `starter.py`.

The function must find the shortest path from `start` to `target` in a directed, weighted graph.

## Graph Format

The graph is represented as a dictionary:

```python
graph = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": []
}
```

Each dictionary key is a node. Each `(neighbor, weight)` tuple represents a directed edge.

You may assume:

* Every node is represented by a string.
* Every neighbor referenced by an edge is also a key in the graph.
* Edge weights are nonnegative integers or floats.
* Zero-weight edges are valid.

## Return Value

Return a tuple:

```python
(distance, path)
```

For example:

```python
shortest_path(graph, "A", "D")
# (4, ["A", "C", "B", "D"])
```

## Required Behavior

* Return the minimum total distance and a corresponding path.
* The path must begin with `start` and end with `target`.
* Return `(0, [start])` when `start == target`.
* Return `(math.inf, [])` when no path exists.
* Raise `KeyError` when `start` is not a graph key.
* Raise `KeyError` when `target` is not a graph key.
* Correctly handle zero-weight edges, duplicate edges, cycles, and nodes with no outgoing edges.
* If multiple shortest paths exist, any valid shortest path is acceptable.
* Do not mutate the input graph.
