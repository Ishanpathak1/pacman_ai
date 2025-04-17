import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from collections import deque
from pacman import GameState
from pacmanAgents import Directions
from layout import getLayout
from graphicsDisplay import PacmanGraphics
from game import Actions

# Map directions to indices
action_map = [Directions.NORTH, Directions.SOUTH, Directions.WEST, Directions.EAST]

class QNetwork(nn.Module):
    def __init__(self, input_size=7, hidden_size=64):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, 1)  # Q-value output

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        return self.fc2(x)

class DeepQLearningAgent:
    def __init__(self, alpha=0.01, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.05):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.model = QNetwork()
        self.optimizer = optim.Adam(self.model.parameters(), lr=alpha)
        self.loss_fn = nn.MSELoss()
        self.actions = action_map
        self.episode_rewards = []

    def get_legal_actions(self, state):
        return state.getLegalActions(0)

    def extract_features(self, state, action):
        from util import manhattanDistance
        pos = state.getPacmanPosition()
        x, y = pos

        dx, dy = Actions.directionToVector(action)
        new_pos = (int(x + dx), int(y + dy))

        food = state.getFood().asList()
        capsules = state.getCapsules()
        ghosts = [g.getPosition() for g in state.getGhostStates() if not g.scaredTimer]
        scared_ghosts = [g.getPosition() for g in state.getGhostStates() if g.scaredTimer > 0]

        def nearest(pos_list):
            return min([manhattanDistance(new_pos, f) for f in pos_list], default=10)

        features = [
            nearest(food) / 10.0,
            nearest(capsules) / 10.0,
            nearest(ghosts) / 10.0,
            nearest(scared_ghosts) / 10.0,
            1.0 if action == state.getPacmanState().getDirection() else 0.0,
            float(len(food)) / 100.0,
            float(sum(g.scaredTimer for g in state.getGhostStates())) / 40.0
        ]
        return torch.tensor(features, dtype=torch.float32)

    def choose_action(self, state, explore=True):
        legal = self.get_legal_actions(state)
        if Directions.STOP in legal: legal.remove(Directions.STOP)

        if explore and random.random() < self.epsilon:
            return random.choice(legal)

        q_vals = {}
        for action in legal:
            features = self.extract_features(state, action)
            q_vals[action] = self.model(features.unsqueeze(0)).item()

        return max(q_vals, key=q_vals.get)

    def update(self, state, action, reward, next_state):
        features = self.extract_features(state, action)
        current_q = self.model(features.unsqueeze(0))

        next_q = -float('inf')
        legal_next = self.get_legal_actions(next_state)
        if Directions.STOP in legal_next: legal_next.remove(Directions.STOP)
        if legal_next:
            next_q = max([self.model(self.extract_features(next_state, a).unsqueeze(0)).item() for a in legal_next])

        target = reward + self.gamma * next_q
        loss = self.loss_fn(current_q, torch.tensor([[target]], dtype=torch.float32))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def run_episode(self, game_state, display=None, explore=True):
        total_reward = 0
        state = game_state.deepCopy()
        previous_score = state.getScore()

        if display:
            display.initialize(state.data)

        while not state.isWin() and not state.isLose():
            action = self.choose_action(state, explore)
            next_state = state.generatePacmanSuccessor(action)

            reward = next_state.getScore() - previous_score - 0.1
            previous_score = next_state.getScore()

            self.update(state, action, reward, next_state)
            total_reward += reward

            state = next_state
            if display:
                display.update(state.data)

        if display:
            display.finish()

        if explore and self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return total_reward

    def plot_rewards(self):
        plt.plot(self.episode_rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Training Reward over Time')
        plt.grid(True)
        plt.show()

    def train(self, layout='tinySearch', episodes=1000):
        for ep in range(episodes):
            game_state = GameState()
            game_state.initialize(getLayout(layout), numGhostAgents=0)
            reward = self.run_episode(game_state, display=None, explore=True)
            self.episode_rewards.append(reward)
            print(f"Episode {ep+1} | Total Reward: {reward:.2f} | Epsilon: {self.epsilon:.3f}")
        self.plot_rewards()

    def test(self, layout='tinySearch'):
        game_state = GameState()
        game_state.initialize(getLayout(layout), numGhostAgents=0)
        display = PacmanGraphics(1.0, True)
        reward = self.run_episode(game_state, display=display, explore=False)
        print(f"🎮 Test Reward: {reward:.2f}")

if __name__ == '__main__':
    agent = DeepQLearningAgent()
    agent.train(layout='tinySearch', episodes=1000)
    agent.test(layout='tinySearch')