"""
=============================================================
PART 2 — The HandController
=============================================================
Goal: build a reusable HandController class that sits on top
of Part 1's foundation and converts raw landmarks into clean
game-ready values:

    controller.gesture   -> "IDLE" | "THRUST" | "SHOOT" | "BRAKE"
    controller.steering  -> float  -1.0 (left) .. +1.0 (right)
    controller.tilt_deg  -> raw tilt angle in degrees (for debug)

What this file adds on top of Part 1:
  - HandController class                (new)
  - draw_tilt_arrow()                   (new drawing helper)
  - draw_steering_bar()                 (new drawing helper)
  - draw_gesture_panel()                (new drawing helper)
  - main loop that shows all the above  (new)

What this file does NOT touch:
  - hand_common.py                      (unchanged)
  - part1_mediapipe_hello.py            (unchanged)

Depends on: hand_common.py (must be in the same folder)

Run:
    python part2_hand_controller.py

Controls:
    Q  — quit
    D  — toggle debug overlay
=============================================================
"""

import cv2
import mediapipe as mp
import math
from hand_common import (
    make_detector,
    draw_hand,
    FPSCounter,
    WRIST, INDEX_MCP, FINGER_TIPS, FINGER_MCPS,
    HAND_CONNECTIONS, lm_px,
)

# ---------------------------------------------------------------------------
# HandController
# ---------------------------------------------------------------------------
# This class is the only new concept in Part 2.
# Its job: take a list of 21 landmarks, return game-ready values.
#
# Design rules:
#   - Never touches the camera or detector directly.
#   - All outputs are plain Python types (str, float).
#   - Safe to call with None when no hand is visible.
#   - Will be imported unchanged by Part 3 onwards.
# ---------------------------------------------------------------------------

class HandController:

    IDLE = "IDLE"
    THRUST = "THRUST"
    SHOOT = "SHOOT"
    BRAKE = "BRAKE"

    # Steering tuning
    DEAD_ZONE_DEG = 10.0  # tilt smaller than this -> steering = 0 (no drift)
    MAX_TILT_DEG = 40.0  # tilt at this angle -> steering = ±1.0 (full)
    