import pygame

def main():
    pygame.init()
    pygame.display.set_mode((200, 100))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    forward()
                elif event.key == pygame.K_x:
                    stop()
                elif event.key == pygame.K_1:
                    do_pickup()

            elif event.type == pygame.KEYUP:
                # Optional: stop when key released
                if event.key == pygame.K_f:
                    stop()

    stop()
    pygame.quit()

if __name__ == "__main__":
    main()