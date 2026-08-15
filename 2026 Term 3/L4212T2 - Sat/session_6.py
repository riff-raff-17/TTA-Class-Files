import pygame

# --- Setup --- 
pygame.init()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Buttons")

clock = pygame.time.Clock()
FPS = 60

BACKGROUND_COLOR = (20, 20, 30)
BUTTON_IDLE_COLOR = (60, 60, 140)
BUTTON_HOVER_COLOR = (90, 90, 200)
BUTTON_PRESSED_COLOR = (130, 130, 230)
TEXT_COLOR = (255, 255, 255)

font = pygame.font.SysFont(None, 24)
status_font = pygame.font.SysFont(None, 28)

# --- A reuseable Button class ---
class Button:
    """A clickable rectangle with a label and an on_click callback."""
    def __init__(self, x, y, width, height, label, on_click):