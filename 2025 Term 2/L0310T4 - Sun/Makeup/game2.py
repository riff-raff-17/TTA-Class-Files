import pygame
import sys
import math
import random
from pygame.math import Vector2

# --- CONFIGURATION ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

PLAYER_SPEED     = 300      # pixels/sec
BULLET_SPEED     = 500      # pixels/sec
FIRE_RATE        = 7          # shots/sec
BULLET_LIFETIME  = 2.0      # sec
PLAYER_RADIUS    = 20

ENEMY_SPAWN_MS   = 400     # spawn every 2s
ENEMY_SPEED      = 150      # random‐movers
CHASER_SPEED     = 200      # chasers
ENEMY_RADIUS     = 20

# --- PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter with Challenges (Fixed)")
clock = pygame.time.Clock()

# --- FONTS ---
font     = pygame.font.Font(None, 36)
font_big = pygame.font.Font(None, 74)

# --- PLAYER SPRITE ---
player_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.polygon(player_surf, (255,255,255), [(20,0),(0,40),(40,40)])

# --- CHALLENGES ---
CHALLENGES = [
    {"type":"no_shoot",   "desc":"Don't shoot for 5s",  "duration":5.0, "bonus":20},
    {"type":"no_move",    "desc":"Don't move for 5s",  "duration":5.0, "bonus":20},
    {"type":"streak_blue","desc":"Shoot 5 blues",      "count":5,     "bonus":30},
    {"type":"streak_red", "desc":"Shoot 5 reds",       "count":5,     "bonus":30},
]

def pick_challenge():
    """Pick and initialize a fresh challenge dict."""
    ch = random.choice(CHALLENGES).copy()
    ch["streak"] = 0
    return ch

class Bullet:
    def __init__(self, pos, direction):
        self.pos        = Vector2(pos)
        self.vel        = direction * BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks() / 1000.0
        self.radius     = 5
    def update(self, dt):    self.pos += self.vel * dt
    def draw(self, surf):    pygame.draw.circle(surf, (255,50,50), self.pos, self.radius)
    def expired(self, now):  return now - self.spawn_time > BULLET_LIFETIME

class Enemy:
    def __init__(self, kind, pos):
        self.kind   = kind
        self.pos    = Vector2(pos)
        self.radius = ENEMY_RADIUS
        if kind=='random':
            angle = random.uniform(0,2*math.pi)
            self.vel = Vector2(math.cos(angle), math.sin(angle)) * ENEMY_SPEED
        else:
            self.vel = Vector2(0,0)
    def update(self, dt, player_pos):
        if self.kind=='chaser':
            d = player_pos - self.pos
            if d.length_squared()>0:
                self.vel = d.normalize() * CHASER_SPEED
        self.pos += self.vel * dt
        if self.kind=='random':
            if not (0<=self.pos.x<=SCREEN_WIDTH):  self.vel.x *= -1
            if not (0<=self.pos.y<=SCREEN_HEIGHT): self.vel.y *= -1
    def draw(self, surf):
        c = (255,0,0) if self.kind=='random' else (0,0,255)
        pygame.draw.circle(surf, c, self.pos, self.radius)

