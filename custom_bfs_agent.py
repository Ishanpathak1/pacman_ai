import pygame
from collections import deque
from custom_pacman import CustomPacman

class BFSAgent:
    def __init__(self):
        self.game = CustomPacman()
        self.cell_size = self.game.cell_size
        self.speed = self.game.pacman_speed
        self.current_direction = None
        self.target_position = None

    def get_grid_pos(self, pixel_pos):
        """Convert pixel position to grid position."""
        return (int(pixel_pos[1] // self.cell_size), 
                int(pixel_pos[0] // self.cell_size))

    def get_center_pixel_pos(self, grid_pos):
        """Convert grid position to center pixel position."""
        return (grid_pos[1] * self.cell_size + self.cell_size // 2,
                grid_pos[0] * self.cell_size + self.cell_size // 2)

    def is_at_center(self, pos):
        """Check if position is at the center of a grid cell."""
        grid_pos = self.get_grid_pos(pos)
        center_pos = self.get_center_pixel_pos(grid_pos)
        return (abs(pos[0] - center_pos[0]) < self.speed and 
                abs(pos[1] - center_pos[1]) < self.speed)

    def find_path_to_pellet(self, start_grid_pos):
        """Find path to nearest pellet using BFS."""
        queue = deque([(start_grid_pos, [])])
        visited = {start_grid_pos}
        
        while queue:
            current, path = queue.popleft()
            y, x = current

            # Check if current position has a pellet
            if self.game.maze[y][x] == 0:
                center_pos = self.get_center_pixel_pos((y, x))
                # Verify there's actually a pellet here
                for pellet in self.game.pellets:
                    if (abs(pellet[0] - center_pos[0]) < self.cell_size/2 and 
                        abs(pellet[1] - center_pos[1]) < self.cell_size/2):
                        return path + [current]

            # Try all four directions
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_y, new_x = y + dy, x + dx
                new_pos = (new_y, new_x)
                
                if (0 <= new_y < len(self.game.maze) and 
                    0 <= new_x < len(self.game.maze[0]) and 
                    self.game.maze[new_y][new_x] != 1 and 
                    new_pos not in visited):
                    visited.add(new_pos)
                    queue.append((new_pos, path + [current]))
        
        return None

    def get_next_direction(self):
        """Determine the next direction to move."""
        current_pos = self.game.pacman_pos
        
        # If we're at a grid center, get new path
        if self.is_at_center(current_pos) or self.target_position is None:
            current_grid = self.get_grid_pos(current_pos)
            path = self.find_path_to_pellet(current_grid)
            
            if path and len(path) > 1:
                # Set next grid position as target
                self.target_position = self.get_center_pixel_pos(path[1])
            else:
                return None  # No path found

        # Move toward target position
        if self.target_position:
            dx = self.target_position[0] - current_pos[0]
            dy = self.target_position[1] - current_pos[1]
            
            if abs(dx) > abs(dy):
                return 2 if dx > 0 else 3  # RIGHT or LEFT
            else:
                return 4 if dy > 0 else 1  # DOWN or UP
        
        return None

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Get next direction
            direction = self.get_next_direction()
            if direction is None:
                if not self.game.pellets:  # If no pellets left
                    break
                direction = 2  # Default to RIGHT

            # Update position based on direction
            new_x, new_y = self.game.pacman_pos[0], self.game.pacman_pos[1]
            
            if direction == 1:  # UP
                new_y -= self.speed
                self.game.mouth_direction = 3
            elif direction == 4:  # DOWN
                new_y += self.speed
                self.game.mouth_direction = 1
            elif direction == 3:  # LEFT
                new_x -= self.speed
                self.game.mouth_direction = 2
            elif direction == 2:  # RIGHT
                new_x += self.speed
                self.game.mouth_direction = 0

            # Update position if no collision
            if not self.game.check_collision(new_x, new_y):
                self.game.pacman_pos[0] = new_x
                self.game.pacman_pos[1] = new_y

            # Collect pellets
            self.game.collect_pellets()

            # Draw everything
            self.game.screen.fill(self.game.BLACK)
            self.game.draw_maze()
            self.game.draw_pellets()
            self.game.draw_pacman()

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'SCORE: {self.game.score}', True, self.game.WHITE)
            self.game.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    agent = BFSAgent()
    try:
        print("🎮 Starting Custom Pacman with BFS Agent...")
        agent.run()
        print("✅ Game completed!")
    except Exception as e:
        print(f"❌ Error: {e}") 