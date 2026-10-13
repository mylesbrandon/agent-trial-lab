from collections import deque


def earliest_finish_times(graph, durations):
    if set(durations) != set(graph):
        raise ValueError("durations must have exactly the graph's keys")
    for duration in durations.values():
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 <= duration <= 1e100:
            raise ValueError("durations must be finite nonnegative numbers")
    neighbors = {node: set(values) for node, values in graph.items()}
    indegree = dict.fromkeys(graph, 0)
    for values in neighbors.values():
        for neighbor in values:
            if neighbor not in graph:
                raise ValueError("edge references an unknown node")
            indegree[neighbor] += 1
    ready = deque(node for node in graph if indegree[node] == 0)
    start = dict.fromkeys(graph, 0)
    finish = {}
    while ready:
        node = ready.popleft()
        finish[node] = start[node] + durations[node]
        for neighbor in neighbors[node]:
            start[neighbor] += finish[node]
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
    if len(finish) != len(graph):
        raise ValueError("graph contains a cycle")
    return finish
