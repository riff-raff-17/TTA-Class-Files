import cv2
import numpy as np
import mediapipe as mp
import time
from collections import deque

PINCH_DIST_PX = 60
SMOOTHING = 0.2
INITIAL_THICKNESS = 6
COLORS = [
    (255, 255, 255),
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
]

thickness = INITIAL_THICKNESS
color_idx = 0
drawing = False
strokes = []
current = deque(maxlen=4096)
canvas = None
last_smoothed = None

def lerp(a, b, t):
    return a + (b - a) * t

def smooth_point(prev, cur, alpha = SMOOTHING):
    return cur if prev is None else (int(lerp(prev[0], cur[0], alpha)),
                                     int(lerp(prev[1], cur[1], alpha)))
def ensure_canvas(h, w):
    global canvas
    if canvas is None or canvas.shape[:2] != (h, w):
        canvas = np.zeros((h, w, 4), dtype=np.uint8)

def draw_polyline_both(bgr_img, rgba_img, pts, color_bgr, thick):
    if len(pts) < 2:
        return
    cv2.polylines(bgr_img, [pts], isClosed=False, color=color_bgr, 
                  thickness=thick, lineType=cv2.LINE_AA)
    
def blend_overlay(frame, overlay, alpha=0.75):
    return cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0)

def landmark_xy(lm, idx, w, h):
    p = lm.landmark[idx]
    return int(p.x * w), int(p.y * h)

def start_stroke(pt):
    current.clear()
    current.append(pt)

def finish_stroke():
    if len(current) > 1:
        strokes.append({"pts" : np.array(current, dtype=np.int32),
                        "color": COLORS[color_idx], "thick": thickness})
        
