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
PADDLE_WIDE_MULT = 1.6

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

# Power-up settings
POWERUP_DROP_CHANCE = 0.9  # chance per brick destroyed
POWERUP_SIZE = 18
POWERUP_FALL_SPEED = 4
POWERUP_DURATION_MS = 8000   # for timed effects


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def make_bricks():
    bricks = []

    total_gap = BRICK_GAP * (BRICK_COLS - 1)
    usable_w = WIDTH - 2 * BRICK_SIDE_PADDING
    brick_w = (usable_w - total_gap) // BRICK_COLS

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

            hp = 1
            color = row_colors[r % len(row_colors)]

            bricks.append({"rect": rect, "hp": hp, "color": color})

    return bricks


def reset_ball(ball_pos, ball_vel):
    ball_pos.update(WIDTH // 2, HEIGHT // 2 + 60)
    vx = random.choice([-1, 1]) * BALL_SPEED_X
    vy = BALL_SPEED_Y
    ball_vel.update(vx, vy)


def circle_rect_collision(cx, cy, radius, rect):
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= radius * radius


def reflect_ball_from_rect(ball_pos, ball_vel, radius, rect):
    cx, cy = ball_pos.x, ball_pos.y
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y

    if dx == 0 and dy == 0:
        if abs(ball_vel.x) > abs(ball_vel.y):
            ball_vel.x *= -1
        else:
            ball_vel.y *= -1
        return

    if abs(dx) > abs(dy):
        ball_vel.x *= -1
    else:
        ball_vel.y *= -1


# -----------------------------
# Power-ups
# -----------------------------
# We'll represent power-ups as dicts:
# {"type": "WIDE"/"SLOW"/"LIFE"/"MULTI", "rect": Rect, "color": (r,g,b)}
POWERUP_TYPES = [
    ("WIDE",  (80, 200, 120)),
    ("SLOW",  (80, 160, 220)),
    ("LIFE",  (220, 80, 80)),
    ("MULTI", (200, 160, 80)),
]


def spawn_powerup(powerups, x, y):
    ptype, color = random.choice(POWERUP_TYPES)
    rect = pygame.Rect(x - POWERUP_SIZE // 2, y - POWERUP_SIZE // 2, POWERUP_SIZE, POWERUP_SIZE)
    powerups.append({"type": ptype, "rect": rect, "color": color})


def apply_powerup(ptype, *, paddle, balls, lives, active_effects):
    """
    Returns updated (lives). Mutates paddle/balls/active_effects in-place.
    active_effects: dict { "WIDE": end_time_ms, "SLOW": end_time_ms }
    """
    now = pygame.time.get_ticks()

    if ptype == "LIFE":
        lives += 1

    elif ptype == "WIDE":
        # Extend duration if already active
        active_effects["WIDE"] = now + POWERUP_DURATION_MS

    elif ptype == "SLOW":
        active_effects["SLOW"] = now + POWERUP_DURATION_MS

    elif ptype == "MULTI":
        # Add another ball with a slightly different direction
        if balls:
            base = balls[0]
            new_ball = {
                "pos": pygame.Vector2(base["pos"].x, base["pos"].y),
                "vel": pygame.Vector2(-base["vel"].x, base["vel"].y),
            }
            balls.append(new_ball)

    return lives


def update_active_effects(*, paddle, base_paddle_w, balls, active_effects):
    """
    Apply/expire timed effects based on current time.
    """
    now = pygame.time.get_ticks()

    # WIDE paddle
    if active_effects.get("WIDE", 0) > now:
        target_w = int(base_paddle_w * PADDLE_WIDE_MULT)
    else:
        target_w = base_paddle_w
        active_effects.pop("WIDE", None)

    # Keep paddle centered while changing width
    if paddle.width != target_w:
        cx = paddle.centerx
        paddle.width = target_w
        paddle.centerx = cx
        paddle.x = clamp(paddle.x, 0, WIDTH - paddle.width)

    # SLOW ball(s)
    slow_active = active_effects.get("SLOW", 0) > now
    if not slow_active:
        active_effects.pop("SLOW", None)

    # We *don't* permanently edit velocities here (that can cause drift over time).
    # Instead we scale movement when updating.
    return slow_active


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brick Breaker (Pygame) + Power-ups")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 56)

    # Paddle
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_W // 2, HEIGHT - 60, PADDLE_W, PADDLE_H)
    base_paddle_w = PADDLE_W

    # Balls: list of dicts with float positions
    balls = [{"pos": pygame.Vector2(WIDTH // 2, HEIGHT // 2), "vel": pygame.Vector2(BALL_SPEED_X, BALL_SPEED_Y)}]
    reset_ball(balls[0]["pos"], balls[0]["vel"])

    # Game state
    bricks = make_bricks()
    powerups = []
    score = 0
    lives = LIVES_START
    paused = False
    game_over = False
    win = False

    # Active timed effects
    active_effects = {}  # "WIDE": end_time_ms, "SLOW": end_time_ms

    while True:
        clock.tick(FPS)

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
                    bricks = make_bricks()
                    powerups = []
                    score = 0
                    lives = LIVES_START
                    game_over = False
                    win = False
                    paused = False
                    active_effects.clear()

                    paddle.width = base_paddle_w
                    paddle.centerx = WIDTH // 2

                    balls = [{"pos": pygame.Vector2(WIDTH // 2, HEIGHT // 2), "vel": pygame.Vector2(0, 0)}]
                    reset_ball(balls[0]["pos"], balls[0]["vel"])

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

            # Apply/expire effects (returns whether slow is active)
            slow_active = update_active_effects(
                paddle=paddle,
                base_paddle_w=base_paddle_w,
                balls=balls,
                active_effects=active_effects,
            )

            # Ball movement scaling (slow effect)
            speed_scale = 0.55 if slow_active else 1.0

            # Update each ball
            balls_to_remove = []
            for bi, ball in enumerate(balls):
                pos = ball["pos"]
                vel = ball["vel"]

                pos += vel * speed_scale

                # Wall collisions
                if pos.x - BALL_RADIUS <= 0:
                    pos.x = BALL_RADIUS
                    vel.x *= -1
                if pos.x + BALL_RADIUS >= WIDTH:
                    pos.x = WIDTH - BALL_RADIUS
                    vel.x *= -1
                if pos.y - BALL_RADIUS <= 0:
                    pos.y = BALL_RADIUS
                    vel.y *= -1

                # Bottom: remove ball (or lose life if it was last ball)
                if pos.y - BALL_RADIUS > HEIGHT:
                    balls_to_remove.append(bi)
                    continue

                # Paddle collision
                if circle_rect_collision(pos.x, pos.y, BALL_RADIUS, paddle) and vel.y > 0:
                    vel.y *= -1
                    hit_pos = (pos.x - paddle.centerx) / (paddle.width / 2)
                    vel.x = hit_pos * 7
                    pos.y = paddle.top - BALL_RADIUS - 1

                # Brick collision (only one per ball per frame)
                hit_index = None
                for i, b in enumerate(bricks):
                    if circle_rect_collision(pos.x, pos.y, BALL_RADIUS, b["rect"]):
                        hit_index = i
                        break

                if hit_index is not None:
                    b = bricks[hit_index]
                    reflect_ball_from_rect(pos, vel, BALL_RADIUS, b["rect"])

                    b["hp"] -= 1
                    score += 10

                    if b["hp"] <= 0:
                        # Chance to spawn a power-up where the brick was
                        if random.random() < POWERUP_DROP_CHANCE:
                            spawn_powerup(powerups, b["rect"].centerx, b["rect"].centery)

                        bricks.pop(hit_index)

                    if not bricks:
                        win = True

            # Remove fallen balls
            for index in reversed(balls_to_remove):
                balls.pop(index)

            # If no balls left: lose life and respawn one ball
            if not balls and not win and not game_over:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    balls = [{"pos": pygame.Vector2(WIDTH // 2, HEIGHT // 2), "vel": pygame.Vector2(0, 0)}]
                    reset_ball(balls[0]["pos"], balls[0]["vel"])

            # Update power-ups falling + pickup
            powerups_to_remove = []
            for pi, p in enumerate(powerups):
                p["rect"].y += POWERUP_FALL_SPEED

                # Off screen
                if p["rect"].top > HEIGHT:
                    powerups_to_remove.append(pi)
                    continue

                # Collected by paddle
                if p["rect"].colliderect(paddle):
                    lives = apply_powerup(
                        p["type"],
                        paddle=paddle,
                        balls=balls,
                        lives=lives,
                        active_effects=active_effects,
                    )
                    powerups_to_remove.append(pi)

            for index in reversed(powerups_to_remove):
                powerups.pop(index)

        # -----------------------------
        # Draw
        # -----------------------------
        screen.fill(BG_COLOR)

        # Bricks
        for b in bricks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=6)

        # Paddle
        pygame.draw.rect(screen, (220, 220, 220), paddle, border_radius=8)

        # Balls
        for ball in balls:
            pygame.draw.circle(
                screen,
                (240, 240, 240),
                (int(ball["pos"].x), int(ball["pos"].y)),
                BALL_RADIUS,
            )

        # Power-ups (simple colored squares with letter)
        for p in powerups:
            pygame.draw.rect(screen, p["color"], p["rect"], border_radius=6)
            letter = p["type"][0]  # W/S/L/M
            t = font.render(letter, True, (10, 10, 10))
            screen.blit(t, (p["rect"].centerx - t.get_width() // 2, p["rect"].centery - t.get_height() // 2))

        # HUD
        effects_txt = []
        now = pygame.time.get_ticks()
        if active_effects.get("WIDE", 0) > now:
            effects_txt.append("WIDE")
        if active_effects.get("SLOW", 0) > now:
            effects_txt.append("SLOW")

        hud = font.render(
            f"Score: {score}   Lives: {lives}   Balls: {len(balls)}   Effects: {', '.join(effects_txt) or 'None'}   (P)ause  (R)estart  (Esc)Quit",
            True,
            TEXT_COLOR,
        )
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
