# Pygame package
import pygame

# Initialize pygame
print(pygame.init())

# Set up the screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame grow a garden")

# Colors
# Colors are in (R, G, B) from 0-255
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

font = pygame.font.SysFont("arial", 72)
text_surface = font.render("Rafa", True, BLUE)
text_rect = text_surface.get_rect(center=(400, 300))

# IMPORTANT!
# Game Loop
running = True # is your game running?

while running:
    # Set up an event listener
    # First event: if quit event, then quit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    
    # Drawing

    # Rectangle (surface to draw, color, (top left x, y, width, height), thickness)
    pygame.draw.rect(screen, RED, (100, 100, 200, 100), 0)

    # Circle
    pygame.draw.circle(screen, BLUE, (600, 300), 50, 0)

    # Line
    pygame.draw.line(screen, BLACK, (50, 500), (40, 400), 5)

    screen.blit(text_surface, text_rect)
    # Update display
    pygame.display.flip()

