from ugot import ugot
import cv2
import numpy as np
import pygame

got = ugot.UGOT()
got.initialize("192.168.1.1")
got.open_camera()


def main():
    pygame.init()
    pygame.display.set_mode((200, 100))

    running = True

    # State variables
    gripper_state = True
    joint_1 = 0  # -90 to 90
    joints_2_3 = 0  # -45 to 45

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
                elif event.key == pygame.K_a:  # STRAFE left
                    got.mecanum_translate_speed(angle=-90, speed=30)
                elif event.key == pygame.K_d:  # STRAFE right
                    got.mecanum_translate_speed(angle=90, speed=30)
                elif event.key == pygame.K_q:  # TURN left
                    got.mecanum_turn_speed(turn=2, speed=30)
                elif event.key == pygame.K_e:  # TURN right
                    got.mecanum_turn_speed(turn=3, speed=30)
                elif event.key == pygame.K_SPACE:
                    if gripper_state:
                        got.mechanical_clamp_release()
                        gripper_state = not gripper_state
                    else:
                        got.mechanical_clamp_close()
                        gripper_state = not gripper_state
                elif event.key == pygame.K_UP:
                    if joints_2_3 <= 45:
                        joints_2_3 += 1
                        got.mechanical_joint_control(
                            angle1=joint_1,
                            angle2=joints_2_3,
                            angle3=joints_2_3,
                            duration=500,
                        )
                elif event.key == pygame.K_DOWN:
                    if joints_2_3 >= -45:
                        joints_2_3 -= 1
                        got.mechanical_joint_control(
                            angle1=joint_1,
                            angle2=joints_2_3,
                            angle3=joints_2_3,
                            duration=500,
                        )
                elif event.key == pygame.K_LEFT:
                    if joint_1 < 90:
                        joint_1 += 5
                        got.mechanical_joint_control(
                            angle1=joint_1,
                            angle2=joints_2_3,
                            angle3=joints_2_3,
                            duration=500,
                        )
                elif event.key == pygame.K_RIGHT:
                    if joint_1 > -90:
                        joint_1 -= 5
                        got.mechanical_joint_control(
                            angle1=joint_1,
                            angle2=joints_2_3,
                            angle3=joints_2_3,
                            duration=500,
                        )
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
