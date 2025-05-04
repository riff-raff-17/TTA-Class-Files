'''Setup and display car'''

import pygame
import math
import sys
import neat

# Constants
SCREEN_WIDTH = 1244
SCREEN_HEIGHT = 1016
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

TRACK = pygame.image.load('Assets/not_car/track.png')

GRASS_COLOR = pygame.Color(2, 105, 31, 255)
START_POS = (490, 820)

pygame.init()

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # This is the image of your car
        self.original_image = pygame.image.load('Assets/not_car/car.png')
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(490, 820))
        self.drive_state = False
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.time_since_death = 0

    def update(self):
        self.drive()
        self.rotate()

    def drive(self):
        if self.drive_state:
            self.rect.center += self.vel_vector * 6

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def check_collision(self):
        # Get color of the pixel under the car's center position
        x, y = int(self.rect.centerx), int(self.rect.centery)
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT: # Ensure within bounds
            color_at_car = SCREEN.get_at((x, y))
            if color_at_car == GRASS_COLOR:
                print("Car hit the grass! Respawning...")
                self.respawn()

    def respawn(self):
        global time_since_death
        self.time_since_death = pygame.time.get_ticks()
        self.rect.center = START_POS
        self.angle = 0
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.direction = 0
        self.drive_state = False

    def draw_info(self, start_time):
        global time_since_death
        font = pygame.font.Font(None, 36)

        # Current time
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        death_time = (pygame.time.get_ticks() - self.time_since_death) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        death_minutes = death_time // 60
        death_seconds = death_time % 60
        timer_text = f'Time: {minutes:02}:{seconds:02}'
        lap_time_text = f'Lap time: {death_minutes:02}:{death_seconds:02}'

        # Draw background box
        info_box = pygame.Rect(SCREEN_WIDTH - 220, 10, 210, 70)
        pygame.draw.rect(SCREEN, (0, 0, 0), info_box, border_radius=5)
        pygame.draw.rect(SCREEN, (255, 255, 255), info_box, 2, border_radius=5)

        # Blit text onto the screen
        timer_surface = font.render(timer_text, True, (255, 255, 255))
        lap_surface = font.render(lap_time_text, True, (255, 255, 255))
        SCREEN.blit(timer_surface, (SCREEN_WIDTH - 210, 20))
        SCREEN.blit(lap_surface, (SCREEN_WIDTH - 210, 40))

car = pygame.sprite.GroupSingle(Car())

def eval_genomes():
    start_time = pygame.time.get_ticks()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.blit(TRACK, (0, 0))

        # User Input
        user_input = pygame.key.get_pressed()
        if sum(pygame.key.get_pressed()) <= 1:
            car.sprite.drive_state = False
            car.sprite.direction = 0

        # Drive
        if user_input[pygame.K_UP]:
            car.sprite.drive_state = True

        # Steering time
        if user_input[pygame.K_RIGHT]:
            car.sprite.direction = 1
        if user_input[pygame.K_LEFT]:
            car.sprite.direction = -1

        # Update everything
        # Check for collisions after update but before drawing on screen
        car.update()
        car.sprite.check_collision()

        car.draw(SCREEN)
        car.sprite.draw_info(start_time)
        pygame.display.update()

eval_genomes()