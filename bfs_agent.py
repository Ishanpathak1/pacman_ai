from pacman_agents import PacmanAgent
from collections import deque
import numpy as np

class BFSAgent(PacmanAgent):
    def __init__(self, display_screen=True, random_seed=42):
        super().__init__(display_screen, random_seed)

    def get_action(self, state):
        """Use BFS to find the shortest path to any food dot."""
        grid = self._state_to_grid(state)
        start_pos = self._get_pacman_position(state)
        food_positions = self._get_food_positions(state)

        if not food_positions:
            return np.random.choice(self.legal_actions)

        path = self._bfs_to_any_goal(grid, start_pos, food_positions)

        if path and len(path) > 1:
            return self._get_action_from_path(path[0], path[1])
        return np.random.choice(self.legal_actions)

    def _state_to_grid(self, state):
        height, width = state.shape[:2]
        grid = np.zeros((height, width), dtype=int)
        wall_mask = (state.mean(axis=2) < 50)
        grid[wall_mask] = 1
        return grid

    def _get_pacman_position(self, state):
        yellow_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] < 100)
        yx = np.argwhere(yellow_mask)
        if len(yx) > 0:
            return tuple(np.mean(yx, axis=0).astype(int))
        return (0, 0)

    def _get_food_positions(self, state):
        white_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] > 200)
        positions = np.argwhere(white_mask)
        return [tuple(p) for p in positions]

    def _bfs_to_any_goal(self, grid, start, goals):
        """Breadth-First Search from start to any goal."""
        queue = deque([(start, [start])])
        visited = {start}
        height, width = grid.shape
        goal_set = set(goals)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        while queue:
            current, path = queue.popleft()
            if current in goal_set:
                return path
            y, x = current
            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                next_pos = (ny, nx)
                if (0 <= ny < height and 0 <= nx < width and
                    grid[ny, nx] == 0 and next_pos not in visited):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        return [start]

    def _get_action_from_path(self, current, next_pos):
        y, x = current
        ny, nx = next_pos
        if ny < y: return 1  # UP
        if ny > y: return 4  # DOWN
        if nx < x: return 3  # LEFT
        if nx > x: return 2  # RIGHT
        return np.random.choice(self.legal_actions)

if __name__ == "__main__":
    agent = BFSAgent()
    rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"

    try:
        print("🎮 Starting Ms. Pacman with BFS Agent...")
        agent.load_rom(rom_path)
        for episode in range(3):
            print(f"\n🎯 Episode {episode + 1}")
            metrics = agent.run_episode()
            print(f"🏁 Episode finished | Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")
        print("\n✅ Testing completed!")
    except Exception as e:
        print(f"❌ Testing failed: {e}")
