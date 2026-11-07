import os
import time

import cv2

CAMERA = 0 # the first webcam; try 1 if you have more than one
WINDOW = "Webcam!"
SNAPSHOT = "output/snapshot.png"

GREEN = (80, 200, 80)
FONT = cv2.FONT_HERSHEY_SIMPLEX

camera = cv2.VideoCapture(CAMERA)
if not camera.isOpened():
    raise SystemExit("Can't open the webcam.")

width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

mirror = True
fps = 0.0
last_time = time.perf_counter()

try:
    while True:
        # read() returns (ok, frame); ok is False when there's no frame
        ok, frame = camera.read()
        if not ok:
            print("No frame from the webcam")
            break

        # Flip left-right so it moves like a mirror
        if mirror:
            frame = cv2.flip(frame, 1)

        # Frames per second, smoothed so the number doesn't jitter
        now = time.perf_counter()
        fps = 0.9 * fps + 0.1 * (1 / (now - last_time))
        last_time = now

        # Draw on the frame like on any image
        text = f"{fps:.0f} fps  mirror {'on' if mirror else 'off'}"
        cv2.putText(frame, text, (10, 30), FONT, 2, GREEN, 2, cv2.LINE_AA)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27): # 27 is Esc
            break
        if key == ord("m"):
            mirror = not mirror
        if key == ord("s"):
            os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
            print("saved:", cv2.imwrite(SNAPSHOT, frame))
        if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
            break
finally:
    camera.release()
    cv2.destroyAllWindows()