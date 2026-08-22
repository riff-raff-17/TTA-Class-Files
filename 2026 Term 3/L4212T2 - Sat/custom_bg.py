import os

import pygame

pygame.init()

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 480

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chocolate Chip Cookie Presser")

clock = pygame.time.Clock()
FPS = 60

BACKGROUND_COLOR = (255, 244, 214)
TEXT_COLOR = (70, 45, 20)

COOKIE_COLOR = (216, 148, 60)
COOKIE_HOVER_COLOR = (232, 168, 82)
COOKIE_PRESSED_COLOR = (245, 188, 104)
CHIP_COLOR = (110, 64, 24)

big_font = pygame.font.SysFont(None, 48)

# --- Load custom images ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

BACKGROUND_IMAGE = None
COOKIE_IMAGE = None

background_path = os.path.join(ASSETS_DIR, "background.png")
if os.path.exists(background_path):
    BACKGROUND_IMAGE = pygame.image.load(background_path).convert()
    BACKGROUND_IMAGE = pygame.transform.smoothscale(
        BACKGROUND_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
else:
    print(f"No background found at {background_path}, using solid color instead.")

cookie_path = os.path.join(ASSETS_DIR, "cookie.png")
if os.path.exists(cookie_path):
    COOKIE_IMAGE = pygame.image.load(cookie_path).convert_alpha()
else:
    print(f"No cookie image found at {cookie_path}, drawing a circle instead.")


class CookieButton:
    def __init__(self, center_x, center_y, radius, on_click):
        self.center = (center_x, center_y)
        self.radius = radius
        self.on_click = on_click
        self.is_pressed = False

    def collidepoint(self, pos):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.collidepoint(mouse_pos)
        is_shrunk = self.is_pressed and is_hovering

        if COOKIE_IMAGE is not None:
            # Slightly shrink the image while pressed for click feedback
            scale = 0.94 if is_shrunk else 1.0
            diameter = int(self.radius * 2 * scale)
            image = pygame.transform.smoothscale(COOKIE_IMAGE, (diameter, diameter))
            rect = image.get_rect(center=self.center)
            surface.blit(image, rect)
        else:
            # Fallback: draw the original vector cookie
            if is_shrunk:
                color = COOKIE_PRESSED_COLOR
            elif is_hovering:
                color = COOKIE_HOVER_COLOR
            else:
                color = COOKIE_COLOR

            radius = self.radius - 4 if is_shrunk else self.radius
            pygame.draw.circle(surface, color, self.center, radius)

            chip_offsets = [(-25, -15), (10, -25), (25, 10), (-15, 20), (0, 0), (-30, 15)]
            for ox, oy in chip_offsets:
                pygame.draw.circle(
                    surface, CHIP_COLOR, (self.center[0] + ox, self.center[1] + oy), 5
                )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.collidepoint(event.pos):
            self.is_pressed = True
            self.on_click()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False


cookies = 0


def click_cookie():
    global cookies
    cookies += 1


cookie = CookieButton(260, 220, 70, click_cookie)

# Main loop
running = True

while running:
    clock.tick(FPS)

    # --- 1. Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        cookie.handle_event(event)

    # --- 2. Update state ---
    # Nothing yet

    # --- 3. Draw the frame ---
    if BACKGROUND_IMAGE is not None:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)

    cookie.draw(screen)

    count_surface = big_font.render(f"{cookies} cookies", True, TEXT_COLOR)
    screen.blit(count_surface, (20, 20))

    pygame.display.flip()

pygame.quit()