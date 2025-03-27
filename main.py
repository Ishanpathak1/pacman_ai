# main.py

from maze import MAZE, START, GOAL
from search import bfs

def print_maze_with_path(maze, path):
    maze_copy = [row[:] for row in maze]
    for x, y in path:
        if (x, y) not in [START, GOAL]:
            maze_copy[x][y] = "*"
    maze_copy[START[0]][START[1]] = "S"
    maze_copy[GOAL[0]][GOAL[1]] = "G"

    for row in maze_copy:
        print(" ".join(str(cell) for cell in row))

result = bfs(MAZE, START, GOAL)

from utils import timeit
result = timeit(bfs, MAZE, START, GOAL)
print("Time Taken:", result['time_taken'], "seconds")


print("✅ BFS Result:")
print("Path:", result['path'])
print("Nodes Expanded:", result['nodes_expanded'])
print("Max Fringe Size:", result['max_fringe'])
print("Path Cost:", result['path_cost'])
print("\nMaze Path Visualization:")
print_maze_with_path(MAZE, result['path'])
