import pygame
import numpy as np
import time

# Screen size
WIDTH, HEIGHT = 1000, 800
CELL_SIZE = 20
FPS = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (40, 40, 40)

# Grid
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

# Initialize grid
grid = np.random.choice([0, 1], size=(ROWS, COLS))

# Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Patrick's Game of Death")
clock = pygame.time.Clock()

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if grid[row][col] == 1 else BLACK
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)  # grid lines

def update_grid():
    global grid
    new_grid = grid.copy()
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = np.sum(grid[row-1:row+2, col-1:col+2]) - grid[row][col]
            if grid[row][col] == 1: # Cell is alive
                if neighbors < 2 or neighbors > 3:
                    new_grid[row][col] = 0 # Underpopulation or Overpopulation
            else: # Cell is dead
                if neighbors == 3:
                    new_grid[row][col] = 1 # Reproduction
    grid = new_grid

def main():
    running = True
    paused = True

    while running:
        screen.fill(BLACK)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Toggle pause with SPACE key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r: # Reset with "R"
                    global grid
                    grid = np.random.choice([0, 1], size=(ROWS, COLS))
        if not paused:
            update_grid()

        pygame.display.flip()
        clock.tick(FPS)  # FPS

    pygame.quit()

if __name__ == "__main__":
    main()
