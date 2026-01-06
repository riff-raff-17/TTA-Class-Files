'''Face detection using mediapipe'''

import cv2 
import mediapipe as mp

# Initialize MediaPipe face detection
mp_draw = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)

# Initialize the face detection model
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert frame to RBG (Mediapipe uses RGB)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = face_detection.process(rgb_frame)

    if results.detections:
        for detection in results.detections:
            # Draw bounding box
            bboxC = detection.location_data.relative_bounding_box
            h, w, c = frame.shape
            x, y, w_box, h_box = int(bboxC.xmin*w), int(bboxC.ymin*h), \
                                    int(bboxC.width*w), int(bboxC.height*h)
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (188, 0, 255), 2)

            # Draw confidence score
            confidence = int(detection.score[0] * 100)
            cv2.putText(frame, f'{confidence}% chance of Josh', (x, y - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (188, 0, 255), 2)

    # Display frame
    cv2.imshow("Caden tracker", frame)

    # Break loop with q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()