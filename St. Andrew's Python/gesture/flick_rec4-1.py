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
    """
    Detects: index finger extended, others curled.
    """
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
    """
    (OLD) Return 'up'/'down'/'left'/'right' based on index pointing direction.
    """
    tip = landmarks[8]
    mcp = landmarks[5]

    dx = tip.x - mcp.x
    dy = tip.y - mcp.y
    vx, vy = dx, (mcp.y - tip.y)  # invert y for math-up

    reach = math.hypot(vx, vy)
    if reach < min_reach:
        return None

    angle = math.degrees(math.atan2(vy, vx))  # 0=right, 90=up, -90=down, 180/-180=left

    if -angle_deadzone_deg <= angle <= angle_deadzone_deg:
        return 'left'   # NOTE: original code mapped 0=right -> 'left' action (robot-specific)
    if 60 <= angle <= 120:
        return 'up'
    if angle >= 150 or angle <= -150:
        return 'right'
    if -120 <= angle <= -60:
        return 'down'
    return None

# ====== New: Flick recognition ======
# Tuning knobs (normalized coords per second)
FLICK_WINDOW_MS = 180     # lookback window for motion integration
MIN_TRAVEL      = 0.12    # minimum normalized distance tip must travel in window
MIN_SPEED       = 1.4     # minimum speed (= travel / time) in norm-units per second
COOLDOWN_MS     = 350     # ignore new flicks during cooldown after firing
MOVE_HOLD_MS    = 500     # how long to command motion after a flick before auto-stop

# Motion buffers & timers
tip_track = deque(maxlen=64)  # (t, x, y) for landmark 8 (index tip)
last_flick_time = 0.0
move_until_time = 0.0
last_flick_dir = None  # for HUD

def detect_flick(track_deque, now_s):
    """
    Returns 'up'/'down'/'left'/'right' if a flick is detected in the recent window, else None.
    Uses net displacement between oldest and newest sample inside FLICK_WINDOW_MS.
    """
    if len(track_deque) < 3:
        return None

    # Find oldest sample still within window
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

    # In image coords, y increases downward; flip for math-up
    vx, vy = dx / dt, -(dy / dt)   # normalized units per second
    travel = math.hypot(dx, dy)
    speed  = math.hypot(vx, vy)

    if travel < MIN_TRAVEL or speed < MIN_SPEED:
        return None

    angle = math.degrees(math.atan2(vy, vx))  # 0=right, 90=up
    # Direction bins similar to your prior code
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

        # Default action each frame (unless flick active hold is running)
        action_now = 'stop'

        # Time bookkeeping
        now_s = time.time()

        if results.multi_hand_landmarks:
            h, w = flipped.shape[:2]

            # Use the first hand (as before). You can extend to choose based on handedness.
            hand_landmarks = results.multi_hand_landmarks[0]

            # Draw landmarks
            mp_drawing.draw_landmarks(
                flipped,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style()
            )

            # Show landmark indices
            if show_labels:
                for idx, lm in enumerate(hand_landmarks.landmark):
                    x = int(lm.x * w); y = int(lm.y * h)
                    cv2.putText(flipped, str(idx), (x + 4, y - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(flipped, str(idx), (x + 4, y - 4),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # ====== NEW: track index tip for flick detection ======
            tip_lm = hand_landmarks.landmark[8]
            tip_track.append((now_s, tip_lm.x, tip_lm.y))

            # ====== FLICK DETECTION ======
            # Respect cooldown so one flick doesn't fire multiple times while the hand slows
            if (now_s - last_flick_time) * 1000.0 > COOLDOWN_MS:
                flick_dir = detect_flick(tip_track, now_s)
                if flick_dir is not None:
                    last_flick_time = now_s
                    last_flick_dir = flick_dir

                    # Map flick direction to robot actions (tweak to your preference)
                    if flick_dir == 'up':
                        action_now = 'forward'
                        move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'down':
                        action_now = 'backward'
                        move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'left':
                        action_now = 'left'
                        move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)
                    elif flick_dir == 'right':
                        action_now = 'right'
                        move_until_time = now_s + (MOVE_HOLD_MS / 1000.0)

            # ====== [COMMENTED OUT]: Old POINTING gesture block ======
            # (You asked to take out pointing—kept here for easy re-enable)
            #
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

        # If a flick started movement, keep moving until the hold time elapses
        if move_until_time > 0 and now_s < move_until_time:
            # Maintain the last commanded action during the hold
            # (action_now may be 'stop' if no new flick this frame)
            action_now = last_action if last_action in ('forward', 'backward', 'left', 'right') else action_now
        elif move_until_time > 0 and now_s >= move_until_time:
            # Hold elapsed – stop and clear
            move_until_time = 0
            action_now = 'stop'

        # Debounce: only send command when action changes
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
        # Add last flick direction for visibility
        if last_flick_dir:
            hud += f"   (last: {last_flick_dir})"

        cv2.putText(flipped, f"Gesture: {hud}   (L: toggle labels, Q/ESC: quit)",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(flipped, f"Gesture: {hud}   (L: toggle labels, Q/ESC: quit)",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("MediaPipe Hands (flick gesture)", flipped)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break
        elif key == ord('l'):
            show_labels = not show_labels

cv2.destroyAllWindows()
