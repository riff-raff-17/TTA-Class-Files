"""
Data capture for the cube classifier.

Captures images from the UGOT robot's camera (not your laptop webcam --
training and inference must use the same camera/lens/color response, or
accuracy will quietly suffer on the actual field).

Controls:
  'r' -> save current ROI as RIPE      (small cube, 25mm)
  'u' -> save current ROI as UNRIPE    (large cube, 50mm)
  'b' -> save current ROI as BACKGROUND (empty track / no cube)
  'q' -> quit early

While capturing, deliberately rotate through:
  - every cube color in each size class (ripe: purple/red/orange,
    unripe: blue/white/green/pink) -- otherwise the model may learn
    "this specific color" instead of "this size", and will misfire on
    any color it hasn't seen.
  - multiple distances around your expected classification trigger point
  - multiple rotations/orientations (cube placement is randomized on the
    field)
  - a few different lighting conditions if you can manage it
"""

import os

import cv2
import numpy as np
from ugot import ugot

from roi_utils import crop_roi, get_roi_box

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
UGOT_IP = "192.168.1.54"  # match your robot's IP

DATASET_DIR = "dataset"
CLASSES = ["ripe", "unripe", "background"]
KEY_TO_CLASS = {"r": "ripe", "u": "unripe", "b": "background"}

TARGET_PER_CLASS = 150

RIPE_COLOR_HINTS = ["purple", "red", "orange"]
UNRIPE_COLOR_HINTS = ["blue", "white", "green", "pink"]

BAR_WIDTH = 220
BAR_HEIGHT = 18
BAR_X = 10
BAR_Y_START = 60
BAR_Y_STEP = 30
BAR_COLORS = {"ripe": (0, 200, 0), "unripe": (0, 0, 220), "background": (180, 180, 180)}


def draw_progress(frame, counts):
    for i, c in enumerate(CLASSES):
        y = BAR_Y_START + i * BAR_Y_STEP
        progress = min(int((counts[c] / TARGET_PER_CLASS) * BAR_WIDTH), BAR_WIDTH)
        cv2.rectangle(frame, (BAR_X, y), (BAR_X + BAR_WIDTH, y + BAR_HEIGHT), (50, 50, 50), -1)
        cv2.rectangle(frame, (BAR_X, y), (BAR_X + progress, y + BAR_HEIGHT), BAR_COLORS[c], -1)
        cv2.putText(
            frame, f"{c}: {counts[c]}/{TARGET_PER_CLASS}",
            (BAR_X + BAR_WIDTH + 10, y + BAR_HEIGHT - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
        )


def main():
    for c in CLASSES:
        os.makedirs(os.path.join(DATASET_DIR, c), exist_ok=True)

    counts = {c: len(os.listdir(os.path.join(DATASET_DIR, c))) for c in CLASSES}

    got = ugot.UGOT()
    got.initialize(UGOT_IP)
    got.open_camera()

    print("Controls: 'r'=RIPE(small)  'u'=UNRIPE(large)  'b'=BACKGROUND  'q'=quit")
    print(f"Ripe colors to rotate through:   {RIPE_COLOR_HINTS}")
    print(f"Unripe colors to rotate through: {UNRIPE_COLOR_HINTS}")

    while any(counts[c] < TARGET_PER_CLASS for c in CLASSES):
        raw = got.read_camera_data()
        if not raw:
            print("Failed to grab frame")
            continue

        nparr = np.frombuffer(raw, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            continue

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = get_roi_box(w, h)

        display = frame.copy()
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(
            display, "Place cube in yellow box, then press r/u/b",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
        )
        draw_progress(display, counts)

        cv2.imshow("Cube Data Capture", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        pressed_char = chr(key) if 32 <= key < 127 else ""
        pressed_class = KEY_TO_CLASS.get(pressed_char)

        if pressed_class and counts[pressed_class] < TARGET_PER_CLASS:
            roi = crop_roi(frame)
            idx = counts[pressed_class]
            path = os.path.join(DATASET_DIR, pressed_class, f"{pressed_class}_{idx:04d}.jpg")
            cv2.imwrite(path, roi)
            print(f"Saved {pressed_class}: {path}")
            counts[pressed_class] += 1

    cv2.destroyAllWindows()
    print("Done. Final counts:", counts)


if __name__ == "__main__":
    main()
