"""
robot_finger_control.py — Main entry point.
Move your index finger to control the robot:
  - Center (deadzone): STOP
  - Up:    FORWARD
  - Down:  BACKWARD
  - Left:  LEFT
  - Right: RIGHT

Press 'q' to quit.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import RunningMode

from helpers import get_direction, draw_overlay, download_model, MODEL_PATH

# --- Robot functions ---
def robot_forward():
    print("FORWARD")

def robot_backward():
    print("BACKWARD")

def robot_left():
    print("LEFT")

def robot_right():
    print("RIGHT")

def dispatch(direction):
    """Call the appropriate robot function."""
    actions = {
        "forward": robot_forward
    }