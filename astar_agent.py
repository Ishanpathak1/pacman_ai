from pacman_agents import PacmanAgent
import numpy as np
import heapq
import logging

logging.basicConfig(filename='pacman_agent.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Starting the improved A* agent script.")

class AStarAgent(PacmanAgent):
    def __init__(self, display_screen=True, random_seed=42):
        super().__init__(display_screen, random_seed)
        self.search_depth = 20
        self.visited_positions = set()

    def get_action(self, state):
        if np.random.rand() < 0.1:
            logging.debug("Exploring randomly.")
            return np.random.choice(self.legal_actions)

        strategy = self._choose_strategy(state)
        self.search_depth = 10 if strategy == 'defensive' else 20

        ghosts = self._find_ghosts(state)
        if ghosts:
            logging.debug(f"{len(ghosts)} ghosts nearby, avoiding.")
            return self._avoid_ghosts(state, ghosts)

        grid = self._state_to_grid(state)
        start_pos = self._get_pacman_position(state)
        goal_pos = self._find_nearest_dot(state)

        if goal_pos is None:
            logging.debug("No dot found. Choosing random move.")
            return np.random.choice(self.legal_actions)

        path = self._astar_search(grid, start_pos, goal_pos, state)

        if path and len(path) > 1:
            action = self._get_action_from_path(path[0], path[1])
            logging.debug(f"Action: {action}, Path: {path}")
            return action

        logging.debug("Fallback: choosing safe random move.")
        legal = [a for a in self.legal_actions if not self._is_wall(state, self._simulate_action(start_pos, a))]
        return np.random.choice(legal) if legal else 2

    def _state_to_grid(self, state):
        gray = np.mean(state, axis=2)
        wall_mask = gray < 50
        return wall_mask.astype(int)

    def _get_pacman_position(self, state):
        yellow_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] < 100)
        pos = np.where(yellow_mask)
        if len(pos[0]) > 0:
            return (int(pos[0].mean()), int(pos[1].mean()))
        return (0, 0)

    def _find_nearest_dot(self, state):
        white_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] > 200)
        dot_positions = np.where(white_mask)
        if len(dot_positions[0]) == 0:
            logging.debug("No dots detected.")
            return None
        pacman_pos = self._get_pacman_position(state)
        distances = [self._manhattan_distance(pacman_pos, (y, x)) for y, x in zip(dot_positions[0], dot_positions[1])]
        idx = np.argmin(distances)
        return (dot_positions[0][idx], dot_positions[1][idx])

    def _find_ghosts(self, state):
        red = (state[:,:,0] > 150) & (state[:,:,1] < 100) & (state[:,:,2] < 100)
        pink = (state[:,:,0] > 200) & (state[:,:,1] < 200) & (state[:,:,2] > 200)
        ghost_mask = red | pink
        ghost_pos = np.where(ghost_mask)
        return list(zip(ghost_pos[0], ghost_pos[1]))

    def _find_power_pellets(self, state):
        mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] > 200)
        pos = np.where(mask)
        return list(zip(pos[0], pos[1]))

    def _manhattan_distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _dynamic_ghost_penalty(self, state, pos):
        ghosts = self._find_ghosts(state)
        penalty = sum(10 / (self._manhattan_distance(pos, g) + 1) for g in ghosts if self._manhattan_distance(pos, g) < 3)
        revisit_penalty = 2 if pos in self.visited_positions else 0
        return penalty + revisit_penalty

    def _astar_search(self, grid, start, goal, state):
        frontier = [(0, start, [start])]
        visited = {start: 0}
        h, w = grid.shape
        directions = [(-1,0),(1,0),(0,-1),(0,1)]

        while frontier:
            _, current, path = heapq.heappop(frontier)
            if current == goal:
                return path
            self.visited_positions.add(current)
            for dy, dx in directions:
                ny, nx = current[0]+dy, current[1]+dx
                new_pos = (ny, nx)
                if not (0 <= ny < h and 0 <= nx < w) or grid[ny, nx] == 1:
                    continue
                new_cost = visited[current] + 1
                if new_pos not in visited or new_cost < visited[new_pos]:
                    visited[new_pos] = new_cost
                    g_penalty = self._dynamic_ghost_penalty(state, new_pos)
                    pellet_bonus = -10 if new_pos in self._find_power_pellets(state) else 0
                    priority = new_cost + self._manhattan_distance(new_pos, goal) + g_penalty + pellet_bonus
                    heapq.heappush(frontier, (priority, new_pos, path + [new_pos]))
                    logging.debug(f"Expand: {new_pos} | Priority: {priority}")
        logging.debug(f"A* failed: no path from {start} to {goal}")
        return [start]

    def _get_action_from_path(self, cur, nxt):
        dy, dx = nxt[0] - cur[0], nxt[1] - cur[1]
        if dy == -1: return 1  # UP
        if dy == 1: return 4   # DOWN
        if dx == -1: return 3  # LEFT
        if dx == 1: return 2   # RIGHT
        return np.random.choice(self.legal_actions)

    def _is_wall(self, state, pos):
        y, x = pos
        return np.mean(state[y, x]) < 50

    def _simulate_action(self, pos, action):
        y, x = pos
        if action == 1: return (y-1, x)
        if action == 4: return (y+1, x)
        if action == 3: return (y, x-1)
        if action == 2: return (y, x+1)
        return pos

    def _choose_strategy(self, state):
        return 'defensive' if len(self._find_ghosts(state)) > 2 else 'aggressive'

    def _avoid_ghosts(self, state, ghosts):
        pacman_pos = self._get_pacman_position(state)
        best_action = None
        max_dist = -1
        for action in self.legal_actions:
            new_pos = self._simulate_action(pacman_pos, action)
            if self._is_wall(state, new_pos):
                continue
            min_dist = min(self._manhattan_distance(new_pos, g) for g in ghosts)
            if min_dist > max_dist:
                max_dist = min_dist
                best_action = action
        return best_action if best_action else np.random.choice(self.legal_actions)

if __name__ == "__main__":
    agent = AStarAgent()
    rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
    try:
        print("🎮 Starting Ms. Pacman with A* Agent...")
        agent.load_rom(rom_path)
        for i in range(3):
            print(f"\n🎯 Episode {i+1}")
            metrics = agent.run_episode()
            print(f"🏁 Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")
        print("✅ Done!")
    except Exception as e:
        print(f"❌ Error: {e}")
