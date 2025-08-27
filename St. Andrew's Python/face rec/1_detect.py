import cv2
import mediapipe as mp
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize('192.168.1.136')
got.open_camera()

mp_fd = mp.solutions.face_detection

def main():
    with mp_fd.FaceDetection(model_selection=0, min_detection_confidence=0.5) as fd:
        while True:
            frame = got.read_camera_data()
            if not frame:
                break
            nparr = np.frombuffer(frame, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = fd.process(frame_rgb)

            if res.detections:
                h, w = frame.shape[:2]
                for det in res.detections:
                    bbox = det.location_data.relative_bounding_box
                    x, y = int(bbox.xmin*w), int(bbox.ymin*h)
                    ww, hh = int(bbox.width*w), int(bbox.height*h)
                    cv2.rectangle(frame, (x,y), (x+ww, y+hh), (0,255,0), 2)

            cv2.imshow("step01_detect", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break  # ESC to quit

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
