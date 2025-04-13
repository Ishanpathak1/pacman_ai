# graphicsDisplay.py
# ------------------
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


from graphicsUtils import *
import math, time
from game import Directions, Grid  # Be specific about imports from game

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Based on code by Dan Klein and John DeNero, UC Berkeley.
# Some code adapted from a Pacman implementation by LiveWires.

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = formatColor(0, 0, 0)
WALL_COLOR = formatColor(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0)
INFO_PANE_COLOR = formatColor(.4, .4, 0)
SCORE_COLOR = formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 2
PACMAN_CAPTURE_OUTLINE_WIDTH = 4  # Used for capture the flag version

# Ghost Colors
GHOST_COLORS = [
    formatColor(.9, 0, 0),  # Red
    formatColor(0, .3, .9),  # Blue
    formatColor(.98, .41, .07),  # Orange
    formatColor(.1, .75, .7),  # Green
    formatColor(1.0, 0.6, 0.0),  # Yellow
    formatColor(.4, 0.13, 0.91)  # Purple
]
TEAM_COLORS = GHOST_COLORS[:2]  # For capture the flag
SCARED_COLOR = formatColor(1, 1, 1)  # White for scared ghosts
GHOST_VEC_COLORS = list(map(colorToVector, GHOST_COLORS))  # Used for distribution display

# Ghost Shape definition
GHOST_SHAPE = [
    (0, 0.3), (0.25, 0.75), (0.5, 0.3), (0.75, 0.75),
    (0.75, -0.5), (0.5, -0.75), (-0.5, -0.75), (-0.75, -0.5),
    (-0.75, 0.75), (-0.5, 0.3), (-0.25, 0.75)
]
GHOST_SIZE = 0.65  # Scale factor for ghost drawing

# Pacman Color and Scale
PACMAN_COLOR = formatColor(255.0 / 255.0, 255.0 / 255.0, 61.0 / 255)  # Yellow
PACMAN_SCALE = 0.5

# Food Color and Size
FOOD_COLOR = formatColor(1, 1, 1)
FOOD_SIZE = 0.1

# Capsule Color and Size
CAPSULE_COLOR = formatColor(1, 1, 1)
CAPSULE_SIZE = 0.25

# Wall drawing constants
WALL_RADIUS = 0.15


class InfoPane:
    """ Displays the score """

    def __init__(self, layout, gridSize):
        self.gridSize = gridSize
        self.width = (layout.width) * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 24
        self.textColor = PACMAN_COLOR
        self.drawPane()

    def toScreen(self, pos, y=None):
        """ Translates a point relative from the bottom left of the info pane. """
        if y is None:  # Allow passing tuple or separate x, y
            x, y = pos
        else:
            x = pos
        # Position relative to the bottom-left of the main grid area
        x = self.gridSize + x  # Add left margin
        y = self.base + y
        return x, y

    def drawPane(self):
        self.scoreText = text(self.toScreen(0, 0), self.textColor, "SCORE:    0", "Times", self.fontSize, "bold")
        # Ghost distance text initialization removed, potentially added back if capture mode needed

    def updateScore(self, score):
        changeText(self.scoreText, "SCORE: % 4d" % score)

    # Methods related to team/ghost distances removed as likely not needed for basic Pacman search
    # def setTeam(self, isBlue): ...
    # def initializeGhostDistances(self, distances): ...
    # def updateGhostDistances(self, distances): ...
    # def drawGhost(self): pass
    # def drawPacman(self): pass
    # def drawWarning(self): pass
    # def clearIcon(self): pass
    # def updateMessage(self, message): pass
    # def clearMessage(self): pass