def run_game():
    player_pos   = Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    lives, score = 3, 0
    bullets, enemies = [], []

    time_between_shots   = 1.0 / FIRE_RATE
    time_since_last_shot = 0.0

    now = pygame.time.get_ticks() / 1000.0
    last_shot_time = now
    last_move_time = now

    challenge = pick_challenge()

    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, ENEMY_SPAWN_MS)

    running = True
    while running:
        dt  = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        time_since_last_shot += dt

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == SPAWN_ENEMY:
                side = random.choice(['left','right','top','bottom'])
                if side=='left':    pos=(0,random.uniform(0,SCREEN_HEIGHT))
                elif side=='right': pos=(SCREEN_WIDTH,random.uniform(0,SCREEN_HEIGHT))
                elif side=='top':   pos=(random.uniform(0,SCREEN_WIDTH),0)
                else:               pos=(random.uniform(0,SCREEN_WIDTH),SCREEN_HEIGHT)
                kind = random.choice(['random','chaser'])
                enemies.append(Enemy(kind, pos))

        # --- Movement ---
        keys = pygame.key.get_pressed()
        mv = Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN])  - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        if mv.length_squared()>0:
            mv = mv.normalize()
            last_move_time = now
        player_pos += mv * PLAYER_SPEED * dt
        player_pos.x = max(0, min(SCREEN_WIDTH, player_pos.x))
        player_pos.y = max(0, min(SCREEN_HEIGHT, player_pos.y))

        # --- Aiming & Shooting ---
        mx, my = pygame.mouse.get_pos()
        aim    = Vector2(mx,my) - player_pos
        if aim.length_squared()>0:
            aim = aim.normalize()
        angle = math.degrees(math.atan2(-aim.y, aim.x)) - 90

        if keys[pygame.K_SPACE] and time_since_last_shot>=time_between_shots:
            bullets.append(Bullet(player_pos, aim))
            time_since_last_shot = 0.0
            last_shot_time = now

        # --- Update Entities ---
        for b in bullets[:]:
            b.update(dt)
            if b.expired(now): bullets.remove(b)
        for e in enemies:
            e.update(dt, player_pos)

        # --- Bullet–Enemy Collisions & Streak Logic ---
        for b in bullets[:]:
            for e in enemies[:]:
                if b.pos.distance_to(e.pos) < b.radius + e.radius:
                    bullets.remove(b)
                    enemies.remove(e)
                    score += 1
                    # if it’s a streak challenge, update streak
                    if "count" in challenge:
                        needed = "chaser" if challenge["type"]=="streak_blue" else "random"
                        if e.kind == needed:
                            challenge["streak"] += 1
                        else:
                            challenge["streak"] = 0
                    break

        # --- Enemy–Player Collisions ---
        for e in enemies[:]:
            if e.pos.distance_to(player_pos) < e.radius + PLAYER_RADIUS:
                enemies.remove(e)
                lives -= 1
                if lives<=0:
                    running = False
                break

        # --- Challenge Completion ---
        completed = False
        if "duration" in challenge:
            # timer‐based
            elapsed = (now - (last_shot_time if challenge["type"]=="no_shoot" else last_move_time))
            if elapsed >= challenge["duration"]:
                completed = True
        else:
            # streak‐based
            if challenge["streak"] >= challenge["count"]:
                completed = True

        if completed:
            score += challenge["bonus"]
            challenge = pick_challenge()
            last_shot_time = now
            last_move_time = now

        # --- Drawing ---
        screen.fill((30,30,30))
        for b in bullets: b.draw(screen)
        for e in enemies: e.draw(screen)
        rot = pygame.transform.rotate(player_surf, angle)
        screen.blit(rot, rot.get_rect(center=player_pos))

        # HUD: score & lives
        screen.blit(font.render(f"Score: {score}   Lives: {lives}", True, (255,255,255)), (10,10))

        # HUD: challenge + progress
        desc = challenge["desc"]
        if "duration" in challenge:
            elapsed = now - (last_shot_time if challenge["type"]=="no_shoot" else last_move_time)
            prog = max(0.0, min(elapsed, challenge["duration"]))
            prog_txt = f"{prog:.1f}/{challenge['duration']:.1f}s"
        else:
            prog_txt = f"{challenge['streak']}/{challenge['count']}"

        screen.blit(font.render(f"Challenge: {desc}", True, (200,200,50)), (10,50))
        screen.blit(font.render(prog_txt, True, (200,200,50)), (10,80))

        pygame.display.flip()

    return score

def game_over_screen(final_score):
    restart_btn = pygame.Rect(0,0,200,50)
    restart_btn.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
    while True:
        for ev in pygame.event.get():
            if ev.type in (pygame.QUIT, pygame.KEYDOWN):
                pygame.quit(); sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and restart_btn.collidepoint(ev.pos):
                return True

        screen.fill((0,0,0))
        screen.blit(font_big.render("GAME OVER", True, (255,0,0)),
                    font_big.render("GAME OVER", True, (255,0,0)).get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-40)))
        screen.blit(font.render(f"Final Score: {final_score}", True, (255,255,255)),
                    font.render(f"Final Score: {final_score}", True, (255,255,255)).get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        pygame.draw.rect(screen, (50,200,50), restart_btn)
        txt = font.render("Restart", True, (0,0,0))
        screen.blit(txt, txt.get_rect(center=restart_btn.center))
        pygame.display.flip()
        clock.tick(30)

# --- MAIN LOOP WITH RESTART ---
while True:
    final = run_game()
    if not game_over_screen(final):
        break

pygame.quit()
sys.exit()
