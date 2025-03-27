from pacman_agents import PacmanAgent
from collections import deque
import numpy as np

class BFSAgent(PacmanAgent):
    def __init__(self, display_screen=True, random_seed=42):
        super().__init__(display_screen, random_seed)
        self.search_depth = 10  # How many steps ahead to search
        
    def get_action(self, state):
        """Use BFS to find path to nearest dot/pellet."""
        # Convert state to simplified grid representation
        grid = self._state_to_grid(state)
        start_pos = self._get_pacman_position(state)
        
        # Find path using BFS
        path = self._bfs_search(grid, start_pos)
        
        # Convert first step in path to action
        if path and len(path) > 1:
            return self._get_action_from_path(path[0], path[1])
        return np.random.choice(self.legal_actions)
    
    def _state_to_grid(self, state):
        """Convert game state to simplified grid."""
        # This is a simplified version - you'll need to implement proper state processing
        # For now, we'll just detect walls and paths
        height, width = state.shape[:2]
        grid = np.zeros((height, width), dtype=int)
        
        # Basic wall detection (black pixels are likely walls)
        wall_mask = (state.mean(axis=2) < 50)
        grid[wall_mask] = 1
        
        return grid
    
    def _get_pacman_position(self, state):
        """Find Pacman's position in the state."""
        # Look for yellow pixels (Pacman's color)
        yellow_mask = (state[:,:,0] > 200) & (state[:,:,1] > 200) & (state[:,:,2] < 100)
        positions = np.where(yellow_mask)
        if len(positions[0]) > 0:
            # Return center of yellow pixels
            y = int(positions[0].mean())
            x = int(positions[1].mean())
            return (y, x)
        return (0, 0)  # fallback
    
    def _bfs_search(self, grid, start):
        """Perform BFS to find path to nearest dot."""
        queue = deque([(start, [start])])
        visited = {start}
        height, width = grid.shape
        
        # Possible movements (up, right, down, left)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        while queue and len(visited) < self.search_depth:
            pos, path = queue.popleft()
            y, x = pos
            
            # Check all possible directions
            for dy, dx in directions:
                new_y, new_x = y + dy, x + dx
                new_pos = (new_y, new_x)
                
                if (0 <= new_y < height and 
                    0 <= new_x < width and 
                    grid[new_y, new_x] == 0 and 
                    new_pos not in visited):
                    
                    visited.add(new_pos)
                    new_path = path + [new_pos]
                    queue.append((new_pos, new_path))
                    
                    # If we find a dot, return the path
                    # In a real implementation, you'd check for dots here
                    # For now, we'll just return any valid path
                    return new_path
        
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
    # Test the BFS agent
    agent = BFSAgent()
    rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
    
    try:
        print("🎮 Starting Ms. Pacman with BFS Agent...")
        agent.load_rom(rom_path)
        
        # Run 3 episodes
        for episode in range(3):
            print(f"\n🎯 Episode {episode + 1}")
            metrics = agent.run_episode()
            print(f"🏁 Episode finished | Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")
        
        print("\n✅ Testing completed!")
    except Exception as e:
        print(f"❌ Testing failed: {e}") 