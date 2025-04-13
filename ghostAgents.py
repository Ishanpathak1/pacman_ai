# ghostAgents.py
# --------------
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
from game import Actions
from game import Directions
import random
from util import manhattanDistance  # Used by DirectionalGhost
import util  # Used by GhostAgent and DirectionalGhost


class GhostAgent(Agent):
    """
    Base class for ghost agents. Ghosts provide a distribution over possible actions.
    """

    def __init__(self, index):
        """ The ghost agent's index is used to get its state from the GameState. """
        self.index = index

    def getAction(self, state):
        """
        The ghost agent chooses an action from the distribution returned by
        getDistribution. Defaults to STOP if the distribution is empty.
        """
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            # Samples an action according to the distribution
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        """
        Returns a Counter encoding a distribution over actions from the provided state.
        This method must be implemented by subclasses.
        """
        # Subclasses should override this method
        raise NotImplementedError("getDistribution must be implemented by GhostAgent subclasses")


class RandomGhost(GhostAgent):
    """A ghost that chooses a legal action uniformly at random."""

    def getDistribution(self, state):
        """Returns a uniform distribution over legal actions."""
        dist = util.Counter()
        for action in state.getLegalActions(self.index):
            dist[action] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    """A ghost that prefers to rush Pacman, or flee when scared."""

    def __init__(self, index, prob_attack=0.8, prob_scaredFlee=0.8):
        """
        Initializes the directional ghost.

        Args:
            index: The agent index.
            prob_attack: Probability of moving towards Pacman when not scared.
            prob_scaredFlee: Probability of moving away from Pacman when scared.
        """
        super().__init__(index)  # Call parent constructor
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state):
        """
        Returns a distribution favoring attacking Pacman (if not scared) or fleeing (if scared).
        """
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        # Assume speed = 1 for distance calculation, actual speed is handled by game logic
        speed = 1.0

        # Calculate positions after taking each legal action
        actionVectors = [Actions.directionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0] + v[0], pos[1] + v[1]) for v in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Calculate distances to Pacman from potential next positions
        distancesToPacman = [manhattanDistance(new_pos, pacmanPosition) for new_pos in newPositions]

        # Determine best score based on scared state
        if isScared:
            # Flee: Maximize distance
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            # Attack: Minimize distance
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack

        # Identify actions that achieve the best score
        bestActions = [action for action, distance in zip(legalActions, distancesToPacman) if distance == bestScore]

        # Construct the probability distribution over actions
        dist = util.Counter()
        # Assign probability to best actions
        for action in bestActions:
            dist[action] = bestProb / len(bestActions)
        # Assign remaining probability uniformly to all legal actions (including best ones again)
        for action in legalActions:
            dist[action] += (1.0 - bestProb) / len(legalActions)

        # Normalize the distribution to ensure probabilities sum to 1
        dist.normalize()
        return dist