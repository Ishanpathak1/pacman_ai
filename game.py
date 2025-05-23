# game.py
# -------
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

from util import *
import time, os
import traceback
import sys
import io  # Moved import here, was inside Game.__init__


#######################
# Parts worth reading #
#######################

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """

    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState and must return an action
        from Directions.{North, South, East, West, Stop}
        """
        # This method must be implemented by subclasses
        raiseNotDefined()


class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST: NORTH,
            WEST: SOUTH,
            STOP: STOP}

    RIGHT = dict([(y, x) for x, y in list(LEFT.items())])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}


class Configuration:
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def getPosition(self):
        return (self.pos)

    def getDirection(self):
        return self.direction

    def isInteger(self):
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other):
        if other == None: return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)=" + str(self.pos) + ", " + str(self.direction)

    def generateSuccessor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x + dx, y + dy), direction)


class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__(self, startConfiguration, isPacman):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        self.numCarrying = 0  # Used in capture.py
        self.numReturned = 0  # Used in capture.py

    def __str__(self):
        if self.isPacman:
            return "Pacman: " + str(self.configuration)
        else:
            return "Ghost: " + str(self.configuration)

    def __eq__(self, other):
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy(self):
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self):
        if self.configuration == None: return None
        return self.configuration.getPosition()

    def getDirection(self):
        return self.configuration.getDirection()


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists. Data is accessed
    via grid[x][y] where (x,y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a pacman board.
    """

    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]:
            # We allow grids for layout editing, paredes values are objects
            # raise Exception('Grids can only contain booleans')
            pass
        self.CELLS_PER_INT = 30  # Used for efficient hashing

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other == None: return False
        return self.data == other.data

    def __hash__(self):
        # Return Has a consistent representation
        # Also faster than str(self)
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    def asList(self, key=True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append((x, y))
        return list

    # The following methods are used for efficient state hashing
    def packBits(self):
        """
        Returns an efficient int list representation
        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index // self.height  # Integer division
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0: raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools


def reconstituteGrid(bitRep):
    """Used to reconstitute grids stored"""
    if type(bitRep) is not type((1, 2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])


####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST: (1, 0),
                   Directions.WEST: (-1, 0),
                   Directions.STOP: (0, 0)}

    _directionsAsList = list(_directions.items())

    TOLERANCE = .001

    @staticmethod
    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    @staticmethod
    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    @staticmethod
    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)

    @staticmethod
    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        # Check if the agent is midway between squares
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        if (abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE):
            # If midway, must continue in current direction
            return [config.getDirection()]

        # Otherwise, check adjacent squares
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    @staticmethod
    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x >= walls.width: continue  # Use >= for width/height
            next_y = y_int + dy
            if next_y < 0 or next_y >= walls.height: continue  # Use >= for width/height
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    @staticmethod
    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)


