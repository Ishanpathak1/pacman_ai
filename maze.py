# maze.py

MAZE = [
    [0, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 0],
]

START = (0, 0)
GOAL = (2, 4)

def get_neighbors(maze, position):
    rows, cols = len(maze), len(maze[0])
    x, y = position
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    neighbors = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
            neighbors.append((nx, ny))
    return neighbors
