# Prerequisities
- Python 3.11

## Algorithms Implemented (`search.py`)
- BFS
- DFS
- UCS
- A* (Manhattan Distance Heuristic)
- Greedy Best First Search

## Heuristics Implemented (`searchagents.py`)

* null heuristic
* manhattan heuristic
* food count heuristic
* farthest food heuristic
* corners heuristic

## Problems Explored

* PositionSearchProblem
* FoodSearchProblem
* CornersProblem

## How to run:
* python pacman.py

**Examples:**

```bash
# Run BFS on mediumMaze to find the goal position
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs

# Run A* on trickySearch to eat all food using farthestFoodHeuristic
python pacman.py -l trickySearch -p SearchAgent -a fn=astar,prob=FoodSearchProblem,heuristic=farthestFoodHeuristic

# Run GBFS on mediumCorners to visit all corners using cornersHeuristic
python pacman.py -l mediumCorners -p SearchAgent -a fn=gbfs,prob=CornersProblem,heuristic=cornersHeuristic