class GameStateData:
    """
    Stores the data packets for the game state.
    """

    def __init__(self, prevState=None):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agentStates = self.copyAgentStates(prevState.agentStates)
            self.layout = prevState.layout  # Shallow copy; layout never changes
            self._eaten = prevState._eaten  # Which agents have been eaten
            self.score = prevState.score

        # Variables used to log changes state to state - not part of core state
        self._foodEaten = None
        self._foodAdded = None
        self._capsuleEaten = None
        self._agentMoved = None
        self._lose = False
        self._win = False
        self.scoreChange = 0

    def deepCopy(self):
        """ Works appropriately for GameStateData """
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        # Layout doesn't need deep copy
        # self.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    def __eq__(self, other):
        """
        Allows two states to be compared. Checks agent states, food, capsules and score.
        """
        if other == None: return False
        if not self.agentStates == other.agentStates: return False
        if not self.food == other.food: return False
        if not self.capsules == other.capsules: return False
        if not self.score == other.score: return False
        return True

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        # Hash tuple of agent states, food, capsules, score
        # Food hashing is done by the Grid object using bit packing
        hashables = (hash(tuple(self.agentStates)),
                     hash(self.food),
                     hash(tuple(self.capsules)),
                     hash(self.score))

        # Use a large prime number for combining hashes
        result_hash = 0
        prime = 1000003  # A large prime number
        for h in hashables:
            result_hash = (result_hash * prime + h) % 2 ** 63  # Keep within reasonable bounds

        return result_hash

    def __str__(self):
        """ Produces a string representation of the state """
        width, height = self.layout.width, self.layout.height
        map_grid = Grid(width, height)
        if type(self.food) == type((1, 2)):  # If food is bitpacked
            self.food = reconstituteGrid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.layout.walls
                map_grid[x][y] = self._foodWallStr(food[x][y], walls[x][y])

        for agentState in self.agentStates:
            if agentState == None: continue
            if agentState.configuration == None: continue
            x, y = [int(i) for i in nearestPoint(agentState.configuration.pos)]
            agent_dir = agentState.configuration.direction
            if agentState.isPacman:
                map_grid[x][y] = self._pacStr(agent_dir)
            else:
                map_grid[x][y] = self._ghostStr(agent_dir)

        for x, y in self.capsules:
            map_grid[x][y] = 'o'

        return str(map_grid) + ("\nScore: %d\n" % self.score)

    def _foodWallStr(self, hasFood, hasWall):
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr(self, dir):
        if dir == Directions.NORTH: return 'v'
        if dir == Directions.SOUTH: return '^'
        if dir == Directions.WEST:  return '>'
        return '<'  # Default EAST

    def _ghostStr(self, dir):
        # Simple representation for ghost
        return 'G'

    def initialize(self, layout, numGhostAgents):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.food = layout.food.copy()
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0
        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            if not isPacman:
                if numGhosts == numGhostAgents:
                    continue  # Max ghosts reached
                else:
                    numGhosts += 1
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
        self._eaten = [False for a in self.agentStates]  # Which agents are eaten


