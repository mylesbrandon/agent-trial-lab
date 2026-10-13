from collections import deque


def bipartite_coloring(graph):
    neighbors = {node: set() for node in graph}
    for node, values in graph.items():
        for neighbor in values:
            if neighbor not in graph:
                raise ValueError("edge references an unknown node")
            neighbors[node].add(neighbor)
    colors = {}
    for root in sorted(graph):
        if root in colors:
            continue
        colors[root] = 0
        queue = deque([root])
        while queue:
            node = queue.popleft()
            for neighbor in sorted(neighbors[node]):
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[node]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[node]:
                    return None
    return colors
