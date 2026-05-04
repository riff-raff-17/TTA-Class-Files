import cv2
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize("192.168.1.1")
got.open_camera()

# Speed ranges
MOVE_MIN, MOVE_MAX = 5, 80  # units are in cm/s
TURN_MIN, TURN_MAX = 5, 280  # units are in degrees/s


def clamp(val, lo, hi):
    # if > max, set to max. If < min, set to min. Otherwise, leave the same
    return max(lo, min(hi, val))


def main():
    move_speed = 30  # initial movement speed
    turn_speed = 45  # initial turn speed

    while True:
        frame = got.read_camera_data()
        if frame is None:
            print("Failed to grab frame")
            break

        # Decode JPEG bytes to image
        nparr = np.frombuffer(frame, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if data is None:
            print("Failed to decode frame")
            break

        # Overlay current speeds
        info = f"Move speed: {move_speed}   |   Turn speed: {turn_speed}"
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

        cv2.imshow("Webcam Feed", data)

        # One waitKey per loop; capture special keys (arrows) too
        key = cv2.waitKey(1) & 0xFF

        # --- movement with WASD using current speeds ---
        # 0=forwards, 1=backwards, 2=left, 3=right
        if key == ord("w"):
            got.mecanum_move_speed(0, move_speed)  # forward
        elif key == ord("s"):
            got.mecanum_move_speed(1, move_speed)  # backwards
        elif key == ord("a"):
            got.mecanum_turn_speed(2, turn_speed) # left
        elif key == ord("d"):
            got.mecanum_turn_speed(3, turn_speed) # right
        elif key == ord(" "):
            got.mecanum_stop()
        elif key == ord("q"): # q to quit
            break

        # --- arrow keys to adjust speeds ---
        # In OpenCV, arrow keys typically map to:
        # up=0, down=1, left=2, right=3 (after & 0xFF)
        if key == 0: # Up arrow -> increase movement speed
            move_speed = clamp(move_speed + 5, MOVE_MIN, MOVE_MAX)
        elif key == 1: # Down arrow -> decrease movement speed
            move_speed = clamp(move_speed - 5, MOVE_MIN, MOVE_MAX)
        elif key == 2: # Left arrow -> decrease turn speed
            turn_speed = clamp(turn_speed - 5, TURN_MIN, TURN_MAX)
        elif key == 3: # Right arrow -> increase turn speed
            turn_speed = clamp(turn_speed + 5, TURN_MIN, TURN_MAX)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()