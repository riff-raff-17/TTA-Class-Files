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

import mediapipe as mp
import pygame
import math
import random
import time

from hand_common import (
    make_detector,
    INDEX_TIP,
    THUMB_TIP,
    FPSCounter,
)

# --- Config ---
SCREEN_W = SCREEN_H = 960, 640
CAM_W, CAM_H = 640, 480
CENTER = (SCREEN_W // 2, SCREEN_H // 2)

SMOOTHING = 0.70  # finger-tip smoothing (0=raw, 1=frozen)
PINCH_THRESHOLD = 0.05  # normalised distance for pinch detection

# Character
CHAR_RADIUS = 30

# Bullets 
BULLET_SPEED = 10
BULLET_RADIUS = 6
BULLET_LIFETIME = 1.2 # seconds before bullet disappers off-screen

# Entities
ENEMY_RADIUS = 18
FRIENDLY_RADIUS = 16
BASE_ENTITY_SPEED = 2.4  # pixels per frame at wave 1
SPAWN_INTERVAL = 2.0  # seconds between spawns at wave 1
ENEMY_RATIO = 0.65  # fraction of spawns that are enemies

REACH_RADIUS = CHAR_RADIUS + 4  # how close = "reached" the character

# Shooting
FIRE_RATE = 0.12  # seconds between bullets while pinching (~8 bullets/sec)

# Lives
MAX_LIVES = 5

# Aim line
AIM_LINE_LEN = 80

# --- Colors ---
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