class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__(self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0.0 for agent in agents]  # Use floats
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        # Create a stream for each agent's output
        self.agentOutput = [io.StringIO() for agent in agents]
        self.state = None  # Will be initialized in run()

    def getProgress(self):
        """ Returns the game progress fraction """
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash(self, agentIndex, quiet=False):
        """Helper method for handling agent crashes"""
        if not quiet: traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    # Store original stdout/stderr for unmute
    _ORIGINAL_STDOUT = sys.stdout
    _ORIGINAL_STDERR = sys.stderr

    def mute(self, agentIndex):
        """Redirects stdout/stderr for the specified agent"""
        if not self.muteAgents: return
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        """Restores original stdout/stderr"""
        if not self.muteAgents: return
        sys.stdout = Game._ORIGINAL_STDOUT
        sys.stderr = Game._ORIGINAL_STDERR

    def run(self):
        """
        Main control loop for game play.
        """
        # Initialize state if not already done (allows restarting a game object)
        if self.state is None:
            self.state = self.rules.newGame(self.agents, self.display, self.quiet, self.catchExceptions)

        self.display.initialize(self.state.data)
        self.numMoves = 0

        # Inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:  # Handle null agent
                self.mute(i)
                print(f"Agent {i} failed to load.", file=sys.stderr)
                self.unmute()
                self._agentCrash(i, quiet=True)
                return

            if hasattr(agent, "registerInitialState"):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        # Use TimeoutFunction if available and rules define startup time
                        startup_time_limit = self.rules.getMaxStartupTime(i)
                        if startup_time_limit > 0:
                            timed_func = TimeoutFunction(agent.registerInitialState, startup_time_limit)
                            try:
                                start_time = time.time()
                                timed_func(self.state.deepCopy())
                                time_taken = time.time() - start_time
                                self.totalAgentTimes[i] += time_taken
                            except TimeoutFunctionException:
                                print(f"Agent {i} ran out of time on startup!", file=sys.stderr)
                                self.unmute()
                                self.agentTimeout = True
                                self._agentCrash(i, quiet=True)
                                return
                        else:  # No time limit
                            agent.registerInitialState(self.state.deepCopy())

                    except Exception as data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return
                else:  # Run without exception catching
                    agent.registerInitialState(self.state.deepCopy())
                self.unmute()

        # Start game loop
        agentIndex = self.startingIndex
        numAgents = len(self.agents)

        while not self.gameOver:
            agent = self.agents[agentIndex]
            move_time = 0.0
            skip_action = False
            observation = None

            # Generate observation (potentially agent-specific)
            if hasattr(agent, 'observationFunction'):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        # Apply timeout if defined
                        move_timeout = self.rules.getMoveTimeout(agentIndex)
                        if move_timeout > 0:
                            timed_func = TimeoutFunction(agent.observationFunction, move_timeout)
                            try:
                                start_time = time.time()
                                observation = timed_func(self.state.deepCopy())
                            except TimeoutFunctionException:
                                print(f"Agent {i} timed out calculating observation!", file=sys.stderr)
                                skip_action = True  # Skip getAction if observation timed out
                            move_time += time.time() - start_time
                        else:  # No timeout for observation
                            observation = agent.observationFunction(self.state.deepCopy())
                    except Exception as data:
                        self._agentCrash(agentIndex, quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()

            # If no observation function or it wasn't run, use default state copy
            if observation is None:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    remaining_time = self.rules.getMoveTimeout(agentIndex) - move_time
                    if remaining_time <= 0 and self.rules.getMoveTimeout(agentIndex) > 0:
                        skip_action = True  # Timeout already used up

                    if skip_action:
                        raise TimeoutFunctionException()  # Raise timeout explicitly

                    if self.rules.getMoveTimeout(agentIndex) > 0:
                        timed_func = TimeoutFunction(agent.getAction, remaining_time)
                        try:
                            start_time = time.time()
                            action = timed_func(observation)
                        except TimeoutFunctionException:
                            print(f"Agent {agentIndex} timed out on getAction!", file=sys.stderr)
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return
                    else:  # No move time limit
                        start_time = time.time()
                        action = agent.getAction(observation)

                    move_time += time.time() - start_time

                    # Check move time warnings
                    if move_time > self.rules.getMoveWarningTime(agentIndex):
                        self.totalAgentTimeWarnings[agentIndex] += 1
                        warn_msg = f"Agent {agentIndex} took too long: {move_time:.2f}s. Warning {self.totalAgentTimeWarnings[agentIndex]}."
                        print(warn_msg, file=sys.stderr)
                        if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                            print(f"Agent {agentIndex} exceeded max warnings.", file=sys.stderr)
                            self.agentTimeout = True
                            self._agentCrash(agentIndex, quiet=True)
                            self.unmute()
                            return

                    # Check total time budget
                    self.totalAgentTimes[agentIndex] += move_time
                    if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                        print(f"Agent {agentIndex} exceeded total time: {self.totalAgentTimes[agentIndex]:.2f}s.",
                              file=sys.stderr)
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return

                except Exception as data:
                    self._agentCrash(agentIndex)  # Already handles printing traceback if not quiet
                    self.unmute()
                    return
                finally:
                    self.unmute()  # Ensure unmute happens even if exceptions occur
            else:  # No exception catching
                action = agent.getAction(observation)
                self.unmute()  # Still need to unmute

            # Execute the action
            if action is None:  # Handle case where agent returns None (e.g., error)
                print(f"Agent {agentIndex} returned None action, treating as STOP.", file=sys.stderr)
                action = Directions.STOP

            self.moveHistory.append((agentIndex, action))

            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor(agentIndex, action)
                except Exception as data:
                    self.mute(agentIndex)  # Mute before potential crash handling
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor(agentIndex, action)

            # Update display
            self.display.update(self.state.data)

            # Allow game rules to process the transition
            self.rules.process(self.state, self)

            # Track progress (only count full cycles after all agents moved)
            if agentIndex == numAgents - 1:
                self.numMoves += 1

            # Next agent's turn
            agentIndex = (agentIndex + 1) % numAgents

        # Game Over: Inform agents
        for agentIndex, agent in enumerate(self.agents):
            if agent and hasattr(agent, "final"):
                try:
                    self.mute(agentIndex)
                    if self.catchExceptions:
                        timed_func = TimeoutFunction(agent.final, self.rules.getMaxStartupTime(
                            agentIndex))  # Reuse startup time for final call?
                        try:
                            timed_func(self.state)
                        except TimeoutFunctionException:
                            print(f"Agent {agentIndex} timed out on final() method.", file=sys.stderr)
                    else:
                        agent.final(self.state)
                    self.unmute()
                except Exception as data:
                    if not self.catchExceptions: raise  # Re-raise if not catching
                    self._agentCrash(agentIndex)
                    self.unmute()
                    # Continue informing other agents even if one crashes in final

        # Finish display
        self.display.finish()