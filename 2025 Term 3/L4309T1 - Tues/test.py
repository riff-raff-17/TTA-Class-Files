# Pong vs Simple AI
# Run: python pong_ai.py
# Controls: W/S = Move (player is left paddle), P = Pause, R = Reset, Esc = Quit
# Requires: pip install pygame

import sys
import random
import math
import pygame

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 900, 540
MARGIN = 20
PADDLE_W, PADDLE_H = 14, 100
BALL_SIZE = 14
PLAYER_SPEED = 7
AI_MAX_SPEED = 6
BALL_SPEED = 6
BALL_SPEED_MAX = 14
FPS = 60

# AI difficulty (0 = easy, 1 = medium, 2 = hard)
DIFFICULTY = 1

# Difficulty tuning
AI_REACTION = [10, 6, 3][DIFFICULTY]    # frames between decisions
AI_NOISE = [22, 12, 4][DIFFICULTY]      # vertical jitter range (px)
AI_AIM_BIAS = [0.35, 0.2, 0.08][DIFFICULTY]  # how strongly AI aims for ball center (less = stronger)
AI_SPEED = [AI_MAX_SPEED*0.8, AI_MAX_SPEED*0.95, AI_MAX_SPEED*1.05][DIFFICULTY]

# Colors
BG = (12, 14, 22)
FG = (235, 235, 245)
ACCENT = (120, 120, 140)

pygame.init()
pygame.display.set_caption("Pong vs AI")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas,menlo,monaco,monospace", 28)
big_font = pygame.font.SysFont("consolas,menlo,monaco,monospace", 64)

# -----------------------------
# Entities
# -----------------------------
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_W, PADDLE_H)
        self.speed = 0.0

    def move(self, dy):
        self.rect.y += int(dy)
        if self.rect.top < MARGIN:
            self.rect.top = MARGIN
        if self.rect.bottom > HEIGHT - MARGIN:
            self.rect.bottom = HEIGHT - MARGIN

    def draw(self, surf):
        pygame.draw.rect(surf, FG, self.rect, border_radius=6)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.vx = 0.0
        self.vy = 0.0

    def reset(self, toward_left=None):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        angle = random.uniform(-0.35*math.pi, 0.35*math.pi)
        speed = BALL_SPEED * random.uniform(0.95, 1.05)
        direction = -1 if (toward_left if toward_left is not None else random.choice([True, False])) else 1
        self.vx = direction * speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Top/bottom walls
        if self.rect.top <= MARGIN and self.vy < 0:
            self.rect.top = MARGIN
            self.vy *= -1
        if self.rect.bottom >= HEIGHT - MARGIN and self.vy > 0:
            self.rect.bottom = HEIGHT - MARGIN
            self.vy *= -1

    def draw(self, surf):
        pygame.draw.rect(surf, FG, self.rect, border_radius=4)

# -----------------------------
# Helpers
# -----------------------------
def draw_center_line(surf):
    dash_h = 16
    gap = 16
    x = WIDTH//2 - 2
    y = MARGIN
    while y < HEIGHT - MARGIN:
        pygame.draw.rect(surf, ACCENT, (x, y, 4, dash_h), border_radius=2)
        y += dash_h + gap

def draw_hud(surf, p_score, ai_score, paused):
    # Border margins
    pygame.draw.rect(surf, ACCENT, (MARGIN-2, MARGIN-2, WIDTH-2*MARGIN+4, HEIGHT-2*MARGIN+4), 2, border_radius=12)

    score_text = font.render(f"{p_score}   :   {ai_score}", True, FG)
    surf.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))

    controls = font.render("W/S move • P pause • R reset • Esc quit", True, ACCENT)
    surf.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - controls.get_height() - 6))

    if paused:
        t = big_font.render("PAUSED", True, FG)
        surf.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - t.get_height()//2 - 40))
        s = font.render("Press P to resume", True, ACCENT)
        surf.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 - s.get_height()//2 + 20))

def clamp_ball_speed(ball):
    speed = math.hypot(ball.vx, ball.vy)
    if speed > BALL_SPEED_MAX:
        scale = BALL_SPEED_MAX / max(speed, 0.0001)
        ball.vx *= scale
        ball.vy *= scale

