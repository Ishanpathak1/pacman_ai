# layout.py
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

from util import manhattanDistance
from game import Grid, Directions  # Import Directions if needed (removed visibility)
import os
import random


# from functools import reduce # Not needed if visibility cache removed

# Visibility calculation removed as it's complex and often unused for basic search
# VISIBILITY_MATRIX_CACHE = {}

class Layout:
    """
    A Layout manages the static information about the game board: walls, food, capsules,
    agent starting positions.
    """

    def __init__(self, layoutText):
        """
        Initializes the Layout from a list of strings representing the maze rows.
        """
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.capsules = []
        self.agentPositions = []  # List of (agent_index/is_pacman_flag, (x, y)) tuples
        self.numGhosts = 0
        self.layoutText = layoutText  # Store original text
        self.processLayoutText(layoutText)  # Parse the text representation
        self.totalFood = len(self.food.asList())
        # Visibility matrix initialization removed
        # self.initializeVisibilityMatrix()

    def getNumGhosts(self):
        """ Returns the number of ghosts specified in the layout. """
        return self.numGhosts

    # Visibility matrix calculation and related methods removed
    # def initializeVisibilityMatrix(self): ...
    # def isVisibleFrom(self, ghostPos, pacPos, pacDirection): ...

    def isWall(self, pos):
        """ Returns true if the position (x, y) is a wall. """
        x, y = pos  # Unpack tuple
        # Check boundaries first
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False  # Treat out-of-bounds as not a wall for some logic? Or True? Depends. Let's assume False.
        return self.walls[x][y]

    def getRandomLegalPosition(self):
        """ Returns a random non-wall position on the board. """
        # Ensure width/height > 0
        if self.width <= 0 or self.height <= 0: return None

        x = random.randrange(self.width)
        y = random.randrange(self.height)
        # Loop until a non-wall position is found
        while self.isWall((x, y)):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
        return (x, y)

    def getRandomCorner(self):
        """ Returns a random one of the four corners. """
        # Assumes corners are inset from the boundary
        # Consider checking if corners are valid/not walls if layouts vary
        h = self.height
        w = self.width
        # Ensure corners are within bounds if map is very small
        corners = [(1, 1), (1, max(1, h - 2)), (max(1, w - 2), 1), (max(1, w - 2), max(1, h - 2))]
        # Filter out corners that might be walls (optional, depends on expected layouts)
        # legal_corners = [p for p in corners if not self.isWall(p)]
        # if not legal_corners: return self.getRandomLegalPosition() # Fallback
        return random.choice(corners)  # Return random choice from original list

    def getFurthestCorner(self, pacPos):
        """ Returns the corner furthest from the given position (using Manhattan distance). """
        h = self.height
        w = self.width
        corners = [(1, 1), (1, max(1, h - 2)), (max(1, w - 2), 1), (max(1, w - 2), max(1, h - 2))]

        # Find the corner with the maximum Manhattan distance
        maxDist = -1
        bestPos = None
        for pos in corners:
            dist = manhattanDistance(pos, pacPos)
            if dist > maxDist:
                maxDist = dist
                bestPos = pos
        return bestPos

    def __str__(self):
        """ Returns the original layout text. """
        return "\n".join(self.layoutText)

    def deepCopy(self):
        """ Creates a new Layout object with the same layout text. """
        # Layouts are immutable once created, so a new object is sufficient
        return Layout(self.layoutText[:])

    def processLayoutText(self, layoutText):
        """
        Processes the layout text and populates walls, food, capsules, agents.
        Coordinates are flipped from (row, col) in text file to (x, y) convention
        where (0,0) is bottom-left.

        Layout Characters:
         % - Wall
         . - Food
         o - Capsule
         G - Ghost
         P - Pacman
         1-4 - Numbered Ghost (sometimes used for different behaviors)
        """
        maxY = self.height - 1
        pacmanIndex = 0  # Track Pacman index for sorting
        ghostIndex = 1  # Start ghost indices from 1

        tempAgentPositions = []  # Store positions before assigning indices

        for y in range(self.height):
            for x in range(self.width):
                # Read character from the reversed row index
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar, tempAgentPositions)  # Pass list to modify

        # Sort agents: Pacman (index 0) first, then ghosts by parsed order/number
        # Assign final indices based on sorted order
        agent_details = []
        for detail in tempAgentPositions:
            # Detail could be ('P', pos) or ('G', pos) or (num_str, pos)
            char_or_num, pos = detail
            if char_or_num == 'P':
                agent_details.append({'type': 'P', 'order': -1, 'pos': pos})  # Pacman always first
            elif char_or_num == 'G':
                agent_details.append({'type': 'G', 'order': ghostIndex, 'pos': pos})
                ghostIndex += 1
            elif char_or_num in ['1', '2', '3', '4']:
                # Use explicit number for sorting order, ensure ghostIndex advances past it
                num = int(char_or_num)
                agent_details.append({'type': 'G', 'order': num, 'pos': pos})
                ghostIndex = max(ghostIndex, num + 1)
                # Ignore other characters

        # Sort based on 'order' key
        agent_details.sort(key=lambda item: item['order'])

        # Assign final isPacman flag and position
        finalAgentPositions = []
        for i, agent in enumerate(agent_details):
            isPacman = (agent['type'] == 'P')
            # The final list stores (isPacman_boolean, position_tuple)
            finalAgentPositions.append((isPacman, agent['pos']))

        self.agentPositions = finalAgentPositions

    def processLayoutChar(self, x, y, layoutChar, tempAgentPositions):
        """ Helper function to process a single character from the layout text. """
        if layoutChar == '%':
            self.walls[x][y] = True
        elif layoutChar == '.':
            self.food[x][y] = True
        elif layoutChar == 'o':
            self.capsules.append((x, y))
        elif layoutChar == 'P':
            # Store 'P' marker and position temporarily
            tempAgentPositions.append(('P', (x, y)))
        elif layoutChar == 'G':
            # Store 'G' marker and position
            tempAgentPositions.append(('G', (x, y)))
            self.numGhosts += 1
        elif layoutChar in ['1', '2', '3', '4']:
            # Store digit marker and position
            tempAgentPositions.append((layoutChar, (x, y)))
            self.numGhosts += 1
        # Ignore other characters like spaces


