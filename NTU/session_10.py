from ugot import ugot
import numpy as np
import cv2

got = ugot.UGOT()
got.initialize("192.168.1.128")
got.load_models(["apriltag_qrcode"])
got.open_camera()

# ==== Main Loop ====
def main():
    # ==== Variables ====
    frame_count = 0
    tags = []
    SCAN_FRAMES = 1  # Change this to change how often you scan!
    try:
        while True:
            # Grab the latest camera frame as raw bytes
            frame = got.read_camera_data()
            # Decode the bytes into an OpenCV image array
            nparr = np.frombuffer(frame, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Only run tag detection every SCAN_FRAMES frames
            frame_count += 1
            if frame_count % SCAN_FRAMES == 0:
                tags = got.get_apriltag_total_info()

            if tags:
                tag = tags[0][0:6]
                cv2.putText(img, f"tag: {tag}", (20, 70), 0, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(img, "No tag!",  (20, 70), 0, 0.8, (255, 0, 0), 2)

            # Display the frame in a native OpenCV window
            cv2.imshow("UGOT Camera", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        got.mecanum_stop()
        print("Done!")

    finally:
        got.mecanum_stop()
        cv2.destroyAllWindows()

# ==== Entry point ====
if __name__ == "__main__":
    main()
