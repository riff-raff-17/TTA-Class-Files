from ugot import ugot
import numpy as np
import cv2

got = ugot.UGOT()
got.initialize("192.168.1.189")
got.load_models(["apriltag_qrcode"])
got.open_camera()

frame_count = 0
tags = []
SCAN_FRAMES = 0

def approach_tag(c_x, dist, strafe_spd=10, fwd_spd=10, gap=20, target_dist=0.2):
    if dist > target_dist:
        if c_x < 320 - gap:
            # Tag is to the LEFT of center — strafe left to re-align.
            # mecanum_move_xyz(x, y, z): x=strafe, y=forward, z=rotation
            got.mecanum_move_xyz(-strafe_spd, strafe_spd, 0)
        elif c_x > 320 + gap:
            # Tag is to the RIGHT of center — strafe right to re-align.
            got.mecanum_move_xyz(strafe_spd, strafe_spd, 0)
        else:
            # Tag is centered but still too far — drive straight forward.
            got.mecanum_move_xyz(0, fwd_spd, 0)
    else:
        # Tag is within target distance — stop and exit.
        got.mecanum_stop()
        return False
    
    return True

try:
    while True:
        # Grab the latest camera frame as raw bytes
        frame = got.read_camera_data()
        # Decode the bytes into an OpenCV image array
        nparr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Only run tag detection every 5 frames
        frame_count += 1
        if SCAN_FRAMES != 0:
            if frame_count % SCAN_FRAMES == 0:
                tags = got.get_apriltag_total_info()
        else:
            tags = got.get_apriltag_total_info()

        if tags:
            tag = tags[0]  # Only look at the first detected tag
            # Extract center and dimensions
            cx, cy = int(tag[1]), int(tag[2])
            half_w, half_h = int(tag[4] / 2), int(tag[3] / 2)
            # Compute bounding box corners
            x1, y1 = cx - half_w, cy - half_h
            x2, y2 = cx + half_w, cy + half_h
            # Draw bounding box and center dot
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)
            # Label with tag ID and distance (using 5x5 cm reference)
            label = f"ID: {tag[0]}  dist: {tag[6]:.2f}cm"
            cv2.putText(
                img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

            reached = approach_tag(c_x=cx, dist=tag[6])

        else:
            cv2.putText(
                img, "No tag!", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2
            )
            got.mecanum_stop()

        # Display the frame in a native OpenCV window
        cv2.imshow("Camera", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    print("Done")
finally:
    got.mecanum_stop()
    cv2.destroyAllWindows()
