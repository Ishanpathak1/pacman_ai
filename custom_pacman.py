import pygame
import math

class CustomPacman:
    def __init__(self):
        pygame.init()
        self.cell_size = 30
        self.rows = 20
        self.cols = 25
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Custom Pacman - No Ghosts!")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.BLUE = (25, 25, 166)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        
        # Pacman properties
        self.pacman_pos = [self.cell_size * 1.5, self.cell_size * 1.5]
        self.pacman_radius = self.cell_size // 2
        self.pacman_speed = 4
        self.mouth_angle = 45
        self.mouth_speed = 5
        self.mouth_direction = 0  # 0: right, 1: down, 2: left, 3: up
        self.animation_frame = 0
        
        # Score
        self.score = 0
        
        # Create maze and pellets
        self.maze = self.create_maze()
        self.pellets = self.initialize_pellets()
        self.power_pellets = self.initialize_power_pellets()

    def create_maze(self):
        # Same maze layout as before
        return [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1],
            [1,2,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,2,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1],
            [1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1],
            [1,1,1,1,1,0,1,0,1,1,1,1,0,1,1,1,1,0,1,0,1,1,1,1,1],
            [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
            [1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1],
            [1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1],
            [1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1],
            [1,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,2,1],
            [1,1,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]

    def initialize_power_pellets(self):
        power_pellets = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == 2:
                    power_pellets.append([col * self.cell_size + self.cell_size//2,
                                        row * self.cell_size + self.cell_size//2])
        return power_pellets

    def initialize_pellets(self):
        pellets = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == 0:
                    pellets.append([col * self.cell_size + self.cell_size//2,
                                  row * self.cell_size + self.cell_size//2])
        return pellets

    def draw_maze(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.maze[row][col] == 1:
                    # Draw rounded walls
                    rect = pygame.Rect(col * self.cell_size,
                                     row * self.cell_size,
                                     self.cell_size,
                                     self.cell_size)
                    pygame.draw.rect(self.screen, self.BLUE, rect, border_radius=2)

    def draw_pellets(self):
        # Draw regular pellets
        for pellet in self.pellets:
            pygame.draw.circle(self.screen, self.WHITE,
                             (pellet[0], pellet[1]), 3)
        
        # Draw power pellets (larger and flashing)
        if self.animation_frame < 15:  # Make power pellets flash
            for pellet in self.power_pellets:
                pygame.draw.circle(self.screen, self.WHITE,
                                 (pellet[0], pellet[1]), 8)

    def draw_pacman(self):
        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % 30
        mouth_angle = abs(math.sin(self.animation_frame * 0.2)) * 45
        
        # Calculate direction vectors
        direction_vectors = {
            0: (1, 0, 0),    # Right
            1: (0, 1, 90),   # Down
            2: (-1, 0, 180), # Left
            3: (0, -1, 270)  # Up
        }
        
        dx, dy, base_angle = direction_vectors[self.mouth_direction]
        
        # Draw Pacman body
        pygame.draw.circle(self.screen, self.YELLOW,
                         (int(self.pacman_pos[0]), int(self.pacman_pos[1])),
                         self.pacman_radius)
        
        # Draw mouth
        mouth_points = [
            (self.pacman_pos[0], self.pacman_pos[1]),
            (self.pacman_pos[0] + self.pacman_radius * math.cos(math.radians(base_angle - mouth_angle)),
             self.pacman_pos[1] + self.pacman_radius * math.sin(math.radians(base_angle - mouth_angle))),
            (self.pacman_pos[0] + self.pacman_radius * math.cos(math.radians(base_angle)),
             self.pacman_pos[1] + self.pacman_radius * math.sin(math.radians(base_angle))),
            (self.pacman_pos[0] + self.pacman_radius * math.cos(math.radians(base_angle + mouth_angle)),
             self.pacman_pos[1] + self.pacman_radius * math.sin(math.radians(base_angle + mouth_angle)))
        ]
        pygame.draw.polygon(self.screen, self.BLACK, mouth_points)

    def check_collision(self, x, y):
        # Convert position to grid coordinates
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        
        # Check if position is within a wall
        if 0 <= grid_y < len(self.maze) and 0 <= grid_x < len(self.maze[0]):
            return self.maze[grid_y][grid_x] == 1
        return True

    def collect_pellets(self):
        pacman_rect = pygame.Rect(self.pacman_pos[0] - self.pacman_radius//2,
                                self.pacman_pos[1] - self.pacman_radius//2,
                                self.pacman_radius, self.pacman_radius)
        
        for pellet in self.pellets[:]:
            pellet_rect = pygame.Rect(pellet[0] - 2, pellet[1] - 2, 4, 4)
            if pacman_rect.colliderect(pellet_rect):
                self.pellets.remove(pellet)
                self.score += 10

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Move Pacman and update direction
            keys = pygame.key.get_pressed()
            new_x = self.pacman_pos[0]
            new_y = self.pacman_pos[1]
            
            if keys[pygame.K_LEFT]:
                new_x -= self.pacman_speed
                self.mouth_direction = 2
            if keys[pygame.K_RIGHT]:
                new_x += self.pacman_speed
                self.mouth_direction = 0
            if keys[pygame.K_UP]:
                new_y -= self.pacman_speed
                self.mouth_direction = 3
            if keys[pygame.K_DOWN]:
                new_y += self.pacman_speed
                self.mouth_direction = 1

            # Update position if no collision
            if not self.check_collision(new_x, new_y):
                self.pacman_pos[0] = new_x
                self.pacman_pos[1] = new_y

            # Collect pellets
            self.collect_pellets()

            # Draw everything
            self.screen.fill(self.BLACK)
            self.draw_maze()
            self.draw_pellets()
            self.draw_pacman()

            # Draw score with arcade-style font
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'SCORE: {self.score}', True, self.WHITE)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = CustomPacman()
    game.run() 