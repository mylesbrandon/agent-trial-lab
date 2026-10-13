def minimum_spanning_forest(nodes, edges):
    if len(set(nodes)) != len(nodes):
        raise ValueError("duplicate node names")
    parent = {node: node for node in nodes}
    ranked = []
    for left, right, weight in edges:
        if left not in parent or right not in parent:
            raise ValueError("edge references an unknown node")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not -1e100 <= weight <= 1e100:
            raise ValueError("edge weights must be finite real numbers")
        left, right = sorted((left, right))
        ranked.append((left, right, weight))
    ranked.sort(key=lambda edge: (-edge[2], edge[0], edge[1]))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    forest = []
    total = 0
    for left, right, weight in ranked:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root
            forest.append((left, right, weight))
            total += weight
    return total, forest
