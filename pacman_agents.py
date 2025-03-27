from ale_py import ALEInterface
import numpy as np
import time
from abc import ABC, abstractmethod

class PacmanAgent(ABC):
    def __init__(self, display_screen=True, random_seed=42):
        self.ale = ALEInterface()
        self.ale.setInt("random_seed", random_seed)
        self.ale.setBool("display_screen", display_screen)
        
    def load_rom(self, rom_path):
        """Load the Ms. Pacman ROM."""
        self.ale.loadROM(rom_path)
        self.legal_actions = self.ale.getLegalActionSet()
        
    @abstractmethod
    def get_action(self, state):
        """Each agent must implement this to choose an action."""
        pass
    
    def run_episode(self):
        """Run one episode of the game."""
        self.ale.reset_game()
        total_reward = 0
        frame = 0
        metrics = {"frames": [], "rewards": [], "actions": []}
        
        while not self.ale.game_over():
            # Get the game screen
            state = self.ale.getScreenRGB()
            
            # Get action from the agent
            action = self.get_action(state)
            
            # Execute action and get reward
            reward = self.ale.act(action)
            total_reward += reward
            frame += 1
            
            # Store metrics
            metrics["frames"].append(frame)
            metrics["rewards"].append(reward)
            metrics["actions"].append(action)
            
            # Optional delay for visualization
            time.sleep(0.01)
            
            if frame % 100 == 0:
                print(f"Frame: {frame} | Score: {total_reward}")
        
        metrics["total_reward"] = total_reward
        metrics["total_frames"] = frame
        return metrics

class RandomAgent(PacmanAgent):
    """A simple random agent for baseline comparison."""
    def get_action(self, state):
        return np.random.choice(self.legal_actions) 