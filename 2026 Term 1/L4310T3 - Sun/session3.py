# imports
import pygame
import sys

# Constants

# Functions
class Player:
    def __init__(self, pos):
        # Physics
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        # Ship orientation (degrees). 0 = pointing right.
        self.angle = -90.0 # start pointing up

        # Tuning
        self.turn_speed = 220.0 # degrees per second
        self.thrust_accel = 520.0 # pixels per second^2
        self.max_speed = 420.0 # clamp velocity magnitude
        self.damping = 0.995 # slight drift reduction per frame; 0.5% reduction per frame

        # Rendering / collision
        self.radius = 16 # pixels
    
    def update(self, dt, keys, screen_size):
        # Rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.turn_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.turn_speed * dt
        
        # Thrust (acceleration in facing direction)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            forward = pygame.Vector2(1, 0).rotate(self.angle)
            self.vel += forward * self.thrust_accel * dt

        # Clamp speed
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)

        # Move
        self.pos += self.vel * dt

        # Mild damping to keep things controllable 
        self.vel *= self.damping

        # Screen wrap
        w, h = screen_size
        if self.pos.x < 0:
            self.pos.x += w
        elif self.pos.x >= w:
            self.pos.x -= w
        
        if self.pos.y < 0:
            self.pos.y += h
        elif self.pos.y >= h:
            self.pos.y -= h
        
    def _ship_points(self):
        """
        Returns 3 points (triangle) in world space.
        We'll draw a simple simple triangle ship
        """
        # Define ship triangle in local space (pointing right),
        # then rotate by angle and translate by pos
        tip = pygame.Vector2(self.radius, 0)

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
            # 2. Update all objects
            self.update(self.dt)
            # 3. Draw frame
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
    game = Game()
    game.run()

# Script entry point
if __name__ == "__main__":
    main()