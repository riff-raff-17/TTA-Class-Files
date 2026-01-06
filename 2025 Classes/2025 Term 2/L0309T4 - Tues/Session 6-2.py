from ugot import ugot
import cv2
import numpy as np

# Connect to the UGOT
got = ugot.UGOT()
ip_add = input("What is the UGOT IP address? >")
got.initialize(ip_add)
got.open_camera()

while True:
    # Read video frame by frame
    frame = got.read_camera_data()

    if not frame:
        break

    # Convert your data into a numpy array
    nparr = np.frombuffer(frame, np.uint8)
    data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Flip image
    frame = cv2.flip(data, 1)

    # Show video frame and exit on 'q'
    cv2.imshow('Caden tracker', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        cv2.destroyAllWindows()
        break
    if cv2.waitKey(1)  & 0xff == ord('f'):
        face_name = input('What name? >')
        got.face_recognition_add_name(face_name)

    face_data = got.get_face_recognition_total_info()
    names = [face[0] for face in face_data]
    print(f"\rFaces: {', '.join(names)}                         ", end='')