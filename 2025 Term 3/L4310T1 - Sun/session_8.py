import time
import cv2
import numpy as np
import mediapipe as mp
from ugot import ugot
got = ugot.UGOT()
got.initialize('192.168.1.120')

# Robot motion stubs
def forward():
    print("Going forward")
    got.mecanum_move_speed(0, 30)

def backward():
    print("Going backward")
    got.mecanum_move_speed(1, 30)

def left():
    print("Going left")
    got.mecanum_turn_speed(2, 45)

def right():
    print("Going right")
    got.mecanum_turn_speed(3, 45)

def stop():
    print("Stopping")
    got.mecanum_stop()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

TIP_IDS = [8, 12, 16, 20]
PIP_IDS = [6, 10, 14, 18]

def fingers_up(hand_landmarks, image_w, image_h):
    lm = hand_landmarks.landmark

    # Helper function
    def xy(idx):
        return int(lm[idx].x * image_w), int(lm[idx].y * image_h)
    
    fingers = [False] * 4

    for i in range(4):
        _, tip_y = xy(TIP_IDS[i])
        _, pip_y = xy(PIP_IDS[i])
        fingers[i] = tip_y < pip_y - 5

    return fingers

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)

    if not cap.isOpened():
        print("Could not open camera")
        return
    
    last_action = None
    last_action_time = 0.0
    ACTION_COOLDOWN_SEC = 0.6

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                break

            frame_bgr = cv2.flip(frame_bgr, 1)
            frame_rgb = cv2.cvtColor(frame_bgr,  cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            h, w = frame_bgr.shape[:2]
            command = None

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                ups = fingers_up(hand_landmarks, w, h)
                count = sum(ups)

                # HUD
                cv2.putText(frame_bgr, f"Fingers up: {count}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            (0, 255, 255), 2)
                
                # Map count to actions
                if count == 0:
                    command = "stop"
                elif count == 1:
                    command = "forward"
                elif count == 2:
                    command = "backward"
                elif count == 3:
                    command = "left"
                elif count == 4:
                    command = "right"

            now = time.time()
            if command:
                if command != last_action or (now - last_action_time) > ACTION_COOLDOWN_SEC:
                    if command == "forward":
                        forward()
                    elif command == "backward":
                        backward()
                    elif command == "left":
                        left()
                    elif command == "right":
                        right()
                    elif command == "stop":
                        stop()
                    last_action = command
                    last_action_time = now

                cv2.putText(frame_bgr, f"Command: {command}", (10, 65), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (0, 255, 0), 2)
            
            cv2.imshow("Hands", frame_bgr)
            if cv2.waitKey(1) &0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

main()