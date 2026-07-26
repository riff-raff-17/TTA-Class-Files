import pygame

# --- Setup ---
pygame.init()

# Designing a grid on top of pixel coordinates
CELL_SIZE = 20  # pixels
GRID_WIDTH = 30  # cells across
GRID_HEIGHT = 20  # cells down

WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
FPS = 60

BACKGROUND_COLOR = (10, 10, 10)
GRID_LINE_COLOR = (40, 40, 40)
SNAKE_COLOR = (0, 200, 200)
HEAD_COLOR = (0, 255, 100)


def draw_grid(surface):
    """Draw faint grid lines so each cell is visible."""
    for col in range(GRID_WIDTH + 1):
        x = col * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))

    for row in range(GRID_HEIGHT + 1):
        y = row * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (0, y), (WINDOW_WIDTH, y))


# --- Representing the snake as a list of segments ---
# Each segment is an (x, y) GRID-coordinate tuple (not pixels). The first
# element is the head.
snake = [(10, 10), (9, 10), (8, 10)]  # head first

# Choosing a direction with a single variable.
direction = (1, 0)  # (dx, dy) -- moving right

# --- Decoupling movement speed from the frame rate ---
move_timer = 0
MOVE_INTERVAL = 150  # milliseconds per grid step

running = True

while running:
    # --- 1. Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Preventing an immediate reversal.
            # Each check rejects the new direction if it's the exact
            # opposite of the current one, so you can't turn left
            # while already moving right.
            if event.key == pygame.K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                direction = (1, 0)

    # --- 2. Update state ---
    move_timer += clock.get_time()

    if move_timer >= MOVE_INTERVAL:
        move_timer = 0

        # Moving the whole snake on a fixed tick
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        snake.insert(0, new_head)
        snake.pop()

    # --- 3. Draw the frame ---
    screen.fill(BACKGROUND_COLOR)
    draw_grid(screen)

    for index, segment in enumerate(snake):
        seg_x, seg_y = segment
        rect = (seg_x * CELL_SIZE, seg_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = HEAD_COLOR if index == 0 else SNAKE_COLOR
        pygame.draw.rect(screen, color, rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
