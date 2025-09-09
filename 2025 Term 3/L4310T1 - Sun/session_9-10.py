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
        
# Main loop
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Error :( tell mr rafa")

fps_hist = deque(maxlen=30)
last_time = time.time()

mp_hands = mp.solutions.hands
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        ensure_canvas(h, w)

        # Mediapipe
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pinch, index_tip = False, None
        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0]
            ix, iy = landmark_xy(lm, 8, w, h)
            tx, ty = landmark_xy(lm, 4, w, h)
            index_tip = (ix, iy)
            pinch = ((ix - tx) ** 2 + (iy - ty) ** 2) ** 0.5 < PINCH_DIST_PX

        # smooth points
        smoothed = smooth_point(last_smoothed, index_tip) if index_tip else None
        last_smoothed = smoothed if index_tip else None

        # Drawing state
        if pinch and smoothed:
            if not drawing:
                drawing = True
                start_stroke(smoothed)
            else:
                current.append(smoothed)
        elif drawing:
            drawing = False
            finish_stroke()
        
        # Redraw overlay + RGBA canvas
        overlay = frame.copy()
        canvas[:] = 0
        for s in strokes:
            draw_polyline_both(overlay, canvas, s["pts"], s["color"], s["thick"])
        if drawing and len(current) > 1:
            pts = np.array(current, dtype=np.int32)
            draw_polyline_both(overlay, canvas, pts, COLORS[color_idx], thickness)
        
        if smoothed:
            cv2.circle(overlay, smoothed, 6, COLORS[color_idx], -1, cv2.LINE_AA)
        
        hud = overlay.copy()
        cv2.rectangle(hud, (0, 0), (w, 40), (0, 0, 0), -1)
        display = blend_overlay(overlay, hud, alpha=0.2)
        cv2.putText(display, f"Pinch to draw | Color {color_idx+1} | Thickness {thickness}px",
                    (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)