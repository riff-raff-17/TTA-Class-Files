from ugot import ugot
import cv2
import numpy
import pygame

got = ugot.UGOT()
got.initialize("192.168.1.1")
got.open_camera()

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

        cv2.imshow("Webcam Feed", data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    got.mecanum_move_speed(direction=0, speed=30)
                elif event.key == pygame.K_a: # STRAFE left
                    got.mecanum_translate_speed(angle=-90, speed=30)
                elif event.key == pygame.K_d: # STRAFE right
                    got.mecanum_translate_speed(angle=90, speed=30)
                elif event.key == pygame.K_q: # TURN left
                    got.mecanum_turn_speed(turn=2, speed=30)
                elif event.key == pygame.K_e: # TURN right
                    got.mecanum_turn_speed(turn=3, speed=30)
            
            elif event.type == pygame.KEYUP:
                got.mecanum_stop()

        # Press "q" to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

    # Robot stop
    got.mecanum_stop()
    # Computer stop
    pygame.quit()

if __name__ == "__main__":
    main()