def reflect_from_paddle(ball, paddle_rect):
    # Compute hit position relative to paddle center to add spin
    offset = ((ball.rect.centery - paddle_rect.centery) / (paddle_rect.height / 2))
    offset = max(-1.25, min(1.25, offset))
    speed = math.hypot(ball.vx, ball.vy) * 1.05 + 0.1

    # Determine new angle based on offset (max ~50 degrees)
    max_angle = math.radians(50)
    angle = offset * max_angle
    direction = -1 if ball.vx > 0 else 1  # bounce horizontally
    ball.vx = direction * speed * math.cos(angle)
    ball.vy = speed * math.sin(angle)
    clamp_ball_speed(ball)

def ai_target_y(ball, ai_rect):
    # Very lightweight "prediction": if ball moving towards AI, project where it will cross AI x,
    # accounting for top/bottom bounces. Otherwise, drift to center.
    if ball.vx > 0:
        # time to reach AI x
        distance_x = (ai_rect.left - ball.rect.right)
        if distance_x <= 0:
            return ball.rect.centery
        t = distance_x / max(ball.vx, 0.001)

        # predict y with wall reflections
        projected_y = ball.rect.centery + ball.vy * t
        # mirror across top/bottom bounds to simulate bounces
        top = MARGIN + BALL_SIZE//2
        bottom = HEIGHT - MARGIN - BALL_SIZE//2
        span = bottom - top
        if span <= 0:
            return ball.rect.centery

        # Convert to triangle-wave via modular arithmetic
        relative = (projected_y - top) % (2*span)
        if relative > span:
            projected_y = top + (2*span - relative)
        else:
            projected_y = top + relative
        # add some imperfection
        noise = random.uniform(-AI_NOISE, AI_NOISE)
        aim = ai_rect.centery * AI_AIM_BIAS + projected_y * (1 - AI_AIM_BIAS) + noise
        return aim
    else:
        return HEIGHT // 2

def main():
    player = Paddle(MARGIN + 10, HEIGHT//2 - PADDLE_H//2)
    ai = Paddle(WIDTH - MARGIN - 10 - PADDLE_W, HEIGHT//2 - PADDLE_H//2)
    ball = Ball()
    ball.reset(toward_left=random.choice([True, False]))

    p_score = 0
    ai_score = 0
    paused = False
    ai_timer = 0
    ai_goal_y = ai.rect.centery

    while True:
        # --- Events
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
                    p_score = ai_score = 0
                    player.rect.centery = HEIGHT//2
                    ai.rect.centery = HEIGHT//2
                    ball.reset(toward_left=random.choice([True, False]))

        # --- Update
        keys = pygame.key.get_pressed()
        if not paused:
            dy = 0
            if keys[pygame.K_w]:
                dy -= PLAYER_SPEED
            if keys[pygame.K_s]:
                dy += PLAYER_SPEED
            player.move(dy)

            # AI logic
            ai_timer -= 1
            if ai_timer <= 0:
                ai_goal_y = ai_target_y(ball, ai.rect)
                ai_timer = AI_REACTION

            # move AI towards goal
            if ai.rect.centery < ai_goal_y - 4:
                ai.move(AI_SPEED)
            elif ai.rect.centery > ai_goal_y + 4:
                ai.move(-AI_SPEED)

            # Ball
            ball.update()

            # Collisions with paddles
            if ball.rect.colliderect(player.rect) and ball.vx < 0:
                ball.rect.left = player.rect.right
                reflect_from_paddle(ball, player.rect)

            if ball.rect.colliderect(ai.rect) and ball.vx > 0:
                ball.rect.right = ai.rect.left
                reflect_from_paddle(ball, ai.rect)

            # Scoring
            if ball.rect.left <= 0:
                ai_score += 1
                ball.reset(toward_left=False)
            elif ball.rect.right >= WIDTH:
                p_score += 1
                ball.reset(toward_left=True)

        # --- Draw
        screen.fill(BG)
        draw_center_line(screen)
        draw_hud(screen, p_score, ai_score, paused)
        player.draw(screen)
        ai.draw(screen)
        ball.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()