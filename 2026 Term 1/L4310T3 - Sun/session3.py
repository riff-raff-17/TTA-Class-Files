# imports
import pygame
import sys

# Constants

# Functions
class Game:
    # always start with self!
    def __init__(self, width=800, height=450, caption="Pygame OOP"):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()
        self.running = True

        # We'll use dt (delta time) in later sessions for smooth movement
        self.dt = 0.0

    def run(self):
        """Main game loop"""
        while self.running:
            # dt in seconds (e.g., 0.016 at ~60 FPS)
            # dt is also called frametime
            self.dt = self.clock.tick(60) / 1000.0

            # 1. Handle events (inputs)
            self.handle_events()
            self.update(self.dt)
            self.draw()

        self.quit()

    def handle_events(self):
        """Handle all events (inputs)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, pygame.K_q}:
                    self.running = False

    def update(self, dt):
        """Update game state. (Nothing yet here)"""
        pass

    def draw(self):
        """Draw everything each frame"""
        self.screen.fill((25, 25, 35)) # Background color

        # In later sessions we'll draw entities here.

        pygame.display.flip()

    def quit(self):
        """Clean shutdown"""
        pygame.quit()
        sys.exit()
        

# Main loop
def main():
    print("Hello")

# Script entry point
if __name__ == "__main__":
    main()