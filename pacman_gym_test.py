# pacman_gym_test.py

from ale_py import ALEInterface
import time
import pygame
import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from pathlib import Path

def main():
    try:
        print("🎮 Launching Ms. Pacman...")
        
        ale = ALEInterface()
        ale.setBool('display_screen', True)
        
        # Use the same ROM path as your working pacman_test.py
        rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
        print(f"Loading ROM from: {rom_path}")
        ale.loadROM(rom_path)
        
        # Play 3 episodes
        for episode in range(3):
            total_reward = 0
            game_over = False
            ale.reset_game()
            
            while not game_over:
                action = ale.getMinimalActionSet()[0]  # Just move right
                reward = ale.act(action)
                total_reward += reward
                game_over = ale.game_over()
                time.sleep(0.01)
            
            print(f"Episode {episode + 1} finished! Score: {total_reward}")
            
    except Exception as e:
        print(f"Error: {e}")

class SimplePacman:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.pacman_pos = [400, 300]  # Start in middle
        self.pellets = [(random.randint(0, self.width), random.randint(0, self.height)) for _ in range(20)]
        self.score = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Move Pacman with arrow keys
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.pacman_pos[0] -= 5
            if keys[pygame.K_RIGHT]:
                self.pacman_pos[0] += 5
            if keys[pygame.K_UP]:
                self.pacman_pos[1] -= 5
            if keys[pygame.K_DOWN]:
                self.pacman_pos[1] += 5

            # Keep Pacman in bounds
            self.pacman_pos[0] = max(0, min(self.width, self.pacman_pos[0]))
            self.pacman_pos[1] = max(0, min(self.height, self.pacman_pos[1]))

            # Check pellet collection
            for pellet in self.pellets[:]:
                if ((self.pacman_pos[0] - pellet[0])**2 + 
                    (self.pacman_pos[1] - pellet[1])**2) < 400:  # 20px radius
                    self.pellets.remove(pellet)
                    self.score += 10

            # Draw everything
            self.screen.fill((0, 0, 0))  # Black background
            pygame.draw.circle(self.screen, (255, 255, 0), self.pacman_pos, 20)  # Pacman
            for pellet in self.pellets:
                pygame.draw.circle(self.screen, (255, 255, 255), pellet, 5)  # Pellets

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            pygame.time.delay(16)  # ~60 FPS

        pygame.quit()

class CustomPacmanEnv(gym.Env):
    def __init__(self):
        super().__init__()
        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # Up, Down, Left, Right
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)
        # Additional initialization code...

if __name__ == "__main__":
    main()
    game = SimplePacman()
    game.run() 