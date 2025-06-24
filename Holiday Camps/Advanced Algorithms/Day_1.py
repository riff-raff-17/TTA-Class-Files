import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 30)
SPRITE_SIZE = (100, 60)
SPRITE_POSITION = (350, 270)
SPRITE_SPEED = 10

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The GREATEST GAME of ALL TIME")

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

# Load and scale the image
sprite_image = pygame.image.load("Piranha_Plant.png").convert_alpha()
sprite_image = pygame.transform.scale(sprite_image, SPRITE_SIZE)

# Sprite position
sprite_x, sprite_y = 400, 300

# =================================

# Game (main) loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        sprite_x -= SPRITE_SPEED
    if keys[pygame.K_RIGHT]:
        sprite_x += SPRITE_SPEED
    if keys[pygame.K_UP]:
        sprite_y -= SPRITE_SPEED
    if keys[pygame.K_DOWN]:
        sprite_y += SPRITE_SPEED    

    # Fill the screen with COLOR
    screen.fill(BACKGROUND_COLOR)

    # Draw a shape
    screen.blit(sprite_image, (sprite_x, sprite_y))

    # pygame.draw.circle(screen, SHAPE_COLOR, (400, 300), 50)

    # Update the display by flipping it
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Clean up and exit
pygame.quit()
sys.exit()