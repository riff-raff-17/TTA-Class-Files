from ugot import ugot
import numpy as np
import cv2

got = ugot.UGOT()
got.initalize("192.168.1.128")
got.load_models(["apriltag_qrcode"])
got.open_camera()

# ==== Variables ====
frame_count = 0
tags = []
SCAN_FRAMES = 1 # Change this to change how often you scan!

# ==== Main Loop ====
def main():
    try:
        while True:
            # Grab the latest camera frame as raw bytes
            frame = got.read_camera_data()
            # Decode the bytes into an OpenCV image array

# ==== Entry point ====
if __name__ == "__main__":
    main()