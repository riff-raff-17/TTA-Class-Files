import cv2
import numpy as np
from ugot import ugot

# --- Connect to the robot and open the camera ---
got = ugot.UGOT()
got.initialize("192.168.1.1")
got.open_camera()

print("Camera opened. Press 'q' to quit.")

# --- HSV color range for a RED object ---
# Hue for red wraps around in HSV, so we need two ranges to capture it fully
RED_LOW1 = np.array([0, 120, 70])
RED_HIGH1 = np.array([10, 255, 255])
RED_LOW2 = np.array([170, 120, 70])
RED_HIGH2 = np.array([180, 255, 255])

MIN_AREA = 2000  # ignore tiny blobs (noise); increase if getting false detections


# --- Color detection function ---
def find_object(frame):
    """
    Convert frame to HSV, build a red mask, find the biggest blob.
    Returns (cx, cy, area, mask).
    cx/cy/area are None if no object is found.
    """
    # Convert from BGR (what OpenCV uses) to HSV (easier to filter by color)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Build a mask for each red range, then combine them
    mask1 = cv2.inRange(hsv, RED_LOW1, RED_HIGH1)
    mask2 = cv2.inRange(hsv, RED_LOW2, RED_HIGH2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Find the outlines of all blobs in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None, None, mask

    # Pick the largest blob
    biggest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(biggest)


while True:
    # Grab a raw frame from the robot's camera
    frame = got.read_camera_data()

    # Check 1: did we actually receive any data?
    if frame is None or len(frame) == 0:
        print("Failed to grab frame")
        break

    # Decode the raw bytes into an image we can work with
    nparr = np.frombuffer(frame, np.uint8)
    data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Check 2: did the decode succeed?
    if data is None:
        print("Failed to decode frame")
        break

    # Display the live camera feed in a window
    cv2.imshow("Camera Feed", data)

    # Wait 1ms for a keypress; quit if the user presses 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Clean up
cv2.destroyAllWindows()
print("Camera closed. Goodbye!")
