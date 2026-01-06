import cv2
import numpy
from ugot import ugot
import mediapipe as mp

got = ugot.UGOT()
got.initialize('192.168.1.29')
got.open_camera()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

def main():
    with mp_hands.Hands(
        static_image_mode = False,
        max_num_hands = 2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        while True:
            frame = got.read_camera_data()
            if not frame:
                print("Failed to get camera data")
                break

            nparr = numpy.frombuffer(frame, numpy.uint8)
            data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            color_frame = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

            results = hands.process(color_frame)

            # Draw hand landmarks
            if results.multi_hand_landmarks:
                h, w = data.shape[:2]
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        data,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style()
                    )

                    for idx, lm in enumerate(hand_landmarks.landmark):
                        x = int(lm.x * w)
                        y = int(lm.y * h)

                        cv2.putText(data, str(idx), (x+4, y-4), cv2.FONT_HERSHEY_COMPLEX,
                                    0.45, (0, 0, 0), 2)

            cv2.imshow("UGOT CAMERA", data)

            # Press q to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()