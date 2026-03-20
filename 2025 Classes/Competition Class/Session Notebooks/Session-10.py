import pygame
import random
import sys
import math                # ← for distance calculation

# ───── Setup ──────────────────────────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Dodger")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 200, 50)
BULLET_COLOR = (200, 50, 50)
ENEMY_COLOR  = (200, 200, 50)  # ← enemy color

# ───── Player ─────────────────────────────────────────────────────────────────
PLAYER_SIZE  = 30
PLAYER_SPEED = 5
player = pygame.Rect(
    WIDTH//2 - PLAYER_SIZE//2,
    HEIGHT//2 - PLAYER_SIZE//2,
    PLAYER_SIZE, PLAYER_SIZE
)

# ───── Enemy (new) ───────────────────────────────────────────────────────────
ENEMY_SIZE  = 30
ENEMY_SPEED = 3
# spawn enemy at a random location
enemy = pygame.Rect(
    random.randrange(0, WIDTH-ENEMY_SIZE),
    random.randrange(0, HEIGHT-ENEMY_SIZE),
    ENEMY_SIZE, ENEMY_SIZE
)

# ───── Bullets & Difficulty ──────────────────────────────────────────────────
BULLET_SIZE        = 10
INITIAL_BULLET_SPEED = 10
MAX_BULLET_SPEED     = 20
INITIAL_SPAWN_DELAY  = 500   # ms between bullets at start
MIN_SPAWN_DELAY      = 25
SPAWN_DECREASE       = 10    # ms less delay after each spawn
SPEED_INCREASE       = 0.1   # bullet speed increment per spawn

bullets      = []            # list of {'rect':…, 'vel':…}
spawn_delay  = INITIAL_SPAWN_DELAY
bullet_speed = INITIAL_BULLET_SPEED
last_spawn   = pygame.time.get_ticks()
start_time   = last_spawn

# ───── Main Loop ──────────────────────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(60)  # cap at 60 FPS

    # — Handle events
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False

    # — Move player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += PLAYER_SPEED
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.y += PLAYER_SPEED
    player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # — Move enemy toward player (new)
    dx = player.centerx - enemy.centerx
    dy = player.centery - enemy.centery
    dist = math.hypot(dx, dy)
    if dist:
        enemy.x += ENEMY_SPEED * dx / dist
        enemy.y += ENEMY_SPEED * dy / dist
    enemy.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # — Spawn bullets when enough time has passed
    now = pygame.time.get_ticks()
    if now - last_spawn >= spawn_delay:
        last_spawn = now
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x, y = random.randrange(0, WIDTH), 0
            vel = (0, bullet_speed)
        elif side == 'bottom':
            x, y = random.randrange(0, WIDTH), HEIGHT
            vel = (0, -bullet_speed)
        elif side == 'left':
            x, y = 0, random.randrange(0, HEIGHT)
            vel = (bullet_speed, 0)
        else:  # right
            x, y = WIDTH, random.randrange(0, HEIGHT)
            vel = (-bullet_speed, 0)
        rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        bullets.append({'rect': rect, 'vel': vel})

        # ramp difficulty
        spawn_delay  = max(MIN_SPAWN_DELAY, spawn_delay - SPAWN_DECREASE)
        bullet_speed = min(MAX_BULLET_SPEED, bullet_speed + SPEED_INCREASE)

    # — Update bullets and remove off-screen ones
    for b in bullets[:]:
        b['rect'].x += b['vel'][0]
        b['rect'].y += b['vel'][1]
        if not screen.get_rect().colliderect(b['rect']):
            bullets.remove(b)

    # — Check for collisions (bullets or enemy)
    if any(player.colliderect(b['rect']) for b in bullets) or player.colliderect(enemy):
        running = False

    # — Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    pygame.draw.rect(screen, ENEMY_COLOR,  enemy)  # ← draw the chaser
    for b in bullets:
        pygame.draw.rect(screen, BULLET_COLOR, b['rect'])
    elapsed_sec = (now - start_time) // 1000
    txt = font.render(f"Time: {elapsed_sec}s", True, WHITE)
    screen.blit(txt, (10, 10))
    pygame.display.flip()

# ───── Game Over ──────────────────────────────────────────────────────────────
screen.fill(BLACK)
go_txt    = font.render("Game Over", True, WHITE)
score_txt = font.render(f"You survived {elapsed_sec}s", True, WHITE)
screen.blit(go_txt,    (WIDTH//2 - go_txt.get_width()//2,    HEIGHT//2 - 50))
screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, HEIGHT//2 + 10))
pygame.display.flip()
pygame.time.delay(3000)

pygame.quit()
sys.exit()
