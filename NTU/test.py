from ugot import ugot
import cv2
import numpy as np
got = ugot.UGOT()
got.initialize("192.168.1.129")

import pygame

# forward(), stop(), do_pickup(), etc.

def main():
    pygame.init()
    pygame.display.set_mode((200, 100))

    running = True
    while running:

        frame = got.read_camera_data()
        if not frame:
            print("Failed to grab frame")
            break

        nparr = np.frombuffer(frame, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    got.mecanum_move_speed(direction=0, speed=30)
                elif event.key == pygame.K_s:
                    got.mecanum_move_speed(direction=1, speed=30)

            elif event.type == pygame.KEYUP:
                # Optional: stop when key released
                    got.mecanum_stop()

        
        cv2.imshow("Webcam Feed", data)

        # Press "q" to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    got.mecanum_stop()
    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()