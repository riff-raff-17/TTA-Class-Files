import cv2
import numpy as np
from ugot import ugot

ROBOT_IP = "192.168.1.53"

# PD steering tuning
KP = 0.5
KD = 0.2

MAX_SPEED = 28
MIN_SPEED = 15
MAX_STEERING_FOR_SLOWDOWN = 15


def connect_robot(ip=ROBOT_IP):
    got = ugot.UGOT()
    got.initialize(ip)
    got.open_camera()
    got.transform_adaption_control(False)
    return got


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
    frame, threshold=180, num_strips=3, scan_height_frac=0.4, scan_width_frac=0.75
):
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
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
    bottom_strip_bounds = None
    for i in range(num_strips):
        strip_bottom = height - i * strip_h
        strip_top = height - (i + 1) * strip_h
        strip_top = max(strip_top, scan_top)

        if i == 0:
            bottom_strip_bounds = (scan_left, scan_right, strip_top, strip_bottom)

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

    return results, mask, overlay, bottom_strip_bounds


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


def speed_for_steering(steering, max_speed, min_speed, max_steering_for_slowdown):
    """Scales speed down as steering magnitude increases."""
    turn_fraction = min(abs(steering) / max_steering_for_slowdown, 1.0)
    return max_speed - turn_fraction * (max_speed - min_speed)


def main():
    got = connect_robot()

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

        centroid, mask, overlay = get_line_position_single_strip(data)

        if centroid is not None:
            print(f"line centroid: {centroid}")
        else:
            print("line not found")

        cv2.imshow("Webcam Feed", overlay)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
