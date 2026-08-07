You are solving a Python code-repair benchmark task.

Follow the written specification exactly.

Return only the complete contents of starter.py after your repair.
Do not include Markdown fences, explanations, tests, or commentary.

TASK SPECIFICATION
------------------
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


STARTER CODE
------------
import heapq
import math


def shortest_path(graph, start, target):
    """
    Find the shortest path between two nodes in a directed,
    nonnegatively weighted graph.

    This implementation contains logical bugs that must be repaired.
    """
    distances = {node: math.inf for node in graph}
    distances[start] = 0

    previous = {}
    visited = set()
    queue = [(0, start)]

    while queue:
        current_distance, node = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)

        if node == target:
            break

        for neighbor, weight in graph[node]:
            new_distance = current_distance + weight

            # BUG: This overwrites the best-known distance without
            # checking whether the new route is actually better.
            if neighbor not in visited:
                distances[neighbor] = new_distance
                previous[neighbor] = node
                heapq.heappush(queue, (new_distance, neighbor))

    # BUG: The required unreachable result is (math.inf, []).
    if distances[target] == math.inf:
        return None

    path = [target]

    while path[-1] != start:
        path.append(previous[path[-1]])

    path.reverse()
    return distances[target], path


PUBLIC TESTS
------------
import pytest

from starter import shortest_path


def test_basic_shortest_path():
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 2), ("D", 5)],
        "D": [],
    }

    result = shortest_path(graph, "A", "D")

    assert result == (4, ["A", "C", "B", "D"])


def test_indirect_path_is_cheaper():
    graph = {
        "A": [("B", 5), ("C", 1)],
        "B": [],
        "C": [("B", 1)],
    }

    result = shortest_path(graph, "A", "B")

    assert result == (2, ["A", "C", "B"])


def test_start_equals_target():
    graph = {
        "A": [("B", 1)],
        "B": [],
    }

    assert shortest_path(graph, "A", "A") == (0, ["A"])


def test_missing_start_raises_key_error():
    graph = {"A": []}

    with pytest.raises(KeyError):
        shortest_path(graph, "missing", "A")


def test_missing_target_raises_key_error():
    graph = {"A": []}

    with pytest.raises(KeyError):
        shortest_path(graph, "A", "missing")

