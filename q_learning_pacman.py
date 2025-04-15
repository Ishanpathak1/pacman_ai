import random
import numpy as np
import pickle
from collections import defaultdict
from pacman import GameState
from pacmanAgents import Directions
from game import Actions
from layout import getLayout
from graphicsDisplay import PacmanGraphics

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: np.zeros(4))
        self.actions = [Directions.NORTH, Directions.SOUTH, Directions.WEST, Directions.EAST]

    def get_state(self, state):
        return (state.getPacmanPosition(), tuple(state.getFood().asList()))

    def get_legal_actions(self, state):
        return state.getLegalActions(0)

    def choose_action(self, state, explore=True):
        legal_actions = self.get_legal_actions(state)
        legal_indices = [self.actions.index(a) for a in self.actions if a in legal_actions]
        state_key = self.get_state(state)

        if not legal_indices:
            return Directions.STOP

        if explore and random.random() < self.epsilon:
            return random.choice([self.actions[i] for i in legal_indices])

        q_values = self.q_table[state_key]
        best_index = max(legal_indices, key=lambda i: q_values[i])
        return self.actions[best_index]

    def get_action_index(self, action):
        return self.actions.index(action)

    def update_q_table(self, state, action, reward, next_state):
        state_key = self.get_state(state)
        next_key = self.get_state(next_state)
        a_idx = self.get_action_index(action)
        next_legal_actions = self.get_legal_actions(next_state)
        next_legal_indices = [self.actions.index(a) for a in self.actions if a in next_legal_actions]
        best_next = max([self.q_table[next_key][i] for i in next_legal_indices], default=0)
        self.q_table[state_key][a_idx] += self.alpha * (reward + self.gamma * best_next - self.q_table[state_key][a_idx])

    def manhattan_to_nearest_food(self, state):
        pos = state.getPacmanPosition()
        food_list = state.getFood().asList()
        if not food_list:
            return 0
        return min(abs(pos[0] - fx) + abs(pos[1] - fy) for fx, fy in food_list)

    def find_closest_food_direction(self, state):
        from util import manhattanDistance
        pos = state.getPacmanPosition()
        food_list = state.getFood().asList()
        legal = self.get_legal_actions(state)
        best_action = None
        min_dist = float('inf')
        for action in legal:
            successor = state.generatePacmanSuccessor(action)
            new_pos = successor.getPacmanPosition()
            for food in food_list:
                dist = manhattanDistance(new_pos, food)
                if dist < min_dist:
                    min_dist = dist
                    best_action = action
        return best_action

    def run_episode(self, game_state, display=None, explore=True):
        total_reward = 0
        state = game_state.deepCopy()
        state_visits = defaultdict(int)
        previous_position = None
        stuck_counter = 0
        not_eating_counter = 0
        previous_score = state.getScore()

        if display:
            display.initialize(state.data)

        while not state.isWin() and not state.isLose():
            state_key = self.get_state(state)
            state_visits[state_key] += 1

            action = self.choose_action(state, explore=explore)

            if not explore and stuck_counter > 10:
                action = self.find_closest_food_direction(state)

            if action not in self.get_legal_actions(state):
                break

            next_state = state.generatePacmanSuccessor(action)
            reward = next_state.getScore() - previous_score - 0.1
            previous_score = next_state.getScore()

            repeat_penalty = 0.7 * state_visits[state_key]
            reward -= repeat_penalty

            dist = self.manhattan_to_nearest_food(state)
            reward += max(0, 6 - dist * 0.2)

            if state.getScore() == next_state.getScore():
                not_eating_counter += 1
                if not_eating_counter > 6:
                    reward -= 5
            else:
                not_eating_counter = 0

            self.update_q_table(state, action, reward, next_state)
            total_reward += reward

            if previous_position == state.getPacmanPosition():
                stuck_counter += 1
                if stuck_counter > 30:
                    break
            else:
                stuck_counter = 0

            previous_position = state.getPacmanPosition()
            state = next_state

            if display:
                display.update(state.data)

        if display:
            display.finish()

        return total_reward

    def train(self, layout_name='tinySearch', episodes=500, render_last=True):
        layout = getLayout(layout_name)
        for ep in range(episodes):
            game_state = GameState()
            game_state.initialize(layout, numGhostAgents=0)
            display = PacmanGraphics(1.0, False) if (render_last and ep == episodes - 1) else None
            reward = self.run_episode(game_state, display=display, explore=True)
            print(f"Episode {ep+1} | Total Reward: {reward}")

    def test(self, layout_name='tinySearch', render=True):
        layout = getLayout(layout_name)
        game_state = GameState()
        game_state.initialize(layout, numGhostAgents=0)
        display = PacmanGraphics(1.0, render)
        reward = self.run_episode(game_state, display=display, explore=False)
        print(f"🎮 Test Run | Total Reward: {reward}")

    def save_model(self, filename="q_table.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(dict(self.q_table), f)
        print(f"💾 Q-table saved to '{filename}'.")

    def load_model(self, filename="q_table.pkl"):
        try:
            with open(filename, "rb") as f:
                loaded_q = pickle.load(f)
                self.q_table = defaultdict(lambda: np.zeros(4), loaded_q)
            print(f"✅ Q-table loaded from '{filename}'.")
        except FileNotFoundError:
            print("⚠️ Q-table file not found.")

if __name__ == "__main__":
    agent = QLearningAgent()
    try:
        print("🤖 Training Q-Learning Agent on layout 'tinySearch'...")
        agent.train(episodes=500, render_last=True)
        agent.save_model("q_table_tiny.pkl")
        print("✅ Training completed! Now running test...")
        agent.test(layout_name='tinySearch', render=True)
    except Exception as e:
        print(f"❌ Error: {e}") 








