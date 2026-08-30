import cv2
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize("192.168.1.1")

# --- Load all AI models ---
got.load_models(["line_recognition"])
got.set_track_recognition_line(0)
got.open_camera()

# --- Constants ---
LINE_TYPE_LABELS = {
    0: "No line",
    1: "Straight",
    2: "Y-intersection",
    3: "Crossroads",
}

# --- Helper functions ---
def line_follow(offset, mult=0.25, speed=35):
    """Follow the detected line by turning proportionally to the line offset."""
    rotation_speed = int(offset * mult)

    # Move forward while rotating to stay aligned with the line
    got.mecanum_move_xyz(x_speed=0, y_speed=speed, z_speed=rotation_speed)

def draw_overlay(frame, offset, line_type, x, y):
    """Draw line type and offset text in the top-left corner of the frame,
    and a dot at (x, y) when a crossroads is detected."""
    label = LINE_TYPE_LABELS.get(line_type, f"Unknown ({line_type})")
    lines = [
        f"Line type: {label}",
        f"Offset:    {offset:.0f}",
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (0, 255, 0) # Green text
    shadow_color = (0, 0, 0) # Black shadow for readability

    for i, text in enumerate(lines):
        tx, ty = 10, 25 + i * 30
        # Draw shadow first, then layered text on top
        cv2.putText( # Background shadow
            frame, text, (tx + 1, ty + 1), font, font_scale, shadow_color, thickness
        )
        cv2.putText( # Real color text
            frame, text, (tx, ty), font, font_scale, color, thickness
        )

    # Draw a dot at the detected crossroads position (line_type == 3)
    if line_type == 3:
        cv2.circle(
            frame (int(x), int(y)), radius=8, color=(0, 0, 255), thickness=-1
        )
        cv2.circle(
            frame, (int(x), int(y)), radius=8, color=(0,0,0), thickness=2
        )

# --- Main loop ---
def main():
    try:
        while True:
            frame = got.read_camera_data() # reads data from UGOT camera
            if frame is None: # Frame will be None if not sent
                print("Failed to grab frame")
                break

            nparr = np.frombuffer(frame, np.uint8)
            data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            offset, line_type, x, y = got.get_single_track_total_info()
            draw_overlay(data, offset, line_type, x, y)
            line_follow(offset=offset, mult=0.25, speed=20)

            cv2.imshow("UGOT Camera", data) # Show UGOT camera window

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    finally:
        got.mecanum_stop()
        cv2.destroyAllWindows()

# --- Entry point ---
if __name__ == "__main__":
    main()