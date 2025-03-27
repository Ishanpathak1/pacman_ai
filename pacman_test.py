# pacman_ale_test.py

from ale_py import ALEInterface
import numpy as np
import time
import os
from pathlib import Path

def find_rom_path():
    """Find the Ms. Pacman ROM in the virtual environment."""
    venv_path = Path(os.environ.get('VIRTUAL_ENV', 'venv'))
    possible_paths = [
        venv_path / 'lib' / 'python3.10' / 'site-packages' / 'AutoROM' / 'roms' / 'ms_pacman.bin',
        venv_path / 'lib' / 'python3.10' / 'site-packages' / 'ale_py' / 'roms' / 'ms_pacman.bin'
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Could not find ms_pacman.bin ROM file. Make sure AutoROM is installed and ROMs are downloaded.")

def main():
    try:
        print("🎮 Launching Ms. Pacman using ALEInterface...")

        # Initialize ALE
        ale = ALEInterface()
        ale.setInt("random_seed", 42)
        ale.setBool("display_screen", True)  # Show game window

        # Load the ROM (absolute path to ms_pacman.bin)
        rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
        ale.loadROM(rom_path)

        # Get legal actions for the game
        legal_actions = ale.getLegalActionSet()
        print(f"Available Actions: {legal_actions}")

        # Play 3 episodes
        episodes = 3
        for ep in range(episodes):
            ale.reset_game()
            total_reward = 0
            frame = 0

            print(f"\n🎯 Starting Episode {ep + 1}")
            while not ale.game_over():
                action = np.random.choice(legal_actions)
                reward = ale.act(action)
                total_reward += reward
                frame += 1

                # Print every 100 steps
                if frame % 100 == 0:
                    print(f"Episode {ep + 1} | Frame: {frame} | Score: {total_reward}")

                time.sleep(0.01)  # 10ms delay for visibility

            print(f"🏁 Episode {ep + 1} finished | Total Score: {total_reward}")

        print("\n✅ All episodes completed. Closing game.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you're in the correct environment and ROM path is correct.")

if __name__ == "__main__":
    main()
