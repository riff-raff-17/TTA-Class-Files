# --- Imports ---
import cv2
import numpy as np
from ugot import ugot

# --- List of filters in order ---
# Each entry is a display name and a function that takes a frame and alters it
def apply_normal(frame):
    return frame

def apply_grayscale(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) 

# --- Constants ---
FILTERS = [
    ("Normal", apply_normal),
    ("Grayscale", apply_grayscale),
]

# --- Main Loop ---
def main():
    current = 0 # index into FILTERS

    got = ugot.UGOT()
    got.initialize("192.168.1.1") 
    got.open_camera()

    while True:
        frame = got.read_camera_data() # Read one frame of the UGOT camera
        if not frame:
            print("Failed to grab frame")
            break # stop our code

        nparr = np.frombuffer(frame, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Apply the current filter
        name, fn = FILTERS[current]
        output = fn(data)

        # HUD - show current filter and controls
        cv2.putText(output, f"Filter: {name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 255), 2,)
        cv2.putText(output, "n = next | p = prev | q = quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (200, 200, 200), 1,)

        cv2.imshow("Filter Switcher", output)

        # Press 'q' to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("n"): # next filter
            current = (current + 1) % len(FILTERS)
        elif key == ord("p"): # previous filter
            current = (current - 1) % len(FILTERS)

    cv2.destroyAllWindows()

# --- Entry Point ---
if __name__ == "__main__":
    main()