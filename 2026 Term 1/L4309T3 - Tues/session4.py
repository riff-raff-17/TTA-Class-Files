# imports
import sys
import pygame

class Player:
    def __init__(self, pos):
        # Physics
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

        # Ship orientation (degrees). 0 = pointing right
        self.angle = -90.0 # Start pointing up

        # Tuning
        self.turn_speed = 220.0 # degrees per second
        self.thrust_accel = 520.0 # pixels per second^2
        self.max_speed = 420.0 # clamp velocity magnitude (pixels per second)
        self.damping = 0.995 # slight drift reduction per frame

        # Rendering/Collision
        self.radius = 16

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

        # Mild damping to keep things controllable (can reduce/remove later)
        self.vel *= self.damping

        # Screen wrap
        w, h = screen_size

        # Width
        if self.pos.x < 0:
            self.pos.x += w
        elif self.pos.x >= w:
            self.pos.x -= w

        # Height
        if self.pos.y < 0:
            self.pos.y += h
        elif self.pos.y >= h:
            self.pos.y -= h

    def _ship_points(self):
        """
        Returns 3 points (triangle) in world space.
        We'll draw a simple triangle ship.
        """
        pass

class Game:
    def __init__(self, width=800, height=450, caption="Pygame OOP Skeleton"):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()
        self.running = True

        # We'll use dt (delta time) in later sessions for smooth movement.
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
        """Handle all input/events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, dt):
        """Update game state. (Nothing here yet)"""
        pass

    def draw(self):
        """Draw everything each frame"""
        self.screen.fill((25, 25, 35))

        # In later session we'll draw entities here.

        pygame.display.flip()

    def quit(self):
        """Clean shutdown"""
        pygame.quit()
        sys.exit()

# main loop
def main():
    Game().run()

# script entry point
if __name__ == "__main__":
    main()