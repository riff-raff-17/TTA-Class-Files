import cv2
import numpy as np
from ugot import ugot

ROBOT_IP = "192.168.1.53"

THRESHOLD = 180
STRIP_HEIGHT_FRAC = 0.15  # bottom 15% of the frame


def connect_robot(ip=ROBOT_IP):
    got = ugot.UGOT()
    got.initialize(ip)
    got.open_camera()
    got.transform_adaption_control(False)
    return got


def find_centroid_in_strip(mask_strip, min_area=80):
    """Find centroid of largest white blob in a single strip mask."""
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
    """
    Slices the bottom scan_height_frac of the frame into num_strips horizontal
    bands, and restricts the search to the center scan_width_frac of the
    frame's width (1.0 = full width, 0.5 = center half, etc).
    Returns a list of (cx, cy_in_frame, weight) for strips where the
    line was found, ordered closest-to-robot first, plus a debug overlay,
    plus a (scan_left, scan_right, strip_top, strip_bottom) tuple describing
    the bottom strip's region in full-frame coordinates (handy for other
    detectors, e.g. a red-dot stop signal, that should look in the same
    spot).
    """
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

    results = []  # closest strip (bottom) first
    bottom_strip_bounds = None
    for i in range(num_strips):
        strip_bottom = height - i * strip_h
        strip_top = height - (i + 1) * strip_h
        strip_top = max(strip_top, scan_top)

    centroid = find_centroid_in_strip(strip_mask)
    if centroid is None:
        return None, mask, overlay

    cx, cy_local = centroid
    cy_global = strip_top + cy_local
    cv2.circle(overlay, (cx, cy_global), 6, (0, 0, 255), -1)

    return (cx, cy_global), mask, overlay


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
