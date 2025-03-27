from pacman_agents import PacmanAgent
import numpy as np
import heapq

class AStarAgent(PacmanAgent):
    def __init__(self, display_screen=True, random_seed=42):
        super().__init__(display_screen, random_seed)
        self.search_depth = 15  # A* can handle deeper search
        
    def get_action(self, state):
        """Use A* to find optimal path to nearest dot/pellet."""
        # Convert state to simplified grid representation
        grid = self._state_to_grid(state)
        start_pos = self._get_pacman_position(state)
        goal_pos = self._find_nearest_dot(state)
        
        if goal_pos is None:
            return np.random.choice(self.legal_actions)
        
        # Find path using A*
        path = self._astar_search(grid, start_pos, goal_pos)
        
        # Convert first step in path to action
        if path and len(path) > 1:
            return self._get_action_from_path(path[0], path[1])
        return np.random.choice(self.legal_actions)
    
    def _state_to_grid(self, state):
        """Convert game state to simplified grid."""
        height, width = state.shape[:2]
        grid = np.zeros((height, width), dtype=int)
        
        # Basic wall detection (black pixels are likely walls)
        wall_mask = (state.mean(axis=2) < 50)
        grid[wall_mask] = 1
        
        return grid
    
    def _get_pacman_position(self, state):
        """Find Pacman's position in the state."""
        yellow_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] < 100)
        positions = np.where(yellow_mask)
        if len(positions[0]) > 0:
            y = int(positions[0].mean())
            x = int(positions[1].mean())
            return (y, x)
        return (0, 0)
    
    def _find_nearest_dot(self, state):
        """Find the nearest dot in the state."""
        # Look for white pixels (dots are typically white)
        white_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] > 200)
        dot_positions = np.where(white_mask)
        
        if len(dot_positions[0]) > 0:
            # For now, just return the first dot found
            return (dot_positions[0][0], dot_positions[1][0])
        return None
    
    def _manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _astar_search(self, grid, start, goal):
        """Perform A* search to find optimal path to goal."""
        frontier = []
        heapq.heappush(frontier, (0, start, [start]))  # (priority, position, path)
        visited = {start: 0}  # position -> cost
        height, width = grid.shape
        
        # Possible movements (up, right, down, left)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        while frontier and len(visited) < self.search_depth:
            _, current, path = heapq.heappop(frontier)
            
            if current == goal:
                return path
                
            y, x = current
            current_cost = visited[current]
            
            # Check all possible directions
            for dy, dx in directions:
                new_y, new_x = y + dy, x + dx
                new_pos = (new_y, new_x)
                
                # Check if position is valid
                if (0 <= new_y < height and 
                    0 <= new_x < width and 
                    grid[new_y, new_x] == 0):
                    
                    new_cost = current_cost + 1
                    
                    if new_pos not in visited or new_cost < visited[new_pos]:
                        visited[new_pos] = new_cost
                        priority = new_cost + self._manhattan_distance(new_pos, goal)
                        heapq.heappush(frontier, (priority, new_pos, path + [new_pos]))
        
        return [start]
    
    def _get_action_from_path(self, current, next_pos):
        """Convert path step to action."""
        y, x = current
        next_y, next_x = next_pos
        
        # Determine direction
        if next_y < y: return 1  # UP
        if next_y > y: return 4  # DOWN
        if next_x < x: return 3  # LEFT
        if next_x > x: return 2  # RIGHT
        
        return np.random.choice(self.legal_actions)

if __name__ == "__main__":
    # Test the A* agent
    agent = AStarAgent()
    rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
    
    try:
        print("🎮 Starting Ms. Pacman with A* Agent...")
        agent.load_rom(rom_path)
        
        # Run 3 episodes
        for episode in range(3):
            print(f"\n🎯 Episode {episode + 1}")
            metrics = agent.run_episode()
            print(f"🏁 Episode finished | Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")
        
        print("\n✅ Testing completed!")
    except Exception as e:
        print(f"❌ Testing failed: {e}") 