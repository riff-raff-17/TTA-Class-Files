import cv2
import pygame
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize("192.168.1.223")
got.open_camera()


def main():
    pygame.init()
    pygame.display.set_mode((200, 200))

    running = True  # Flag to tell if the code is running
    while running:
        # Camera section
        frame = got.read_camera_data()
        if not frame:
            print("Failed to grab frame")
            break

        nparr = np.frombuffer(frame, np.uint8)
        data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        cv2.imshow("Webcam Feed", data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    got.mecanum_move_speed(direction=0, speed=30)

                if event.key == pygame.K_q:
                    text = input("What to say > ")
                    got.play_audio_tts(text, voice_type=0, wait=True)

            elif event.type == pygame.KEYUP:
                got.mecanum_stop()

    # Robot stop
    got.mecanum_stop()

    # Computer stop
    pygame.quit()

    # Webcam stop
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
