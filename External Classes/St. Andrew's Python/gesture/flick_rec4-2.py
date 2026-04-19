import cv2
import mediapipe as mp
from ugot import ugot
import numpy as np
import math
import time
from collections import deque

got = ugot.UGOT()
got.initialize('192.168.88.1')
got.open_camera()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

show_labels = True
show_tracer = True   # <-- [ADDED] toggle for the finger tracer

# Debounce / state
last_action = None

def forward():
    print("go forward")
    got.mecanum_move_speed(0, 30)

def backward():
    print("go back")
    got.mecanum_move_speed(1, 30)

def turn_left():
    print("go left")
    got.mecanum_turn_speed(2, 45)

def turn_right():
    print("go right")
    got.mecanum_turn_speed(3, 45)

def stop():
    print("stop")
    got.mecanum_stop()

# ====== (kept for future reference) Finger-shape helpers ======
def only_index_extended(landmarks, extended_thresh=0.2, curl_thresh=0.3):
    def dist(a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

    index_len = dist(landmarks[5], landmarks[8])
    middle_len = dist(landmarks[9], landmarks[12])
    ring_len   = dist(landmarks[13], landmarks[16])
    pinky_len  = dist(landmarks[17], landmarks[20])

    index_extended = index_len > extended_thresh
    middle_curled  = middle_len < curl_thresh
    ring_curled    = ring_len < curl_thresh
    pinky_curled   = pinky_len < curl_thresh

    return index_extended and middle_curled and ring_curled and pinky_curled

def direction_from_index(landmarks, angle_deadzone_deg=30, min_reach=0.02):
    tip = landmarks[8]
    mcp = landmarks[5]
    dx = tip.x - mcp.x
    dy = tip.y - mcp.y
    vx, vy = dx, (mcp.y - tip.y)
    reach = math.hypot(vx, vy)
    if reach < min_reach:
        return None
    angle = math.degrees(math.atan2(vy, vx))
    if -angle_deadzone_deg <= angle <= angle_deadzone_deg:
        return 'left'
    if 60 <= angle <= 120:
        return 'up'
    if angle >= 150 or angle <= -150:
        return 'right'
    if -120 <= angle <= -60:
        return 'down'
    return None

# ====== New: Flick recognition ======
FLICK_WINDOW_MS = 180
MIN_TRAVEL      = 0.12
MIN_SPEED       = 1.4
COOLDOWN_MS     = 350
MOVE_HOLD_MS    = 500

# Motion buffers & timers
tip_track = deque(maxlen=64)  # (t, x, y) for landmark 8 (index tip)
last_flick_time = 0.0
move_until_time = 0.0
last_flick_dir = None  # for HUD

def detect_flick(track_deque, now_s):
    if len(track_deque) < 3:
        return None
    window_s = FLICK_WINDOW_MS / 1000.0
    newest_t, newest_x, newest_y = track_deque[-1]
    oldest_idx = None
    for i in range(len(track_deque) - 1, -1, -1):
        t, _, _ = track_deque[i]
        if newest_t - t <= window_s:
            oldest_idx = i
        else:
            break
    if oldest_idx is None or oldest_idx == len(track_deque) - 1:
        return None
    oldest_t, oldest_x, oldest_y = track_deque[oldest_idx]
    dt = max(1e-3, newest_t - oldest_t)
    dx = newest_x - oldest_x
    dy = newest_y - oldest_y
    vx, vy = dx / dt, -(dy / dt)   # flip y for math-up
    travel = math.hypot(dx, dy)
    speed  = math.hypot(vx, vy)
    if travel < MIN_TRAVEL or speed < MIN_SPEED:
        return None
    angle = math.degrees(math.atan2(vy, vx))
    if -30 <= angle <= 30:
        return 'right'
    if 60 <= angle <= 120:
        return 'up'
    if angle >= 150 or angle <= -150:
        return 'left'
    if -120 <= angle <= -60:
        return 'down'
    return None

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
        flipped = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)

        action_now = 'stop'
        now_s = time.time()

        if results.multi_hand_landmarks:
            h, w = flipped.shape[:2]
            hand_landmarks = results.multi_hand_landmarks[0]

            # Draw landmarks
            mp_drawing.draw_landmarks(
                flipped,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style()
            )

            # Landmark indices
            if show_labels:
                for idx, lm in enumerate(hand_landmarks.landmark):
                    x = int(lm.x * w)
                    y = int(lm.y * h)

                    cv2.putText(flipped, str(idx), (x + 4, y - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2, cv2.LINE_AA)

                    cv2.putText(flipped, str(idx), (x + 4, y - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # ====== NEW: track index tip for tracer & flick ======
            tip_lm = hand_landmarks.landmark[8]
            tip_track.append((now_s, tip_lm.x, tip_lm.y))

            # ====== NEW: draw tracer from tracked positions ======
            if show_tracer and len(tip_track) >= 2:
                # Draw on an overlay so we can fade older segments
                overlay = flipped.copy()

                # How many past points to visualize (caps at deque len)
                max_segments = min(32, len(tip_track) - 1)

                # Use the last N segments, oldest -> newest
                start_idx = len(tip_track) - 1 - max_segments
                pts = [(int(tip_track[i][1] * w), int(tip_track[i][2] * h))
                       for i in range(start_idx, len(tip_track))]

                # Draw fading lines: older = thinner & more transparent
                for i in range(len(pts) - 1):
                    age = i / (len(pts) - 1 + 1e-6)   # 0 (old) .. 1 (new)
                    thickness = max(1, int(8 * (0.25 + 0.75 * (1 - age))))  # 2..8
                    alpha = 0.15 + 0.65 * (1 - age)  # 0.8 (new) .. 0.15 (old)
                    c = (255, 255, 255)  # white; change if you prefer

                    cv2.line(overlay, pts[i], pts[i + 1], c, thickness, cv2.LINE_AA)
                    # Blend this segment onto the frame with per-segment alpha
                    flipped = cv2.addWeighted(overlay, alpha, flipped, 1 - alpha, 0)

            # ====== FLICK DETECTION ======
            if (now_s - last_flick_time) * 1000.0 > COOLDOWN_MS:
                flick_dir = detect_flick(tip_track, now_s)
                if flick_dir is not None:
                    last_flick_time = now_s
                    last_flick_dir = flick_dir
                    if flick_dir == 'up':
                        action_now = 'forward';  move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'down':
                        action_now = 'backward'; move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'left':
                        action_now = 'left';     move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'right':
                        action_now = 'right';    move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)

            # ====== [COMMENTED OUT]: Old POINTING gesture block ======
            # --- BEGIN COMMENTED POINTING BLOCK ---
            # if only_index_extended(hand_landmarks.landmark):
            #     dir_ = direction_from_index(hand_landmarks.landmark)
            #     if dir_ == 'up':
            #         action_now = 'forward'
            #     elif dir_ == 'down':
            #         action_now = 'backward'
            #     elif dir_ == 'left':
            #         action_now = 'left'
            #     elif dir_ == 'right':
            #         action_now = 'right'
            # --- END COMMENTED POINTING BLOCK ---

        # Maintain flick motion hold
        if move_until_time > 0 and now_s < move_until_time:
            action_now = last_action if last_action in ('forward', 'backward', 'left', 'right') else action_now
        elif move_until_time > 0 and now_s >= move_until_time:
            move_until_time = 0
            action_now = 'stop'

        # Debounce commands
        if action_now != last_action:
            if action_now == 'forward':
                forward()
            elif action_now == 'backward':
                backward()
            elif action_now == 'left':
                turn_left()
            elif action_now == 'right':
                turn_right()
            else:
                stop()
            last_action = action_now

        # HUD
        hud_map = {
            'forward':  'FLICK: UP',
            'backward': 'FLICK: DOWN',
            'left':     'FLICK: LEFT',
            'right':    'FLICK: RIGHT',
            'stop':     '—'
        }
        hud = hud_map[action_now]
        if last_flick_dir:
            hud += f"   (last: {last_flick_dir})"
        # Show tracer state
        hud += f"   [Tracer: {'ON' if show_tracer else 'OFF'}]"

        cv2.putText(flipped, f"Gesture: {hud}   (L: labels, T: tracer, Q/ESC: quit)",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(flipped, f"Gesture: {hud}   (L: labels, T: tracer, Q/ESC: quit)",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("MediaPipe Hands (flick gesture)", flipped)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break
        elif key == ord('l'):
            show_labels = not show_labels
        elif key == ord('t'):  # <-- [ADDED] toggle tracer
            show_tracer = not show_tracer

cv2.destroyAllWindows()
