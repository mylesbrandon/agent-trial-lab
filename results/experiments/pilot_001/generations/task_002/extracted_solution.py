lua
if start == target:
    return 0, [start]

distances = {node: math.inf for node in graph}
distances[start] = 0

previous = {}
queue = [(0, start)]

while queue:
    current_distance, node = heapq.heappop(queue)

    if current_distance > distances[node]:
        continue

    if node == target:
        break

    for neighbor, weight in graph[node]:
        new_distance = current_distance + weight

        if new_distance < distances[neighbor]:
            distances[neighbor] = new_distance
            previous[neighbor] = node
            heapq.heappush(queue, (new_distance, neighbor))

if distances[target] == math.inf:
    return math.inf, []

path = [target]

while path[-1] != start:
    path.append(previous[path[-1]])

path.reverse()
return distances[target], path
