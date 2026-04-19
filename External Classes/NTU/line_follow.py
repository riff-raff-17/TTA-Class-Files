import cv2
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize("192.168.1.128")
got.load_models(["line_recognition"])
got.set_track_recognition_line(0)
got.open_camera()


LINE_TYPE_LABELS = {
    0: "No line",
    1: "Straight",
    2: "Y-intersection",
    3: "Crossroads",
}


def line_follow(offset, mult=0.25, speed=35):
    """Follow the detected line by turning proportionally to the line offset."""
    # Read line-tracking information from the robot.
    # `offset` tells how far the detected line is from the center.
    # `type` describes the line/intersection pattern detected.
    # (0: no line, 1: straight line, 2: y-intersection, 3: crossroads)
    # `x` and `y` are the detected line position coordinates (only for crossroads)

    # Convert the line offset into a turning speed.
    # Larger offset -> stronger rotation to re-center on the line.
    rotation_speed = int(offset * mult)

    # Move forward while rotating to stay aligned with the line.
    got.mecanum_move_xyz(x_speed=0, y_speed=speed, z_speed=rotation_speed)


def draw_overlay(frame, offset, line_type, x, y):
    """Draw line type and offset text in the top-left corner of the frame,
    and a dot at (x, y) when a crossroads is detected."""
    label = LINE_TYPE_LABELS.get(line_type, f"Unknown ({line_type})")
    lines = [
        f"Line type: {label}",
        f"Offset:    {offset:.2f}",
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2 
    color = (0, 255, 0)  # Green text
    shadow_color = (0, 0, 0)  # Black shadow for readability

    for i, text in enumerate(lines):
        tx, ty = 10, 25 + i * 30
        # Draw shadow first, then colored text on top
        cv2.putText(
            frame, text, (tx + 1, ty + 1), font, font_scale, shadow_color, thickness
        )
        cv2.putText(frame, text, (tx, ty), font, font_scale, color, thickness)

    # Draw a dot at the detected crossroads position (line_type == 3)
    if line_type == 3:
        cv2.circle(
            frame, (int(x), int(y)), radius=8, color=(0, 0, 255), thickness=-1
        )  # Red filled dot
        cv2.circle(
            frame, (int(x), int(y)), radius=8, color=(0, 0, 0), thickness=2
        )  # Black outline


def main():
    try:
        while True:
            frame = got.read_camera_data()
            if frame is None:
                print("Failed to grab frame")
                break

            nparr = np.frombuffer(frame, np.uint8)
            data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            offset, line_type, x, y = got.get_single_track_total_info()
            draw_overlay(data, offset, line_type, x, y)

            cv2.imshow("Webcam Feed", data)

            # Press "q" to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        got.mecanum_stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
