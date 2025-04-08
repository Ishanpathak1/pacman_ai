from pacman_agents import PacmanAgent
from collections import deque
import numpy as np

class BFSAgent(PacmanAgent):
    def __init__(self, display_screen=True, random_seed=42):
        super().__init__(display_screen, random_seed)
        self.search_depth = 50  # Higher depth to fully explore the maze layer by layer

    def get_action(self, state):
        """Use BFS to find the shortest path to the nearest dot (food)."""
        grid = self._state_to_grid(state)
        start_pos = self._get_pacman_position(state)
        goal_pos = self._find_nearest_dot(state)

        if not goal_pos:
            return np.random.choice(self.legal_actions)

        path = self._bfs_search(grid, start_pos, goal_pos)

        if path and len(path) > 1:
            return self._get_action_from_path(path[0], path[1])
        return np.random.choice(self.legal_actions)

    def _state_to_grid(self, state):
        """Convert RGB state to 2D grid where walls are marked as 1."""
        height, width = state.shape[:2]
        grid = np.zeros((height, width), dtype=int)
        wall_mask = (state.mean(axis=2) < 50)
        grid[wall_mask] = 1
        return grid

    def _get_pacman_position(self, state):
        yellow_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] < 100)
        positions = np.where(yellow_mask)
        if len(positions[0]) > 0:
            y = int(positions[0].mean())
            x = int(positions[1].mean())
            return (y, x)
        return (0, 0)

    def _find_nearest_dot(self, state):
        white_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] > 200)
        dot_positions = np.where(white_mask)
        pacman_pos = self._get_pacman_position(state)

        if len(dot_positions[0]) > 0:
            distances = [abs(y - pacman_pos[0]) + abs(x - pacman_pos[1])
                         for y, x in zip(dot_positions[0], dot_positions[1])]
            index = np.argmin(distances)
            return (dot_positions[0][index], dot_positions[1][index])
        return None

    def _bfs_search(self, grid, start, goal):
        queue = deque([(start, [start])])
        visited = set([start])
        height, width = grid.shape
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        while queue:
            pos, path = queue.popleft()
            if pos == goal:
                return path

            for dy, dx in directions:
                ny, nx = pos[0] + dy, pos[1] + dx
                new_pos = (ny, nx)
                if (0 <= ny < height and 0 <= nx < width and
                    grid[ny, nx] == 0 and new_pos not in visited):
                    visited.add(new_pos)
                    queue.append((new_pos, path + [new_pos]))
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
        print("\U0001F3AE Starting Ms. Pacman with BFS Agent...")
        agent.load_rom(rom_path)

        for episode in range(3):
            print(f"\n\U0001F3AF Episode {episode + 1}")
            metrics = agent.run_episode()
            print(f"\U0001F3C1 Episode finished | Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")

        print("\n✅ Testing completed!")
    except Exception as e:
        print(f"❌ Testing failed: {e}")