def getLayout(name, back=2):
    """
    Loads a layout file given its name. Searches in layouts/ folder first,
    then current directory, then recursively searches parent directories.
    """
    layout = None
    # Prioritize .lay extension if not present
    name_with_ext = name if name.endswith('.lay') else name + '.lay'

    # Check common locations
    locations_to_try = [
        os.path.join('layouts', name_with_ext),  # layouts/name.lay
        name_with_ext,  # name.lay (in current dir)
        os.path.join('layouts', name),  # layouts/name (without extension)
        name  # name (without extension)
    ]

    for fullname in locations_to_try:
        layout = tryToLoad(fullname)
        if layout is not None: break  # Stop if found

    # Recursive backup search (limited depth)
    if layout is None and back >= 0:
        try:
            curdir = os.path.abspath('.')
            parentdir = os.path.dirname(curdir)
            # Avoid infinite loop if already at root
            if parentdir != curdir:
                os.chdir(parentdir)
                layout = getLayout(name, back - 1)  # Recursive call
                os.chdir(curdir)  # Change back to original directory
        except OSError:
            pass  # Ignore errors changing directory (e.g., permissions)

    if layout is None:
        print(f"Warning: Could not load layout '{name}'", file=sys.stderr)

    return layout


def tryToLoad(fullname):
    """ Attempts to load a layout file. Returns None if file not found or error occurs. """
    if not os.path.exists(fullname): return None
    try:
        with open(fullname, 'r') as f:  # Use 'with' for automatic file closing
            # Read lines, stripping whitespace, ignore empty lines
            lines = [line.strip() for line in f if line.strip()]
            if not lines: return None  # Handle empty file
            return Layout(lines)
    except IOError as e:
        print(f"Warning: Error reading layout file '{fullname}': {e}", file=sys.stderr)
        return None
    except Exception as e:  # Catch other potential errors during Layout init
        print(f"Warning: Error processing layout file '{fullname}': {e}", file=sys.stderr)
        return None