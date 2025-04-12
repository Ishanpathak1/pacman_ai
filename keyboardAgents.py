# keyboardAgents.py
# -----------------
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

from game import Agent
from game import Directions
import random
# Used to read keyboard state from the graphics window
from graphicsUtils import keys_waiting, keys_pressed


class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard (W, A, S, D keys or Arrow Keys).
    'q' can be used to stop Pacman.
    """
    # Default key bindings
    WEST_KEY = 'a'
    EAST_KEY = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__(self, index=0):
        """ Initializes the keyboard agent. """
        super().__init__(index)  # Initialize base Agent class
        self.lastMove = Directions.STOP  # Store the last executed move
        self.keys = set()  # Store the set of currently pressed keys

    def getAction(self, state):
        """
        Gets an action from the keyboard input.
        Prefers the last move if no key is pressed but the last move is legal.
        Chooses randomly if the selected key corresponds to an illegal move.
        """
        # Get currently pressed keys from the graphics interface
        new_keys = set(keys_waiting() + keys_pressed())
        if new_keys:  # Update stored keys only if there's new input
            self.keys = new_keys

        # Get legal actions for this agent
        legal_actions = state.getLegalActions(self.index)

        # Determine the intended move based on current keys
        move = self.getMove(legal_actions)

        # Handle STOP key explicitly
        if (self.STOP_KEY in self.keys) and Directions.STOP in legal_actions:
            move = Directions.STOP

        # If STOP was intended or no valid key is pressed, try repeating the last move
        if move == Directions.STOP:
            if self.lastMove in legal_actions:
                move = self.lastMove

        # If the determined move is illegal, choose a random legal action
        # (This handles cases like trying to move into a wall)
        if move not in legal_actions:
            move = random.choice(legal_actions)

        # Store the chosen move and return it
        self.lastMove = move
        return move

    def getMove(self, legal_actions):
        """ Determines the direction based on pressed keys and legal actions. """
        move = Directions.STOP  # Default to STOP
        # Check WASD and Arrow keys against legal actions
        if (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal_actions:
            move = Directions.WEST
        if (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal_actions:
            # Use elif to prioritize (e.g., if both Left and Right are pressed)
            # or handle this based on which key was pressed last if needed.
            # Simple approach: last condition checked wins.
            move = Directions.EAST
        if (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal_actions:
            move = Directions.NORTH
        if (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal_actions:
            move = Directions.SOUTH

        return move

# Removing KeyboardAgent2 as it's likely not needed for the project
# If two-player keyboard control is ever desired, it can be added back.
# class KeyboardAgent2(KeyboardAgent): ...