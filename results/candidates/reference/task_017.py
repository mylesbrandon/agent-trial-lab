from collections import deque


def distance_layers(graph, sources):
    for values in graph.values():
        if any(neighbor not in graph for neighbor in values):
            raise ValueError("edge references an unknown node")
    if any(source not in graph for source in sources):
        raise ValueError("unknown source")
    if not sources:
        return []
    starting = set(sources)
    distances = dict.fromkeys(starting, 0)
    queue = deque(starting)
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    layers = [[] for _ in range(max(distances.values()) + 1)]
    for node, distance in distances.items():
        layers[distance].append(node)
    return [sorted(layer) for layer in layers]
