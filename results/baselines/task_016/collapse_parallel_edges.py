def bridges(nodes, edges):
    if len(set(nodes)) != len(nodes):
        raise ValueError("duplicate node names")
    edges = sorted({tuple(sorted(edge)) for edge in edges})
    adjacency = {node: [] for node in nodes}
    for edge_id, (left, right) in enumerate(edges):
        if left not in adjacency or right not in adjacency:
            raise ValueError("edge references an unknown node")
        adjacency[left].append((right, edge_id))
        adjacency[right].append((left, edge_id))
    discovered = {}
    low = {}
    result = []
    for root in nodes:
        if root in discovered:
            continue
        discovered[root] = low[root] = len(discovered)
        stack = [(root, None, None, iter(adjacency[root]))]
        while stack:
            node, parent, parent_edge, iterator = stack[-1]
            edge = next(iterator, None)
            if edge is None:
                stack.pop()
                if parent is not None:
                    low[parent] = min(low[parent], low[node])
                    if low[node] > discovered[parent]:
                        result.append(tuple(sorted((parent, node))))
                continue
            neighbor, edge_id = edge
            if edge_id == parent_edge:
                continue
            if neighbor not in discovered:
                discovered[neighbor] = low[neighbor] = len(discovered)
                stack.append((neighbor, node, edge_id, iter(adjacency[neighbor])))
            else:
                low[node] = min(low[node], discovered[neighbor])
    return sorted(result)
