import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cartpole - User Controlled")

clock = pygame.time.Clock()
FPS = 50

# CartPole Parameters
gravity = 9.8
masscart = 1.0
masspole = 0.1
total_mass = masspole + masscart
length = 0.5
polemass_length = masspole * length
force_mag = 5.0

theta_threshold_radians = math.radians(30) # 30˚ in radians
x_threshold = 2.4 # cart position limit

# Convert from physics to screen pixels
def physics_x_to_screen(x_phys):
    return int((x_phys + x_threshold) * (SCREEN_WIDTH / (2 * x_threshold)))

# Fixed y-position for the cart on the screen
cart_y = SCREEN_HEIGHT * 0.75

# Cart dimensions (in pixels)
CART_WIDTH = 80
CART_HEIGHT = 40
POLE_WIDTH = 10

# Fonts
font = pygame.font.SysFont(None, 48)

# Game state variables
x = 0.0         # cart position
x_vel = 0.0     # cart velocity
theta = 0.0     # pole angle
theta_vel = 0.0 # pole angular velocity

game_over = False
elapsed_time = 0.0 # seconds survived

# Waiting for spacebar
in_countdown = False

def reset_environment():
    global x, x_vel, theta, theta_vel
    global game_over, elapsed_time
    global in_countdown

    # small random initial state
    x = random.uniform(-0.05, 0.05)
    x_vel = random.uniform(-0.05, 0.05)
    theta = random.uniform(-0.05, 0.05)
    theta_vel = random.uniform(-0.05, 0.05)

    game_over = False
    elapsed_time = 0.0

    # Wait for space to start the game
    in_countdown = True

# Initial reset
reset_environment()

while True:
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.05)

    # Handle Pygame events (quit)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if in_countdown:
        # Draw background
        screen.fill((255, 255, 255))

        # Draw the track
        pygame.draw.line(
            screen, (0, 0, 0),
            (0, cart_y + CART_HEIGHT // 2),
            (SCREEN_WIDTH, cart_y + CART_HEIGHT // 2), 2
        )

        # Draw the cart
        cart_x_pix = physics_x_to_screen(x) - CART_WIDTH // 2
        cart_rect = pygame.Rect(
            cart_x_pix, cart_y - CART_HEIGHT // 2, CART_WIDTH, CART_HEIGHT
        )
        pygame.draw.rect(screen, (0, 0, 255), cart_rect)
        
        # Draw pole
        pole_len_pix = length * (SCREEN_HEIGHT * 0.5)
        pole_x_end = cart_x_pix + CART_WIDTH // 2 + pole_len_pix * math.sin(theta)
        pole_y_end = cart_y - CART_HEIGHT// 2 - pole_len_pix * math.cos(theta)
        pygame.draw.line(
            screen, (255, 0, 0),
            (cart_x_pix + CART_WIDTH // 2, cart_y - CART_HEIGHT // 2),
            (pole_x_end, pole_y_end), POLE_WIDTH
        )  

        # Overlay text on screen
        start_text = font.render("Press SPACE to start", True, (0, 0, 0))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - start_text.get_height() // 2))
        
        # Flip display 
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            in_countdown = False
        
        continue

    # Physics
    if not game_over:
        # Read user input: left/right arrows will apply force
        keys = pygame.key.get_pressed()
        force = 0.0
        if keys[pygame.K_LEFT]:
            force = -force_mag
        elif keys[pygame.K_RIGHT]:
            force = force_mag

        # CartPole dynamics
        sintheta = math.sin(theta)
        costheta = math.cos(theta)

        temp = (force + polemass_length * theta_vel ** 2 * sintheta) / total_mass
        thetaacc = (gravity * sintheta - costheta * temp) / (
            length * (4.0 / 3.0 - (masspole * costheta ** 2) / total_mass)
        )
        xacc = temp - (polemass_length * thetaacc * costheta) / total_mass

        # Update state using dt
        x += dt * x_vel
        x_vel += dt * xacc
        theta += dt * theta_vel
        theta_vel += dt * thetaacc

        elapsed_time += dt

        # Failure conditions: cart out of bounds, pole angle too large
        if abs(x) > x_threshold or abs(theta) > theta_threshold_radians:
            game_over = True

    # Drawing
    screen.fill((255, 255, 255))

    # Draw the track
    pygame.draw.line(screen, (0, 0, 0), (0, cart_y + CART_HEIGHT // 2),
                     (SCREEN_WIDTH, cart_y + CART_HEIGHT // 2), 2)
    
    # Draw the cart
    cart_x_pix = physics_x_to_screen(x) - CART_WIDTH // 2
    cart_rect = pygame.Rect(
        cart_x_pix, cart_y - CART_HEIGHT // 2, CART_WIDTH, CART_HEIGHT
    )
    pygame.draw.rect(screen, (0, 0, 255), cart_rect)

    # Draw the pole
    pole_len_pix = length * (SCREEN_HEIGHT * 0.5)
    pole_x_end = cart_x_pix + CART_WIDTH // 2 + pole_len_pix * math.sin(theta)
    pole_y_end = cart_y - CART_HEIGHT// 2 - pole_len_pix * math.cos(theta)
    pygame.draw.line(
        screen, (255, 0, 0),
        (cart_x_pix + CART_WIDTH // 2, cart_y - CART_HEIGHT // 2),
        (pole_x_end, pole_y_end), POLE_WIDTH
    )  

    # Display time survived as score
    score_text = font.render(f"Time: {elapsed_time:.2f}s", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # If game over, show game over screen and press 'r' to restart
    if game_over: 
        over_text = font.render("Game over! Press R to restart", True, (255, 0, 0))
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_environment()

    pygame.display.flip()