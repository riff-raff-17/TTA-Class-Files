import random
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
SNAKE_COLOR = (0, 200, 0)
HEAD_COLOR = (0, 255, 100)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (255, 255, 255)

# font = pygame.font.Font("font_path.ttf", 28)
font = pygame.font.SysFont(None, 28)


def draw_grid(surface):
    """Draw faint grid lines so each cell is visible."""
    for col in range(GRID_WIDTH + 1):
        x = col * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))

    for row in range(GRID_HEIGHT + 1):
        y = row * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE_COLOR, (0, y), (WINDOW_WIDTH, y))


def random_empty_cell(occupied_cells):
    """Pick a random grid cell that isn't currently occupied by the snake."""
    while True:
        cell = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if cell not in occupied_cells:
            return cell


def hits_wall(head):
    """True if the head has gone outside the grid's valid range."""
    x, y = head
    return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT


def hits_self(snake_body):
    """True if the head's position already appears elsewhere in the body."""
    return snake_body[0] in snake_body[1:]

# --- Representing the snake as a list of segments ---
# Each segment is an (x, y) GRID-coordinate tuple (not pixels). The first
# element is the head.
snake = [(10, 10), (9, 10), (8, 10)]  # head first

# Choosing a direction with a single variable.
direction = (1, 0)  # (dx, dy) -- moving right

# --- Decoupling movement speed from the frame rate ---
move_timer = 0
MOVE_INTERVAL = 150  # milliseconds per grid step

score = 0
food = random_empty_cell(snake)

game_over = False

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
    if not game_over:
        move_timer += clock.get_time()

        if move_timer >= MOVE_INTERVAL:
            move_timer = 0

            # Moving the whole snake on a fixed tick
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])
            snake.insert(0, new_head)

            # Checking collisions in a sensible order: food first.
            if new_head == food:
                score += 1
                food = random_empty_cell(snake)
            else:
                snake.pop()

            if hits_wall(new_head) or hits_self(snake):
                game_over = True

    # --- 3. Draw the frame ---
    screen.fill(BACKGROUND_COLOR)
    draw_grid(screen)

    # Food
    food_rect = (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, FOOD_COLOR, food_rect)

    # Snake
    for index, segment in enumerate(snake):
        seg_x, seg_y = segment
        rect = (seg_x * CELL_SIZE, seg_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = HEAD_COLOR if index == 0 else SNAKE_COLOR
        pygame.draw.rect(screen, color, rect)

    score_surface = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_surface, (10, 10))

    if game_over:
        over_surface = font.render("GAME OVER", True, TEXT_COLOR)
        screen.blit(over_surface, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 14))

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