class PacmanGraphics:
    """ Handles the graphics generation for Pacman display. """

    def __init__(self, zoom=1.0, frameTime=0.0, capture=False):
        self.have_window = 0
        self.currentGhostImages = {}  # Stores graphics objects for ghosts
        self.pacmanImage = None  # Stores graphics objects for Pacman
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.capture = capture  # Flag for capture-the-flag variant styling
        self.frameTime = frameTime  # Delay between frames for animation

    def checkNullDisplay(self):
        """ Returns False for graphical display, True for null display """
        return False

    def initialize(self, state, isBlue=False):
        """ Creates the graphics window and draws the initial state. """
        self.isBlue = isBlue  # Used in capture the flag
        self.startGraphics(state)
        self.distributionImages = None  # For displaying belief distributions (optional)
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)
        # Store previous state for animation purposes
        self.previousState = state

    def startGraphics(self, state):
        """ Creates the main graphics window. """
        self.layout = state.layout
        self.width = self.layout.width
        self.height = self.layout.height
        # Calculate window dimensions
        screen_width = (self.width + 2) * self.gridSize  # Add margins
        screen_height = (self.height + 3) * self.gridSize + INFO_PANE_HEIGHT  # Add margins and info pane

        self.make_window(screen_width, screen_height)
        self.infoPane = InfoPane(self.layout, self.gridSize)
        self.currentState = self.layout  # Store layout for reference

    def make_window(self, width, height):
        """ Internal call to create the graphics window. """
        if self.have_window == 0:
            self.have_window = 1
            begin_graphics(int(width), int(height), BACKGROUND_COLOR, "Pacman")

    def drawStaticObjects(self, state):
        """ Draws walls, food, capsules - things that don't move """
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        refresh()  # Update the display

    def drawAgentObjects(self, state):
        """ Draws Pacman and ghosts in their initial positions """
        self.agentImages = []  # Stores (agentState, image_parts_list) tuples
        for index, agent in enumerate(state.agentStates):
            if agent.isPacman:
                image = self.drawPacman(agent, index)
                self.agentImages.append((agent, image))
            else:
                image = self.drawGhost(agent, index)
                self.agentImages.append((agent, image))
        refresh()  # Update the display

    def swapImages(self, agentIndex, newState):
        """ Changes agent image, e.g., ghost to Pacman in capture the flag """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage: remove_from_screen(item)  # Remove old image parts
        if newState.isPacman:
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        refresh()

    def update(self, newState):
        """ Updates the display based on the new game state. """
        # Identify which agent moved
        agentIndex = newState._agentMoved
        agentState = newState.agentStates[agentIndex]

        # Check if agent type changed (for capture the flag)
        if self.agentImages[agentIndex][0].isPacman != agentState.isPacman:
            self.swapImages(agentIndex, agentState)

        # Get previous state and image for animation/movement
        prevState, prevImage = self.agentImages[agentIndex]

        # Animate or move the agent
        if agentState.isPacman:
            self.animatePacman(agentState, prevState, prevImage)
        else:
            self.moveGhost(agentState, agentIndex, prevState, prevImage)

        # Store the updated state and image reference
        self.agentImages[agentIndex] = (agentState, prevImage)

        # Update food display
        if newState._foodEaten is not None:
            self.removeFood(newState._foodEaten, self.food)
        # Update capsule display
        if newState._capsuleEaten is not None:
            self.removeCapsule(newState._capsuleEaten, self.capsules)

        # Update score
        self.infoPane.updateScore(newState.score)

        # Update ghost distances if applicable (for capture the flag)
        # if hasattr(newState, 'ghostDistances'):
        #    self.infoPane.updateGhostDistances(newState.ghostDistances)

    def drawPacman(self, pacman, index):
        """ Draws Pacman agent """
        position = self.getPosition(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(pacman))

        # Determine colors based on capture mode or standard
        width = PACMAN_OUTLINE_WIDTH
        outlineColor = PACMAN_COLOR
        fillColor = PACMAN_COLOR
        if self.capture:  # Apply team colors if capture the flag
            outlineColor = TEAM_COLORS[index % 2]
            fillColor = GHOST_COLORS[index]  # Use ghost color for Pacman? Check CTF rules
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        # Create circle graphic for Pacman
        return [circle(screen_point, PACMAN_SCALE * self.gridSize,
                       fillColor=fillColor, outlineColor=outlineColor,
                       endpoints=endpoints,  # Creates the mouth effect
                       width=width)]

    def getEndpoints(self, direction, position=(0, 0)):
        """ Calculates the start and end angles for Pacman's mouth arc """
        x, y = position
        # Calculate mouth angle based on fraction of movement within a grid cell
        # Creates a 'wobbling' effect for the mouth
        pos = (x - int(x)) + (y - int(y))
        width = 30 + 80 * math.sin(math.pi * pos)  # Angle width varies sinusoidally

        delta = width / 2.0  # Half-angle for symmetry
        if direction == Directions.WEST:
            endpoints = (180 + delta, 180 - delta)
        elif direction == Directions.NORTH:
            endpoints = (90 + delta, 90 - delta)
        elif direction == Directions.SOUTH:
            endpoints = (270 + delta, 270 - delta)
        else:  # Default EAST
            endpoints = (0 + delta, 0 - delta)
        return endpoints

    def movePacman(self, position, direction, image):
        """ Moves the Pacman circle graphic to a new position """
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints(direction, position)
        radius = PACMAN_SCALE * self.gridSize
        moveCircle(image[0], screenPosition, radius, endpoints)  # Update circle position and endpoints
        refresh()

    def animatePacman(self, pacman, prevPacman, image):
        """ Animates Pacman moving from previous state to current state """
        if self.frameTime < 0:  # Manual stepping mode
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1  # Switch to automated animation

        if self.frameTime > 0.01:  # Animate if frame time is significant
            frames = 4.0  # Number of intermediate frames
            start_time = time.time()
            fx, fy = self.getPosition(prevPacman)
            px, py = self.getPosition(pacman)

            # Interpolate position over frames
            for i in range(1, int(frames) + 1):
                pos = (px * i / frames + fx * (frames - i) / frames,
                       py * i / frames + fy * (frames - i) / frames)
                self.movePacman(pos, self.getDirection(pacman), image)
                refresh()
                # Calculate sleep time to match frameTime budget
                elapsed = time.time() - start_time
                target_time = (abs(self.frameTime) / frames) * i
                sleep_time = max(0, target_time - elapsed)
                sleep(sleep_time)
        else:  # If frameTime is very small, just jump to final position
            self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)
        refresh()

    def getGhostColor(self, ghost, ghostIndex):
        """ Determines the ghost's color based on scared state """
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            # Use modulo for ghost index in case more ghosts than defined colors
            return GHOST_COLORS[ghostIndex % len(GHOST_COLORS)]

    def drawGhost(self, ghost, agentIndex):
        """ Draws a ghost agent """
        pos = self.getPosition(ghost)
        direction = self.getDirection(ghost)
        screen_x, screen_y = self.to_screen(pos)

        # Define coordinates for the ghost polygon shape relative to center
        coords = []
        for (x, y) in GHOST_SHAPE:
            coords.append((x * self.gridSize * GHOST_SIZE + screen_x,
                           y * self.gridSize * GHOST_SIZE + screen_y))

        colour = self.getGhostColor(ghost, agentIndex)
        body = polygon(coords, colour, filled=1)  # Main body shape

        # Draw eyes
        eyeColor = formatColor(1.0, 1.0, 1.0)  # White
        pupilColor = formatColor(0.0, 0.0, 0.0)  # Black

        # Eye position adjustments based on direction
        dx = 0;
        dy = 0
        if direction == Directions.NORTH: dy = -0.2
        if direction == Directions.SOUTH: dy = 0.2
        if direction == Directions.EAST:  dx = 0.2
        if direction == Directions.WEST:  dx = -0.2

        # Calculate eye and pupil positions
        eyeRadius = self.gridSize * GHOST_SIZE * 0.2
        pupilRadius = self.gridSize * GHOST_SIZE * 0.08
        eyeOffsetX = self.gridSize * GHOST_SIZE * 0.3
        eyeOffsetY = self.gridSize * GHOST_SIZE * 0.3  # Relative to center y

        leftEyePos = (screen_x + eyeOffsetX * (-1) + dx * eyeRadius * 1.5,  # Adjust pupil based on dx too?
                      screen_y - eyeOffsetY + dy * eyeRadius * 1.5)
        rightEyePos = (screen_x + eyeOffsetX * (1) + dx * eyeRadius * 1.5,
                       screen_y - eyeOffsetY + dy * eyeRadius * 1.5)
        leftPupilPos = (screen_x + eyeOffsetX * (-1) + dx * eyeRadius * 2.5,  # Adjust pupil position further?
                        screen_y - eyeOffsetY + dy * eyeRadius * 2.5)
        rightPupilPos = (screen_x + eyeOffsetX * (1) + dx * eyeRadius * 2.5,
                         screen_y - eyeOffsetY + dy * eyeRadius * 2.5)

        # Create graphics objects for eyes and pupils
        leftEye = circle(leftEyePos, eyeRadius, eyeColor, eyeColor)
        rightEye = circle(rightEyePos, eyeRadius, eyeColor, eyeColor)
        leftPupil = circle(leftPupilPos, pupilRadius, pupilColor, pupilColor)
        rightPupil = circle(rightPupilPos, pupilRadius, pupilColor, pupilColor)

        # Return list of all ghost image parts
        ghostImageParts = [body, leftEye, rightEye, leftPupil, rightPupil]
        return ghostImageParts

    def moveEyes(self, pos, direction, eyes):
        """ Moves the pupils of the ghost based on direction """
        screen_x, screen_y = self.to_screen(pos)

        # Calculate movement delta based on direction
        dx = 0;
        dy = 0
        if direction == Directions.NORTH: dy = -0.2
        if direction == Directions.SOUTH: dy = 0.2
        if direction == Directions.EAST:  dx = 0.2
        if direction == Directions.WEST:  dx = -0.2

        # Calculate new positions (similar logic to drawGhost eyes)
        eyeRadius = self.gridSize * GHOST_SIZE * 0.2
        pupilRadius = self.gridSize * GHOST_SIZE * 0.08
        eyeOffsetX = self.gridSize * GHOST_SIZE * 0.3
        eyeOffsetY = self.gridSize * GHOST_SIZE * 0.3

        leftEyePos = (screen_x + eyeOffsetX * (-1) + dx * eyeRadius * 1.5,
                      screen_y - eyeOffsetY + dy * eyeRadius * 1.5)
        rightEyePos = (screen_x + eyeOffsetX * (1) + dx * eyeRadius * 1.5,
                       screen_y - eyeOffsetY + dy * eyeRadius * 1.5)
        leftPupilPos = (screen_x + eyeOffsetX * (-1) + dx * eyeRadius * 2.5,
                        screen_y - eyeOffsetY + dy * eyeRadius * 2.5)
        rightPupilPos = (screen_x + eyeOffsetX * (1) + dx * eyeRadius * 2.5,
                         screen_y - eyeOffsetY + dy * eyeRadius * 2.5)

        # Move the graphics objects
        moveCircle(eyes[0], leftEyePos, eyeRadius)  # Left Eye White
        moveCircle(eyes[1], rightEyePos, eyeRadius)  # Right Eye White
        moveCircle(eyes[2], leftPupilPos, pupilRadius)  # Left Pupil Black
        moveCircle(eyes[3], rightPupilPos, pupilRadius)  # Right Pupil Black

    def moveGhost(self, ghost, ghostIndex, prevGhost, ghostImageParts):
        """ Animates the ghost movement and color changes """
        # Calculate screen delta
        old_x, old_y = self.to_screen(self.getPosition(prevGhost))
        new_x, new_y = self.to_screen(self.getPosition(ghost))
        delta = new_x - old_x, new_y - old_y

        # Move all parts of the ghost image
        for ghostImagePart in ghostImageParts:
            move_by(ghostImagePart, delta)

        # Update color based on scared timer
        newColor = self.getGhostColor(ghost, ghostIndex)
        edit(ghostImageParts[0], fillColor=newColor, outlineColor=newColor)  # Edit body color

        # Move the eyes to follow direction
        self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[1:])  # Pass eye parts

        refresh()  # Update display

    def getPosition(self, agentState):
        """ Gets the position from an agent state, handling None configurations """
        if agentState.configuration is None: return (-1000, -1000)  # Off-screen
        return agentState.getPosition()

    def getDirection(self, agentState):
        """ Gets the direction from an agent state, handling None configurations """
        if agentState.configuration is None: return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self):
        """ Closes the graphics window """
        end_graphics()

    def to_screen(self, point):
        """ Converts game coordinates (x, y) to screen coordinates """
        x, y = point
        # Adjust y origin and scale by gridSize, add margin
        screen_x = (x + 1) * self.gridSize
        screen_y = (self.height - y) * self.gridSize
        return (screen_x, screen_y)

    # to_screen2 seems redundant, removing it. Use to_screen consistently.
    # def to_screen2(self, point): ...

    # Replace the existing drawWalls function with this one:
    def drawWalls(self, wallMatrix):
        """ Draws the maze walls based on the wall matrix """
        wallColor = WALL_COLOR
        for xNum in range(wallMatrix.width):
            # Optional: Apply team colors if capture the flag
            if self.capture:
                if (xNum * 2) < wallMatrix.width:
                    wallColor = TEAM_COLORS[0]
                elif (xNum * 2) >= wallMatrix.width:
                    wallColor = TEAM_COLORS[1]
                # else: wallColor = WALL_COLOR # Removed potential center line logic

            for yNum in range(wallMatrix.height):
                if wallMatrix[xNum][yNum]:  # If there is a wall at (xNum, yNum)
                    pos = (xNum, yNum)
                    screen = self.to_screen(pos)  # Use the primary conversion

                    # Check adjacent cells
                    wIsWall = self.isWall(xNum - 1, yNum, wallMatrix)
                    eIsWall = self.isWall(xNum + 1, yNum, wallMatrix)
                    nIsWall = self.isWall(xNum, yNum + 1, wallMatrix)
                    sIsWall = self.isWall(xNum, yNum - 1, wallMatrix)
                    nwIsWall = self.isWall(xNum - 1, yNum + 1, wallMatrix)
                    swIsWall = self.isWall(xNum - 1, yNum - 1, wallMatrix)
                    neIsWall = self.isWall(xNum + 1, yNum + 1, wallMatrix)
                    seIsWall = self.isWall(xNum + 1, yNum - 1, wallMatrix)

                    # Wall drawing logic using lines and arcs based on neighbors
                    # Using screen coordinates directly now, applying offsets for arcs/lines
                    radius = WALL_RADIUS * self.gridSize
                    halfGrid = 0.5 * self.gridSize

                    # NE quadrant
                    if (not nIsWall) and (not eIsWall):  # Inner corner
                        circle(screen, radius, wallColor, wallColor, (0, 91), 'arc')
                    elif (nIsWall) and (not eIsWall):  # Vertical line up from center right
                        line(add(screen, (radius, -radius)), add(screen, (radius, -halfGrid)), wallColor)
                    elif (not nIsWall) and (eIsWall):  # Horizontal line right from center top
                        line(add(screen, (radius, -radius)), add(screen, (halfGrid, -radius)), wallColor)
                    elif (nIsWall) and (eIsWall) and (not neIsWall):  # Outer corner
                        # Adjust circle center for outer corner
                        circle(add(screen, (radius, -radius)), radius, wallColor, wallColor, (180, 271), 'arc')

                        # NW quadrant
                    if (not nIsWall) and (not wIsWall):  # Inner corner
                        circle(screen, radius, wallColor, wallColor, (90, 181), 'arc')
                    elif (nIsWall) and (not wIsWall):  # Vertical line up from center left
                        line(add(screen, (-radius, -radius)), add(screen, (-radius, -halfGrid)), wallColor)
                    elif (not nIsWall) and (wIsWall):  # Horizontal line left from center top
                        line(add(screen, (-radius, -radius)), add(screen, (-halfGrid, -radius)), wallColor)
                    elif (nIsWall) and (wIsWall) and (not nwIsWall):  # Outer corner
                        circle(add(screen, (-radius, -radius)), radius, wallColor, wallColor, (270, 361), 'arc')

                    # SE quadrant
                    if (not sIsWall) and (not eIsWall):  # Inner corner
                        circle(screen, radius, wallColor, wallColor, (270, 361), 'arc')
                    elif (sIsWall) and (not eIsWall):  # Vertical line down from center right
                        line(add(screen, (radius, radius)), add(screen, (radius, halfGrid)), wallColor)
                    elif (not sIsWall) and (eIsWall):  # Horizontal line right from center bottom
                        line(add(screen, (radius, radius)), add(screen, (halfGrid, radius)), wallColor)
                    elif (sIsWall) and (eIsWall) and (not seIsWall):  # Outer corner
                        circle(add(screen, (radius, radius)), radius, wallColor, wallColor, (90, 181), 'arc')

                    # SW quadrant
                    if (not sIsWall) and (not wIsWall):  # Inner corner
                        circle(screen, radius, wallColor, wallColor, (180, 271), 'arc')
                    elif (sIsWall) and (not wIsWall):  # Vertical line down from center left
                        line(add(screen, (-radius, radius)), add(screen, (-radius, halfGrid)), wallColor)
                    elif (not sIsWall) and (wIsWall):  # Horizontal line left from center bottom
                        line(add(screen, (-radius, radius)), add(screen, (-halfGrid, radius)), wallColor)
                    elif (sIsWall) and (wIsWall) and (not swIsWall):  # Outer corner
                        circle(add(screen, (-radius, radius)), radius, wallColor, wallColor, (0, 91), 'arc')
    def isWall(self, x, y, walls):
        """ Checks if the coordinate (x, y) is a wall, handling boundary conditions. """
        if x < 0 or y < 0: return False
        if x >= walls.width or y >= walls.height: return False
        return walls[x][y]

    def drawFood(self, foodMatrix):
        """ Draws the food pellets """
        foodImages = Grid(foodMatrix.width, foodMatrix.height, initialValue=None)  # Store image refs in grid
        for xNum in range(foodMatrix.width):
            # Optional: team colors for food in capture the flag
            color = FOOD_COLOR
            if self.capture:
                if (xNum * 2) <= foodMatrix.width:
                    color = TEAM_COLORS[0]
                elif (xNum * 2) > foodMatrix.width:
                    color = TEAM_COLORS[1]

            for yNum in range(foodMatrix.height):
                if foodMatrix[xNum][yNum]:  # If food exists at (xNum, yNum)
                    screen = self.to_screen((xNum, yNum))
                    dot = circle(screen, FOOD_SIZE * self.gridSize,
                                 outlineColor=color, fillColor=color, width=1)
                    foodImages[xNum][yNum] = dot  # Store reference to the graphics object
        return foodImages

    def drawCapsules(self, capsules):
        """ Draws the power capsules """
        capsuleImages = {}  # Dictionary mapping capsule position to image object
        for capsule_pos in capsules:
            screen_pos = self.to_screen(capsule_pos)
            dot = circle(screen_pos, CAPSULE_SIZE * self.gridSize,
                         outlineColor=CAPSULE_COLOR, fillColor=CAPSULE_COLOR, width=1)
            capsuleImages[capsule_pos] = dot
        return capsuleImages

    def removeFood(self, cell, foodImages):
        """ Removes the graphic for a specific food dot """
        x, y = cell
        if foodImages[x][y] is not None:
            remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell, capsuleImages):
        """ Removes the graphic for a specific capsule """
        if cell in capsuleImages:
            remove_from_screen(capsuleImages[cell])

    def drawExpandedCells(self, cells):
        """ Draws an overlay highlighting cells visited by a search algorithm """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]  # Red base color
        self.clearExpandedCells()  # Clear previous overlay
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            # Color intensity based on order of expansion (later cells are brighter red)
            cellColor = formatColor(*[(n - k) * c * 0.5 / n + 0.25 for c in baseColor])
            block = square(screenPos, 0.5 * self.gridSize, color=cellColor, filled=1, behind=2)  # Draw behind agents
            self.expandedCells.append(block)
            if self.frameTime < 0:  # Refresh immediately if stepping manually
                refresh()

    def clearExpandedCells(self):
        """ Clears the search expansion overlay """
        if hasattr(self, 'expandedCells') and self.expandedCells:
            for cell in self.expandedCells:
                remove_from_screen(cell)
            self.expandedCells = []

    def updateDistributions(self, distributions):
        """ Draws belief distributions for agents (e.g., ghost positions) """
        # Lazily initialize distribution images if not already done
        if self.distributionImages is None:
            self.drawDistributions(self.previousState)

        # Update color of each grid cell based on belief weights
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                # Get belief weights for this cell from all distributions
                weights = [dist.get((x, y), 0.0) for dist in distributions]  # Use get with default 0.0

                # Calculate blended color based on weights and agent colors
                if sum(weights) > 0.0001:  # Avoid division by zero if sum is tiny
                    # Determine base color (usually Pacman/Ghost colors)
                    colors = GHOST_VEC_COLORS[1:]  # Default: Ghost colors
                    if self.capture: colors = GHOST_VEC_COLORS  # Use all colors in capture

                    # Blend colors based on weights
                    blended_color = [0.0, 0.0, 0.0]
                    total_weight = sum(weights)
                    if total_weight > 0:  # Normalize weights implicitly
                        for weight, agent_color_vec in zip(weights, colors):
                            # Weighted average, scaling intensity
                            intensity_factor = 0.95 * (weight / total_weight) ** 0.3
                            blended_color = [min(1.0, c + intensity_factor * g_comp)
                                             for c, g_comp in zip(blended_color, agent_color_vec)]

                    changeColor(image, formatColor(*blended_color))
                else:  # If no belief weight, use background color
                    changeColor(image, BACKGROUND_COLOR)
        refresh()

    def drawDistributions(self, state):
        """ Draws the initial grid for belief distributions (usually blank squares) """
        walls = state.layout.walls
        distImages = Grid(walls.width, walls.height, initialValue=None)
        for x in range(walls.width):
            for y in range(walls.height):
                screen_pos = self.to_screen((x, y))
                block = square(screen_pos, 0.5 * self.gridSize, color=BACKGROUND_COLOR, filled=1, behind=2)
                distImages[x][y] = block
        self.distributionImages = distImages


# First person view graphics (not commonly used for search)
class FirstPersonPacmanGraphics(PacmanGraphics):
    # ... (Implementation largely unchanged, could be removed if not needed) ...
    pass  # Keeping minimal structure for now


def add(x, y):
    """ Utility function to add two tuples element-wise """
    return (x[0] + y[0], x[1] + y[1])