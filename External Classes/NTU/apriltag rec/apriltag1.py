from ugot import ugot
import numpy as np
import cv2

got = ugot.UGOT()
got.initialize("192.168.1.128")
got.load_models(["apriltag_qrcode"])
got.open_camera()

frame_count = 0
tags = []
SCAN_FRAMES = 1

try:
    while True:
        # Grab the latest camera frame as raw bytes
        frame = got.read_camera_data()
        # Decode the bytes into an OpenCV image array
        nparr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Only run tag detection every 3 frames
        frame_count += 1
        if frame_count % SCAN_FRAMES == 0:
            tags = got.get_apriltag_total_info()

        if tags:
            tag = tags[0][0:6]  # Only look at the first detected tag
            cv2.putText(img, f"tag: {tag}", (20, 70), 0, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(
                img, "No tag!", (20, 70), 0, 0.8, (0, 0, 255), 2
            )
        # Display the frame in a native OpenCV window
        cv2.imshow("Camera", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    print("Done")
finally:
    got.mecanum_stop()
    cv2.destroyAllWindows()
