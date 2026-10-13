import heapq


def topological_order(graph):
    neighbors = {node: set(values) for node, values in graph.items()}
    indegree = dict.fromkeys(graph, 0)
    for values in neighbors.values():
        for neighbor in values:
            if neighbor not in graph:
                raise ValueError("edge references an unknown node")
            indegree[neighbor] += 1
    ready = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        node = heapq.heappop(ready)
        result.append(node)
        for neighbor in neighbors[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(ready, neighbor)
    if len(result) != len(graph):
        raise ValueError("graph contains a cycle")
    return result
