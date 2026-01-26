import sys
import pygame

class Player:
    def __init__(self, x, y, size=40, speed=300.0):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed # pixels per second

    def update(self, dt, keys, bounds_rect):
        dx = 0.0
        dy = 0.0

        # Arrows keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt

        # Move (Rect stores ints, so we accumulate into x/y via floats if needed later)
        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # Keep payer inside the window
        self.rect.clamp_ip(bounds_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, (80, 200, 120), self.rect)

class Game:
    def __init__(self, width=800, height=450, caption="Pygame Skeleton"):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(caption)

        self.clock = pygame.time.Clock()
        self.running = True

        # We'll use dt (delta time) in later sessions for smooth movement
        self.dt = 0.0

    def run(self):
        """Main game loop"""
        while self.running:
            # dt in seconds (e.g., 0.016 at ~60 FPS)
            self.dt = self.clock.tick(60) / 1000.0

            self.handle_events()
            self.update(self.dt)
            self.draw()
        
        self.quit()

    def handle_events(self):
        """Handle all inputs"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Checks for key presses
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt):
        """Update game state. (Nothing here yet)"""
        pass

    def draw(self):
        """Draw everything each frame."""
        self.screen.fill((25, 25, 35)) # Background color

        # In later sessions we'll draw entities here

        pygame.display.flip()

    def quit(self):
        """Clean shutdown"""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()