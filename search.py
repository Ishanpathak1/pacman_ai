# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    stack = util.Stack()
    visited = set()

    startState = problem.getStartState()
    if problem.isGoalState(startState):
        return []

    stack.push((startState, []))

    while not stack.isEmpty():
        currentState, currentPath = stack.pop()

        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newPath = currentPath + [action]
                stack.push((nextState, newPath))

    return []
    # util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    queue = util.Queue()
    visited = set()

    startState = problem.getStartState()
    queue.push((startState, []))

    while not queue.isEmpty():
        currentState, currentPath = queue.pop()

        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newPath = currentPath + [action]
                queue.push((nextState, newPath))

    return []
    # util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    pq = util.PriorityQueue()
    visited = set()

    startState = problem.getStartState()
    if problem.isGoalState(startState):
        return []

    pq.push((startState, [], 0), 0)  # (state, path, cost), cost for priority

    while not pq.isEmpty():
        currentState, currentPath, currentCost = pq.pop()
        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newCost = currentCost + cost
                newPath = currentPath + [action]
                pq.push((nextState, newPath, newCost), newCost)

    return []
    # util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = util.PriorityQueue()
    visited = set()

    startState = problem.getStartState()
    if problem.isGoalState(startState):
        return []

    priority = 0 + heuristic(startState, problem)
    pq.push((startState, [], 0), priority)  # (state, path, cost), cost for priority

    while not pq.isEmpty():
        currentState, currentPath, currentCost = pq.pop()
        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newCost = currentCost + cost
                newPath = currentPath + [action]
                priority = newCost + heuristic(nextState, problem)
                pq.push((nextState, newPath, newCost), priority)

    return []
    # util.raiseNotDefined()


def greedyBestFirstSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = util.PriorityQueue()
    visited = set()

    startState = problem.getStartState()
    if problem.isGoalState(startState):
        return []

    priority = heuristic(startState, problem)
    pq.push((startState, [], 0), priority)  # (state, path, cost), cost for priority

    while not pq.isEmpty():
        currentState, currentPath, currentCost = pq.pop()
        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newCost = currentCost + cost
                newPath = currentPath + [action]
                priority = heuristic(nextState, problem)
                pq.push((nextState, newPath, newCost), priority)

    return []
    # util.raiseNotDefined()


def depthLimitedSearch(problem, limit):
    """
    Performs a depth-limited search from the start state up to 'limit' depth.

    Returns:
        - A solution path (list of actions) if the goal is found within the limit
        - A special value 'cutoff' if the goal was not found but the depth limit was reached on at least one path
        - A special value 'failure' if the entire search space reachable within the limit was explored and the goal was not found (Means no solution was exists at or above this depth)

    Note: For simplicity in IDS, we can often just return the path or None. The 'cutoff'/'failure' values exist for theoretical correctness. In this implementation, IDS will be simplified to return the path or None.
    """
    stack = util.Stack()
    startState = problem.getStartState()

    if problem.isGoalState(startState):
        return []

    visited_at_depth = {}

    stack.push((startState, [], 0))
    visited_at_depth[startState] = 0

    while not stack.isEmpty():
        currentState, currentPath, currentDepth = stack.pop()

        if problem.isGoalState(currentState):
            return currentPath

        if currentDepth < limit:
            successors = problem.getSuccessors(currentState)
            for nextState, action, cost in successors:
                newDepth = currentDepth + 1
                if nextState not in visited_at_depth or newDepth < visited_at_depth[nextState]:
                    visited_at_depth[nextState] = newDepth
                    newPath = currentPath + [action]
                    stack.push((nextState, newPath, newDepth))
    return None


def iterativeDeepeningSearch(problem):
    """
    Performs Iterative Deepening Search: calls depthLimitedSearch
    with increasing depth limits (0, 1, 2, ...) until a solution is found.

    Suitable for problems with uniform step costs where BFS memory usage
    is a concern.
    """
    depth_limit = 0
    while True:
        # print(f"IDS: Searching with depth limit {depth_limit}")
        result = depthLimitedSearch(problem, depth_limit)
        if result is not None:
            return result
        depth_limit += 1
        if depth_limit > 500: # Example limit
            print("IDS: Exceeded maximum depth limit, assuming no solution.")
            return []


def weightedAStarSearch(problem, heuristic=nullHeuristic, weight=1.5):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = util.PriorityQueue()
    visited = set()

    startState = problem.getStartState()
    if problem.isGoalState(startState):
        return []

    initial_priority = 0 + weight * heuristic(startState, problem)
    pq.push((startState, [], 0), initial_priority)  # (state, path, cost), cost for priority

    while not pq.isEmpty():
        currentState, currentPath, currentCost = pq.pop()
        if currentState in visited:
            continue

        visited.add(currentState)
        if problem.isGoalState(currentState):
            return currentPath

        successors = problem.getSuccessors(currentState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                newCost = currentCost + cost
                newPath = currentPath + [action]
                priority = newCost + weight * heuristic(nextState, problem)
                pq.push((nextState, newPath, newCost), priority)

    return []
    # util.raiseNotDefined()



# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch
ids = iterativeDeepeningSearch
wastar = weightedAStarSearch
