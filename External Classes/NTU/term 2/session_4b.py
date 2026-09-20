import pygame

# SETTINGS
# Constants go at the top in CAPITALS so they are easy to find later

WINDOW_W, WINDOW_H = 900, 520  # window size in pixels
FPS = 60  # how many times per second we redraw

BG = (24, 26, 32)  # a color is (red, green, blue), 0-255


def main():
    pygame.init()  # start Pygame
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))  # make the window
    pygame.display.set_caption("Robot Control Panel")  # title bar text
    clock = pygame.time.Clock()  # used to limit the speed

    print("Window open. Press Esc or click the X to quit.")

    running = True
    while running:
        # Wait just long enough that the loop runs FPS times a second.
        # Without this, the program would spin as fast as possible
        # and make your laptop fan very unhappy.
        clock.tick(FPS)

        # --- 1. handle events ---
        # Pygame collects everything the user did since last time into
        # a list of events. We look at each one in turn.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # the X button
                running = False
            elif event.type == pygame.KEYDOWN:  # a key was pressed
                if event.key == pygame.K_ESCAPE:
                    running = False
