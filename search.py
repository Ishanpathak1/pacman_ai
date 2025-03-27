# search.py

from collections import deque
from maze import get_neighbors

def bfs(maze, start, goal):
    queue = deque()
    queue.append((start, [start]))  # (current_position, path_so_far)
    visited = set()
    visited.add(start)

    nodes_expanded = 0
    max_fringe = 1

    while queue:
        max_fringe = max(max_fringe, len(queue))
        current, path = queue.popleft()
        nodes_expanded += 1

        if current == goal:
            return {
                "path": path,
                "visited": list(visited),
                "nodes_expanded": nodes_expanded,
                "max_fringe": max_fringe,
                "path_cost": len(path) - 1
            }

        for neighbor in get_neighbors(maze, current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return {
        "path": [],
        "visited": list(visited),
        "nodes_expanded": nodes_expanded,
        "max_fringe": max_fringe,
        "path_cost": float("inf")
    }
