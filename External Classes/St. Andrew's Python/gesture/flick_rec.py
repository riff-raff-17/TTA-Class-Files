import cv2
import mediapipe as mp
from ugot import ugot
import numpy as np
import collections
import time
import math

got = ugot.UGOT()
got.initialize('192.168.88.1')
got.open_camera()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# -----------------------------
# Gesture detection parameters
# -----------------------------
INDEX_TIP_ID = 8

# Distance threshold as a fraction of frame size (normalized coords 0..1)
# e.g., 0.16 = ~16% of the smaller image dimension as a net movement
DIST_THRESH_NORM = 0.16

# Gesture must complete within this time window (seconds)
MAX_GESTURE_TIME = 0.35

# Ignore additional detections for this long after a trigger (seconds)
COOLDOWN_SEC = 0.80

# Keep this many recent samples for detection (roughly ~100ms–200ms worth)
HISTORY_LEN = 7

# Optional: press 'l' to toggle labels on/off during runtime
show_labels = True

# -----------------------------
# Helpers: action dispatch
# -----------------------------
def call_if_exists(obj, name_candidates, *args, **kwargs):
    """Try several method names, return True if any was called."""
    for name in name_candidates:
        fn = getattr(obj, name, None)
        if callable(fn):
            fn(*args, **kwargs)
            return True
    return False

def do_forward():
    if not call_if_exists(got, ["forward", "move_forward", "go_forward"]):
        print("[robot] forward() not found on UGOT; replace with your method.")

def do_backward():
    if not call_if_exists(got, ["backward", "move_backward", "go_backward"]):
        print("[robot] backward() not found on UGOT; replace with your method.")

def do_left():
    # Try both strafing and turning names
    if not call_if_exists(got, ["left", "turn_left", "rotate_left"]):
        print("[robot] left() / turn_left() not found; replace with your method.")

def do_right():
    if not call_if_exists(got, ["right", "turn_right", "rotate_right"]):
        print("[robot] right() / turn_right() not found; replace with your method.")

ACTION_MAP = {
    "up": do_forward,
    "down": do_backward,
    "left": do_left,
    "right": do_right,
}

# -----------------------------
# Flick detector
# -----------------------------
history = collections.deque(maxlen=HISTORY_LEN)  # (x_norm, y_norm, t)
last_trigger_time = 0
last_action_text = ""     # for on-screen feedback
last_action_time = 0

def detect_flick(hist):
    """Return one of: 'up','down','left','right', or None."""
    if len(hist) < 2:
        return None

    # Use earliest vs latest to capture net movement
    x0, y0, t0 = hist[0]
    x1, y1, t1 = hist[-1]

    dt = t1 - t0
    if dt <= 0 or dt > MAX_GESTURE_TIME:
        return None

    dx = x1 - x0
    dy = y1 - y0

    # Normalize distance by using Euclidean norm in normalized coords
    dist = math.hypot(dx, dy)
    if dist < DIST_THRESH_NORM:
        return None

    # Determine principal direction
    # Note: y increases downward in image coords, so "up" is negative dy
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"

# -----------------------------
# Video loop
# -----------------------------
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    while True:
        frame = got.read_camera_data()
        if not frame:
            break
        nparr = np.frombuffer(frame, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        flipped = cv2.flip(frame, 1)  # mirror view
        h, w = flipped.shape[:2]
        frame_rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = hands.process(frame_rgb)

        # Draw hand landmarks + numeric labels
        candidate_xy_norm = None  # we'll track the first detected hand's index tip

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks & connections
                mp_drawing.draw_landmarks(
                    flipped,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )

                # Grab index fingertip in normalized coords for gesture detection
                tip = hand_landmarks.landmark[INDEX_TIP_ID]
                candidate_xy_norm = (float(tip.x), float(tip.y))  # 0..1

                if show_labels:
                    # Label each landmark index (0..20)
                    for idx, lm in enumerate(hand_landmarks.landmark):
                        lx = int(lm.x * w)
                        ly = int(lm.y * h)
                        cv2.putText(flipped, str(idx), (lx + 4, ly - 4),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(flipped, str(idx), (lx + 4, ly - 4),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

                # Use only the first hand for flick detection (break here if desired)
                break

        # Update flick history with the latest fingertip point
        now = time.time()
        if candidate_xy_norm is not None:
            x_norm, y_norm = candidate_xy_norm
            history.append((x_norm, y_norm, now))

            # Draw fingertip trail for visualization
            pts = []
            for (x, y, _) in history:
                pts.append((int(x * w), int(y * h)))
            for i in range(1, len(pts)):
                cv2.line(flipped, pts[i-1], pts[i], (0, 255, 255), 2)

            # Try to detect flick, with cooldown
            if (now - last_trigger_time) >= COOLDOWN_SEC:
                direction = detect_flick(history)
                if direction:
                    # Trigger mapped action
                    action_fn = ACTION_MAP.get(direction)
                    if action_fn:
                        action_fn()
                    last_trigger_time = now
                    last_action_text = f"Flick {direction.upper()}!"
                    last_action_time = now

        # UI hints
        cv2.putText(flipped, "Press 'L' to toggle labels, 'Q' or ESC to quit",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(flipped, "Press 'L' to toggle labels, 'Q' or ESC to quit",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        # Recent action banner
        if last_action_text and (now - last_action_time) < 1.2:
            cv2.putText(flipped, last_action_text,
                        (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(flipped, last_action_text,
                        (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

        # Show preview
        cv2.imshow("MediaPipe Hands — Flick Gestures", flipped)

        # Keys
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break
        elif key == ord('l'):
            show_labels = not show_labels

cv2.destroyAllWindows()
