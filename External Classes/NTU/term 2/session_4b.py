import pygame

# SETTINGS
# Constants go at the top in CAPITALS so they are easy to find later

WINDOW_W, WINDOW_H = 900, 520  # window size in pixels
FPS = 60  # how many times per second we redraw

PANEL_W = 340  # the control panel fills the left of the window

# The whole color scheme lives here
BG = (24, 26, 32)  # a color is (red, green, blue), 0-255
PANEL = (34, 37, 46)
BTN = (52, 57, 70)
BTN_EDGE = (80, 86, 104)
TEXT = (232, 234, 240)
MUTED = (138, 145, 163)
ACCENT = (80, 205, 165)

# DRAWING HELPERS


def draw_text(surface, text, pos, font, color=TEXT, center=False):
    """Draw some text and return nothing."""
    image = font.render(text, True, color)  # turn the string into a picture
    rect = image.get_rect()  # a Rect the same size as it
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)  # "blit" means paste it on


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

        # --- 2. update ----
        # Nothing to update yet. Later this is where the robot commands
        # and sensor readings will live.

        # --- 3. draw ---
        screen.fill(BG)  # paint over everything from last frame
        pygame.display.flip()  # show the result on the actual screen

    print("Closing down.")
    pygame.quit()


# This line means "only run main() if this file was started directly".
if __name__ == "__main__":
    main()
