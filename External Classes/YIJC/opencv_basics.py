# Imports
import cv2
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize("192.168.88.1")
got.open_camera()

# Speed ranges
MOVE_MIN, MOVE_MAX = 5, 80
TURN_MIN, TURN_MAX = 5, 280


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


# Main Loop
def main():
    move_speed = 30  # initial movement speed
    turn_speed = 45  # initial turn speed

    while True:
        frame = got.read_camera_data()
        if not frame:
            print("Failed to grab frame")
            break

        nparr = np.frombuffer(frame, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Overlay current speeds
        info = f"Move speed: {move_speed}  |  Turn speed: {turn_speed}"
        cv2.putText(
            data,
            info,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("Robot Feed", data)

        # Press 'q' to quit
        key = cv2.waitKey(1) & 0xFF

        # --- movement with WASD using current speeds ---
        if key == ord("w"):
            got.mecanum_move_speed(0, move_speed)  # forward
        elif key == ord("s"):
            got.mecanum_move_speed(1, move_speed)  # backward
        elif key == ord("a"):
            got.mecanum_turn_speed(2, turn_speed)  # left
        elif key == ord("d"):
            got.mecanum_turn_speed(3, turn_speed)  # right
        elif key == ord(" "):  # space to stop
            got.mecanum_stop()
        elif key == ord("q"):  # q to quit
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
