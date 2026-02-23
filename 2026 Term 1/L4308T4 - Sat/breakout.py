import sys
import random
import pygame

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

BG_COLOR = (18, 18, 24)
TEXT_COLOR = (240, 240, 240)

PADDLE_W, PADDLE_H = 120, 16
PADDLE_SPEED = 8

BALL_RADIUS = 8
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_GAP = 8
BRICK_TOP_OFFSET = 70
BRICK_SIDE_PADDING = 40
BRICK_H = 26

LIVES_START = 3


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def make_bricks():
    """Create a grid of bricks as a list of dicts: {'rect': Rect, 'hp': int, 'color': (r,g,b)}"""
    bricks = []

    total_gap = BRICK_GAP * (BRICK_COLS - 1)
    usable_w = WIDTH - 2 * BRICK_SIDE_PADDING
    brick_w = (usable_w - total_gap) // BRICK_COLS

    # Simple row colors
    row_colors = [
        (255, 99, 132),
        (255, 159, 64),
        (255, 205, 86),
        (75, 192, 192),
        (54, 162, 235),
        (153, 102, 255),
    ]

    for r in range(BRICK_ROWS):
        for c in range(BRICK_COLS):
            x = BRICK_SIDE_PADDING + c * (brick_w + BRICK_GAP)
            y = BRICK_TOP_OFFSET + r * (BRICK_H + BRICK_GAP)
            rect = pygame.Rect(x, y, brick_w, BRICK_H)

            # Optional: make higher rows tougher
            hp = 1  # keep it simple; try hp = 1 + (r // 2)
            color = row_colors[r % len(row_colors)]

            bricks.append({"rect": rect, "hp": hp, "color": color})

    return bricks


def reset_ball(ball_pos, ball_vel):
    ball_pos.update(WIDTH // 2, HEIGHT // 2 + 60)
    # randomize slight x direction so it doesn't get stuck in boring loops
    vx = random.choice([-1, 1]) * BALL_SPEED_X
    vy = BALL_SPEED_Y
    ball_vel.update(vx, vy)


def circle_rect_collision(cx, cy, radius, rect):
    """Return True if circle intersects rect (simple closest-point test)."""
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= radius * radius


def reflect_ball_from_rect(ball_pos, ball_vel, radius, rect):
    """
    Reflect ball velocity based on which side it likely hit.
    Uses overlap depth to pick axis of reflection.
    """
    # Compute overlaps (how deep ball is into the rect bounds)
    cx, cy = ball_pos.x, ball_pos.y

    # Closest point on rect to circle center
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)

    dx = cx - closest_x
    dy = cy - closest_y

    # If dx is 0 and dy is 0, center is inside rect; handle by axis based on velocity
    if dx == 0 and dy == 0:
        if abs(ball_vel.x) > abs(ball_vel.y):
            ball_vel.x *= -1
        else:
            ball_vel.y *= -1
        return

    # Decide reflection axis by which distance is larger relative to penetration direction
    if abs(dx) > abs(dy):
        ball_vel.x *= -1
    else:
        ball_vel.y *= -1


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brick Breaker (Pygame)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    # Paddle
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_W // 2, HEIGHT - 60, PADDLE_W, PADDLE_H)

    # Ball (store as float position for smooth movement)
    ball_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    ball_vel = pygame.Vector2(BALL_SPEED_X, BALL_SPEED_Y)

    # Game state
    bricks = make_bricks()
    score = 0
    lives = LIVES_START
    paused = False
    game_over = False
    win = False

    reset_ball(ball_pos, ball_vel)

    while True:
        dt = clock.tick(FPS)

        # -----------------------------
        # Events
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_p:
                    paused = not paused

                if event.key == pygame.K_r:
                    # Full restart
                    bricks = make_bricks()
                    score = 0
                    lives = LIVES_START
                    game_over = False
                    win = False
                    paused = False
                    paddle.centerx = WIDTH // 2
                    reset_ball(ball_pos, ball_vel)

        keys = pygame.key.get_pressed()

        # -----------------------------
        # Update
        # -----------------------------
        if not paused and not game_over and not win:
            # Paddle movement
            move = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move += PADDLE_SPEED

            paddle.x += move
            paddle.x = clamp(paddle.x, 0, WIDTH - paddle.width)

            # Ball movement
            ball_pos += ball_vel

            # Wall collisions
            if ball_pos.x - BALL_RADIUS <= 0:
                ball_pos.x = BALL_RADIUS
                ball_vel.x *= -1
            if ball_pos.x + BALL_RADIUS >= WIDTH:
                ball_pos.x = WIDTH - BALL_RADIUS
                ball_vel.x *= -1
            if ball_pos.y - BALL_RADIUS <= 0:
                ball_pos.y = BALL_RADIUS
                ball_vel.y *= -1

            # Bottom (lose life)
            if ball_pos.y - BALL_RADIUS > HEIGHT:
                lives -= 1
                if lives <= 0:
                    game_over = True
                reset_ball(ball_pos, ball_vel)

            # Paddle collision
            if circle_rect_collision(ball_pos.x, ball_pos.y, BALL_RADIUS, paddle) and ball_vel.y > 0:
                # Bounce up
                ball_vel.y *= -1

                # Add "english": change x vel based on where it hit the paddle
                hit_pos = (ball_pos.x - paddle.centerx) / (paddle.width / 2)  # -1..1
                ball_vel.x = hit_pos * 7  # tweak for feel

                # Prevent sticking
                ball_pos.y = paddle.top - BALL_RADIUS - 1

            # Brick collisions (check a few per frame)
            hit_index = None
            for i, b in enumerate(bricks):
                if circle_rect_collision(ball_pos.x, ball_pos.y, BALL_RADIUS, b["rect"]):
                    hit_index = i
                    break

            if hit_index is not None:
                b = bricks[hit_index]
                reflect_ball_from_rect(ball_pos, ball_vel, BALL_RADIUS, b["rect"])

                b["hp"] -= 1
                score += 10
                if b["hp"] <= 0:
                    bricks.pop(hit_index)

                # Win condition
                if not bricks:
                    win = True

        # -----------------------------
        # Draw
        # -----------------------------
        screen.fill(BG_COLOR)

        # Bricks
        for b in bricks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=6)

        # Paddle
        pygame.draw.rect(screen, (220, 220, 220), paddle, border_radius=8)

        # Ball
        pygame.draw.circle(screen, (240, 240, 240), (int(ball_pos.x), int(ball_pos.y)), BALL_RADIUS)

        # HUD
        hud = font.render(f"Score: {score}   Lives: {lives}   (P)ause  (R)estart  (Esc)Quit", True, TEXT_COLOR)
        screen.blit(hud, (20, 20))

        if paused and not game_over and not win:
            t = big_font.render("PAUSED", True, TEXT_COLOR)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))

        if game_over:
            t = big_font.render("GAME OVER", True, TEXT_COLOR)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))
            s = font.render("Press R to restart", True, TEXT_COLOR)
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 20))

        if win:
            t = big_font.render("YOU WIN!", True, TEXT_COLOR)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))
            s = font.render("Press R to play again", True, TEXT_COLOR)
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()


if __name__ == "__main__":
    main()
