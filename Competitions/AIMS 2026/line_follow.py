from dataclasses import dataclass

import cv2
import numpy as np
from ugot import ugot

ROBOT_IP = "192.168.1.54"

DIR_LEFT = 2
DIR_RIGHT = 3


@dataclass
class Config:
    # Speed
    max_speed: float = 25  # speed on straights (steering near 0)
    min_speed: float = 7  # speed floor on sharp turns
    steering_at_min_speed: float = 25  # |steering| at which speed bottoms out

    # PD steering
    kp: float = 0.5
    kd: float = 0.2

    # Smoothing / anti-jerk
    error_deadband: float = 10  # px; errors smaller than this are treated as 0
    smoothing_alpha: float = 0.3  # EMA weight for new readings (0-1, lower = smoother)
    max_steering_delta: float = 15  # max change in steering allowed per frame
    max_speed_delta: float = 4  # max change in speed allowed per frame
    max_steering: float = 70  # hard ceiling on |steering| sent to hardware

    # Lost-line handling
    lost_line_threshold: int = 5  # frames with no line before triggering search


def connect_robot(ip=ROBOT_IP):
    got = ugot.UGOT()
    got.initialize(ip)
    got.open_camera()
    got.transform_adaption_control(False)
    return got


def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def find_centroid_in_strip(mask_strip, min_area=80):
    contours, _ = cv2.findContours(
        mask_strip, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < min_area:
        return None

    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)


def get_line_position_multistrip(
    frame, blurred, threshold=180, num_strips=3, scan_height_frac=0.4, scan_width_frac=0.75
):
    height, width = frame.shape[:2]

    _, mask = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)

    scan_w = int(width * scan_width_frac)
    scan_left = (width - scan_w) // 2
    scan_right = scan_left + scan_w

    width_mask = np.zeros_like(mask)
    width_mask[:, scan_left:scan_right] = mask[:, scan_left:scan_right]
    mask = width_mask

    scan_top = int(height * (1 - scan_height_frac))
    scan_zone_height = height - scan_top
    strip_h = scan_zone_height // num_strips

    overlay = frame.copy()
    cv2.line(overlay, (width // 2, 0), (width // 2, height), (0, 255, 255), 1)
    cv2.line(overlay, (scan_left, 0), (scan_left, height), (255, 0, 255), 1)
    cv2.line(overlay, (scan_right, 0), (scan_right, height), (255, 0, 255), 1)

    results = []
    for i in range(num_strips):
        strip_bottom = height - i * strip_h
        strip_top = height - (i + 1) * strip_h
        strip_top = max(strip_top, scan_top)

        strip_mask = mask[strip_top:strip_bottom, :]
        centroid = find_centroid_in_strip(strip_mask)

        cv2.rectangle(overlay, (0, strip_top), (width, strip_bottom), (255, 0, 0), 1)

        if centroid is not None:
            cx, cy_local = centroid
            cy_global = strip_top + cy_local
            weight = num_strips - i
            results.append((cx, cy_global, weight))
            cv2.circle(overlay, (cx, cy_global), 6, (0, 0, 255), -1)
            cv2.putText(
                overlay,
                str(i),
                (cx + 10, cy_global),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

    return results, mask, overlay


def compute_steering_error(results, frame_width):
    """
    Combines multi-strip centroids into a single weighted steering error
    and an estimate of curvature (difference between near and far strips).
    """
    if not results:
        return None, None

    center_x = frame_width // 2
    total_weight = sum(w for _, _, w in results)
    weighted_error = sum((cx - center_x) * w for cx, _, w in results) / total_weight

    near_cx = results[0][0]
    far_cx = results[-1][0]
    curvature = far_cx - near_cx  # positive = line curving right ahead

    return weighted_error, curvature


def pd_steering(error, curvature, kp, kd):
    return kp * error + kd * curvature


def speed_for_steering(steering, max_speed, min_speed, steering_at_min_speed):
    """Scales speed down as steering magnitude increases."""
    turn_fraction = min(abs(steering) / steering_at_min_speed, 1.0)
    return max_speed - turn_fraction * (max_speed - min_speed)


def turn(got, steering, forward_speed):
    """
    Steer left/right while moving.
    steering < 0 -> turn left, steering > 0 -> turn right.
    """
    if steering < 0:
        got.transform_move_turn(0, int(forward_speed), DIR_LEFT, int(-steering))
    else:
        got.transform_move_turn(0, int(forward_speed), DIR_RIGHT, int(steering))

    print(f"[turn] steering={steering:.1f}, forward_speed={forward_speed}")


def stop(got):
    got.transform_stop()
    print("[stop]")


def search_for_line():
    print("[search_for_line] line lost, searching...")


def main():
    cfg = Config()
    got = connect_robot()

    smoothed_steering = 0.0
    smoothed_speed = float(cfg.max_speed)
    lost_line_count = 0

    try:
        while True:
            frame = got.read_camera_data()
            if not frame:
                print("Failed to grab frame")
                break

            nparr = np.frombuffer(frame, np.uint8)
            data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if data is None:
                print("Failed to decode frame")
                continue

            blurred = preprocess_frame(data)
            results, mask, overlay = get_line_position_multistrip(data, blurred)
            error, curvature = compute_steering_error(results, data.shape[1])

            if error is not None:
                lost_line_count = 0

                # Ignore small errors so the robot doesn't hunt/wobble around center
                if abs(error) < cfg.error_deadband:
                    error = 0.0

                raw_steering = pd_steering(error, curvature, kp=cfg.kp, kd=cfg.kd)
                raw_speed = speed_for_steering(
                    raw_steering, cfg.max_speed, cfg.min_speed, cfg.steering_at_min_speed
                )

                # Low-pass filter (EMA) to smooth out frame-to-frame vision noise
                target_steering = (
                    cfg.smoothing_alpha * raw_steering
                    + (1 - cfg.smoothing_alpha) * smoothed_steering
                )
                target_speed = (
                    cfg.smoothing_alpha * raw_speed + (1 - cfg.smoothing_alpha) * smoothed_speed
                )

                # Rate-limit how much steering/speed can change in a single frame
                steering_delta = max(
                    -cfg.max_steering_delta,
                    min(cfg.max_steering_delta, target_steering - smoothed_steering),
                )
                speed_delta = max(
                    -cfg.max_speed_delta,
                    min(cfg.max_speed_delta, target_speed - smoothed_speed),
                )
                smoothed_steering += steering_delta
                smoothed_speed += speed_delta

                smoothed_steering = max(
                    -cfg.max_steering, min(cfg.max_steering, smoothed_steering)
                )

                print(
                    f"error={error:.1f}, curvature={curvature:.1f}, "
                    f"raw_steering={raw_steering:.1f}, steering={smoothed_steering:.1f}, "
                    f"speed={smoothed_speed:.1f}"
                )
                turn(got, smoothed_steering, smoothed_speed)
            else:
                lost_line_count += 1
                print(f"Line not found in any strip ({lost_line_count} frames)")

                if lost_line_count >= cfg.lost_line_threshold:
                    stop(got)
                    search_for_line()
                    smoothed_steering = 0.0
                    smoothed_speed = float(cfg.max_speed)

            cv2.imshow("Webcam Feed", overlay)
            cv2.imshow("Mask", mask)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                stop(got)
                break
    except KeyboardInterrupt:
        stop(got)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
