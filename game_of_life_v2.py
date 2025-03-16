import pygame
import numpy as np

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

# Initialize grid to all zeros
grid = np.zeros((ROWS, COLS), dtype=int)

# Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()

# Base patterns
PATTERNS = {
    'glider': [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ],
    'small_exploder': [
        [0, 1, 0],
        [1, 1, 1],
        [1, 0, 1],
        [0, 1, 0]
    ],
    'pulsar': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    'glider_gun': [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ]
}

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if grid[row][col] == 1 else BLACK
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1) # grid lines

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

def place_pattern(pattern_name, x, y):
    pattern = PATTERNS.get(pattern_name)
    if pattern:
        for row in range(len(pattern)):
            for col in range(len(pattern[0])):
                if 0 <= row + y < ROWS and 0 <= col + x < COLS:
                    grid[row + y][col + x] = pattern[row][col]

def handle_mouse():
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0]:
        x, y = pygame.mouse.get_pos()
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        grid[row][col] = 1 if grid[row][col] == 0 else 0
    if mouse_pressed[2]:
        grid[:] = 0

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
                if event.key == pygame.K_g:
                    place_pattern('glider', 5, 5)
                if event.key == pygame.K_s:
                    place_pattern('small_exploder', 5, 5)
                if event.key == pygame.K_p:
                    place_pattern('pulsar', 10, 10)
                if event.key == pygame.K_c:
                    place_pattern('glider_gun', 2, 2) # needs fixing

        handle_mouse()

        if not paused:
            update_grid()

        pygame.display.flip()
        clock.tick(FPS) # FPS

    pygame.quit()

if __name__ == "__main__":
    main()
