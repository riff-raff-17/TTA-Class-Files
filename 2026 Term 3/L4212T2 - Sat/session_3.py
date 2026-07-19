import pygame

# 1. Initialising pygame and creating a window

# These two calls are non-negotiable: pygame can't draw
# anything until its subsysterms are started (pygame.init()) and a surface
# to draw on exists (pygame.display.set_mode())
pygame.init()

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame Fundamentals")

# Controlling frame rate with pygame.time.Clock()

# Without calling clock.tick(60) once per loop, the loop would run as fast
# as the CPU allows -- burning resources and making movement speed depend
# on hardware instead of being consistent for everyone.
clock = pygame.time.Clock()
FPS = 60

# Game state -- a game is just variables that get
# updated every frame. Here that's a single shape's position.

circle_x, circle_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
circle_radius = 20
move_speed = 3  # pixels moved per frame



# Colors as RGB tuples -- the same (x, y)-style tuple as before, just
# with three numbers (red, green, blue) instead of two
BACKGROUND_COLOR = (30, 30, 30)
CIRCLE_COLOR = (255, 200, 0)
LINE_COLOR = (80, 80, 200)
RECT_COLOR = (200, 60, 60)

running = True

# The canonical game loop shape: (1) handle events, (2) update state,
# (3) draw the frame. Getting this order right, and not skipping any part,
# is what makes a responsive game.

while running:
    # --- 1. Handle events ---
    # The OS reports user actions (closing the window, pressing a key) as
    # events placed in a queue. We must drain this queue every frame.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # This is the "break on condition", just triggered
            # by a window close event instead of a value check.
            running = False

    # --- 2. Update state ---
    # Basic keyboard input: read the keyboard state each frame and use it
    # to update position.
    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        circle_x += move_speed
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        circle_x -= move_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        circle_y -= move_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        circle_y += move_speed

    # Keep the circle fully on screen using a clamp
    circle_x = max(circle_radius, min(WINDOW_WIDTH - circle_radius, circle_x))
    circle_y = max(circle_radius, min(WINDOW_HEIGHT - circle_radius, circle_y))

    # --- 3. Draw the frame ---
    # screen.fill() must run first to erase the previous frame -- pygame
    # draws to an off-screen buffer, so without this you'd see smearing.
    screen.fill(BACKGROUND_COLOR)

    # Drawing primitives: circle, line, and rect all take a surface, an
    # RGB color tuple, and a position or set of points.
    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_x, circle_y), circle_radius)
    pygame.draw.line(
        screen,
        LINE_COLOR,
        (0, WINDOW_HEIGHT // 2),
        (WINDOW_WIDTH, WINDOW_HEIGHT // 2),
        2,
    )
    pygame.draw.rect(screen, RECT_COLOR, (20, 20, 100, 60))

    # pygame.display.flip() actually shows the new frame -- nothing drawn
    # above is visible on screen until this call happens.
    pygame.display.flip()

    # Cap the loop at FPS frames per second
    clock.tick(FPS)

pygame.quit()