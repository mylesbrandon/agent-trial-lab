def strongly_connected_components(graph):
    neighbors = {node: set(values) for node, values in graph.items()}
    reverse = {node: set() for node in graph}
    for node, values in neighbors.items():
        for neighbor in values:
            if neighbor not in graph:
                raise ValueError("edge references an unknown node")
            reverse[neighbor].add(node)

    seen = set()
    finished = []
    for root in graph:
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(neighbors[root]))]
        while stack:
            node, iterator = stack[-1]
            neighbor = next(iterator, None)
            if neighbor is None:
                stack.pop()
                finished.append(node)
            elif neighbor not in seen:
                seen.add(neighbor)
                stack.append((neighbor, iter(neighbors[neighbor])))

    seen.clear()
    components = []
    for root in reversed(finished):
        if root in seen:
            continue
        seen.add(root)
        stack = [root]
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in neighbors[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return sorted(components)
