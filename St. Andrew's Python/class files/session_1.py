import cv2
import numpy as np
from ugot import ugot
got = ugot.UGOT()
got.initialize('192.168.88.1')
got.open_camera()

def main():
  while True:
    frame = got.read_camera_data()
    if not frame:
      print("Failed to grab frame")
      break
    
    nparr = np.frombuffer(frame, np.uint8)
    data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Drawing
    # Location arguments: top left, bottom right
    cv2.rectangle(data, (50, 50), (200, 200), (0, 0, 255), 2)

    # Text
    # Location arguments: bottom left
    # Color (B, G, R)
    text = "Hello OpenCV"
    cv2.putText(data, text, (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Webcam feed", data)

    # press q to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
      print('Exiting...')
      got.mecanum_stop()
      break
    elif key == ord('w'):
      got.mecanum_move_speed(direction=0, speed=40)
    elif key == ord('s'):
      got.mecanum_move_speed(direction=1, speed=40)
    elif key == ord('a'):
      got.mecanum_turn_speed(turn=2, speed=45)
    elif key == ord('d'):
     got.mecanum_turn_speed(turn=3, speed=45)
    elif key == ord(' '):
      got.mecanum_stop()

  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()