"""
=============================================================
PART 1 — MediaPipe Hello World
=============================================================
Goal: confirm MediaPipe is working and understand the
21-landmark hand model with live visualisation.

Depends on: hand_common.py (must be in the same folder)

Run:
    python part1_mediapipe_hello.py

Controls:
    Q  — quit
    L  — toggle landmark index labels
    D  — toggle coordinate data panel
=============================================================
"""

import cv2
import mediapipe as mp
from hand_common import (
    make_detector,
    draw_hand,
    draw_landmark_indices,
    draw_data_panel,
    FPSCounter,
)

# Setup
detector = make_detector(num_hands=2)
fps_counter = FPSCounter()

# Main loop 
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Webcam Feed", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()