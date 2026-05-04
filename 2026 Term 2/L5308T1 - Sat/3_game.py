"""
=============================================================
Hand-Controlled Shooting Game (MediaPipe + Pygame)
=============================================================
Your character sits at the CENTER of the screen.

HAND CONTROLS:
  - Index finger tip (landmark 8) sets your AIM DIRECTION
    (the angle from the screen center to your fingertip).
  - Pinch (thumb tip + index tip close together) FIRES a bullet
    in the aimed direction. Release and re-pinch to fire again.

ENEMIES  (red circles)  — drift toward you from the edges.
  ✗ Let one reach you   → lose 1 life
  ✓ Shoot one           → +10 points

FRIENDLIES  (green circles) — also drift toward you from the edges.
  ✓ Let one reach you   → +5 points  (you "saved" them)
  ✗ Shoot one           → lose 1 life

Lives: 5  — game over when lives reach 0.
Difficulty ramps up every 10 seconds (more spawns, faster).

Depends on: hand_common.py  (in the same directory)

Run:
    pip install pygame opencv-python mediapipe
    python hand_shooting_game.py

Controls:
    ESC / close window — quit
    R (on game-over screen) — restart
=============================================================
"""

import cv2
import mediapipe as mp
import pygame
import math
import random
import time

from hand_common import make_detector, INDEX_TIP, THUMB_TIP, FPSCounter

# --- Config ---
SCREEN_W, SCREEN_H = 960, 640
CAM_W, CAM_H = 640, 480
CENTER = (SCREEN_W // 2, SCREEN_H // 2)

SMOOTHING = 0.70 # finger-tip smoothing (0=raw, 1=frozen)
PINCH_THRESHOLD = 0.05 # normalised distance for pinch detection

# Cjaracter
CHAR_RADIUS = 30

# Bullets
BULLET_SPEED = 10
BULLET_RADIUS = 6
BULLET_LIFETIME = 1.2 # seconds before bullet disappears off-screen

# Entities
ENEMY_RADIUS = 18
FRIENDLY_RADIUS = 16
BASE_ENTITY_SPEED = 2.4 # pixels per frame at wave 1
SPAWN_INTERVAL = 2.0 # seconds between spawns at wave 1
ENEMY_RATIO = 0.65 # fraction of spawns that are enemies

REACH_RADIUS = CHAR_RADIUS + 4 # how close = "reached" the character

# Shooting
FIRE_RATE = 0.12 # seconds between bullets while pinching (~8 bullets/sec)

# Lives
MAX_LIVES = 5

# Aim line
AIM_LINE_LEN = 80

# Colors
BG = (12, 14, 22)
CHAR_COLOR = (80, 200, 255)
CHAR_PINCH = (255, 180, 60)
AIM_COLOR = (255, 255, 255)
BULLET_COLOR = (255, 230, 80)
ENEMY_COLOR = (220, 50, 50)
FRIEND_COLOR = (60, 200, 100)
HUD_COLOR = (220, 220, 220)
LIFE_COLOR = (220, 50, 80)
WARN_COLOR = (255, 100, 100)
SCORE_COLOR = (255, 220, 60)

# Helpers

def norm_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def lerp(a, b, t):
    return a + (b - a) * t

def angle_to(cx, cy, tx, ty):
    """Angle in radians from (cx, cy) toward (tx, ty)."""
    return math.atan2(ty - cy, tx - cx)

def spawn_edge_position():
    """Return a random (x, y) just outside the screen edges."""
    side = random.randint(0, 3)
    margin = 30
    if side == 0:  # top
        return random.randint(0, SCREEN_W), -margin
    elif side == 1:  # bottom
        return random.randint(0, SCREEN_W), SCREEN_H + margin
    elif side == 2:  # left
        return -margin, random.randint(0, SCREEN_H)
    else:  # right
        return SCREEN_W + margin, random.randint(0, SCREEN_H)

def circle_collide(ax, ay, ar, bx, by, br):
    return math.hypot(ax - bx, ay - by) < ar + br

# ---------------------------------------------------------------------------
# Entity classes
# ---------------------------------------------------------------------------
class Entity:
    def __init__(self, x, y, speed, radius, color, is_enemy):
        self.x, self.y = float(x), float(y)
        self.speed = speed
        self.radius = radius
        self.color = color
        self.is_enemy = is_enemy
        self.alive = True
        # flash effect when spawned
        self.spawn_time = time.time()

    def update(self):
        cx, cy = CENTER
        angle = angle_to(self.x, self.y, cx, cy)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed
    
    def draw(self, surface):
        age = time.time() - self.spawn_time
        # Brief white flash on spawn
        if age < 0.15:
            t = age / 0.15
            r = int(lerp(255, self.color[0], t))
            g = int(lerp(255, self.color[1], t))
            b = int(lerp(255, self.color[2], t))
            color = (r, g, b)
        else:
            color = self.color
        
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, color, (ix, iy), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), self.radius, 2)

        # Label
        label = "E" if self.is_enemy else "F"
        font_small = pygame.font.SysFont("consolas", 13, bold=True)
        lbl = font_small.render(label, True, (255, 255, 255))
        surface.blit(lbl, (ix - lbl.get_width() // 2, iy - lbl.get_height() // 2))

    def reached_center(self):
        cx, cy = CENTER
        return math.hypot(self.x - cx, self.y - cy) < REACH_RADIUS + self.radius
    
class Bullet:
    def __init__(self, x, y, angle):
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.alive = True
        self.born = time.time()

    def update(self):
        self.x += self.vx
        self.y += self.vy
        age = time.time() - self.born
        if age > BULLET_LIFETIME:
            self.alive = False
        # out of screen
        pad = 40
        if not (-pad < self.x < SCREEN_W + pad and -pad < self.y < SCREEN_H + pad):
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(
            surface, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS
        )
        # glow
        glow_surf = pygame.Surface(
            (BULLET_RADIUS * 4, BULLET_RADIUS * 4), pygame.SRCALPHA
        )
        pygame.draw.circle(
            glow_surf,
            (*BULLET_COLOR, 60),
            (BULLET_RADIUS * 2, BULLET_RADIUS * 2),
            BULLET_RADIUS * 2,
        )
        surface.blit(
            glow_surf,
            (int(self.x) - BULLET_RADIUS * 2, int(self.y) - BULLET_RADIUS * 2),
        )

# ---------------------------------------------------------------------------
# Particle effect
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y ,color):
        self.x, self.y = float(x), float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 1.0  # 1.0 -> 0.0

    def update(self, dt):
        self.x += self.vx
        self.y = self.vy
        self.vy += 0.1 # gravity
        self.life -= dt * 2.5
        return self.life > 0