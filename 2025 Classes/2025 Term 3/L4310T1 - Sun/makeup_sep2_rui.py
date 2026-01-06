# simple_shooter.py
# A minimal first-person target shooting game with Ursina.
# Controls: WASD to move, Space to jump, Mouse to look, Left-click to shoot, Esc to quit.

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# --- Window / basics ---
window.title = 'Ursina: Simple Shooter'
window.fps_counter.enabled = True
window.exit_button.visible = False
mouse.locked = True

# --- World ---
ground = Entity(
    model='plane',
    scale=64,
    texture='white_cube',
    texture_scale=(64, 64),
    color=color.lime.tint(-.25),
    collider='box'
)

# Some simple walls so you have a sense of place
for x in (-10, 10):
    Entity(model='cube', scale=(1, 3, 20), position=(x, 1.5, 0), color=color.gray, collider='box')
for z in (-10, 10):
    Entity(model='cube', scale=(20, 3, 1), position=(0, 1.5, z), color=color.gray, collider='box')

# --- Player ---
player = FirstPersonController(
    speed=6,
    jump_height=2,
    position=(0, 2, 0)
)

# A very simple "gun" on the screen
gun = Entity(
    parent=camera.ui,
    model='cube',
    scale=(.09, .05, .2),
    position=(.6, -.4),
    rotation=(0, -20, 10),
    color=color.azure
)

# Muzzle flash (briefly shown when shooting)
muzzle_flash = Entity(
    parent=gun,
    model='quad',
    color=color.yellow,
    scale=(.2, .2),
    position=(0, 0, .3),
    enabled=False,
    billboarding=True
)

# Crosshair
crosshair = Entity(
    parent=camera.ui,
    model=Mesh(vertices=[Vec3(-.005,0,0),Vec3(.005,0,0),Vec3(0,-.005,0),Vec3(0,.005,0)], mode='line'),
    color=color.white
)

# --- Audio (optional; safe if missing) ---
try:
    shoot_sfx = Audio('assets/shoot.wav', autoplay=False)
except Exception:
    shoot_sfx = Audio(sound_file_name='', autoplay=False)  # silent fallback

# --- Targets ---
class Target(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            collider='box',
            scale=(.8, .8, .8),
            **kwargs
        )
        self.base_y = self.y
        self.health = 2
        self.t = random.random() * 100

    def update(self):
        # gentle bob + sway
        self.t += time.dt
        self.y = self.base_y + math.sin(self.t * 2) * 0.3
        self.x += math.sin(self.t) * 0.002
        self.z += math.cos(self.t * 0.7) * 0.002

    def hit(self):
        self.health -= 1
        self.animate_scale(self.scale * 0.9, duration=.08, curve=curve.in_out_sine)
        if self.health <= 0:
            # pop effect
            for _ in range(6):
                Entity(model='sphere', color=color.yellow, scale=.08, position=self.position, eternal=False)\
                    .animate_position(self.position + Vec3(random.uniform(-.6,.6), random.uniform(.4,1.2), random.uniform(-.6,.6)), duration=.3)
            destroy(self)
            spawn_target()

targets_parent = Entity()
def spawn_target():
    # Spawn in a ring around the center, at moderate height, not too close to player
    angle = random.uniform(0, 360)
    radius = random.uniform(6, 12)
    x = math.cos(math.radians(angle)) * radius
    z = math.sin(math.radians(angle)) * radius
    y = random.uniform(1.2, 3.0)
    Target(parent=targets_parent, position=(x, y, z))

for _ in range(7):
    spawn_target()

# --- UI: score + hint ---
score = 0
score_text = Text(text='Score: 0', origin=(-.5, .5), position=(-.86, .45), scale=1.2)
hint_text = Text(text='LMB to shoot | Esc to unlock mouse', origin=(.5, .5), position=(.45, .45), scale=.9, color=color.azure)

# --- Shooting mechanics ---
shoot_cooldown = 0.12
shoot_timer = 0.0
bullet_tracers = []   # track Entities to clean up

def shoot():
    global score
    # sound + flash
    if shoot_sfx.clip:
        shoot_sfx.play()
    muzzle_flash.enabled = True
    muzzle_flash.scale = (.25, .25)
    muzzle_flash.animate_scale((.0, .0), duration=.06)
    invoke(setattr, muzzle_flash, 'enabled', False, delay=.06)

    # Raycast from camera forward
    hit = raycast(camera.world_position, camera.forward, distance=60, ignore=(player,), debug=False)

    # Visual tracer
    end = camera.world_position + camera.forward * (hit.distance if hit.hit else 60)
    tracer = Entity(model='quad', color=color.white, position=(camera.world_position + end) / 2, rotation=camera.world_rotation)
    tracer.look_at(end)
    tracer.scale = (0.02, distance(camera.world_position, end))
    bullet_tracers.append(tracer)
    destroy(tracer, delay=.04)

    # If we hit a target, register the hit
    if hit.hit and isinstance(hit.entity, Target):
        hit.entity.hit()
        score += 100
        score_text.text = f'Score: {score}'

def update():
    global shoot_timer
    shoot_timer += time.dt

    # left click to shoot with a small cooldown
    if mouse.left and shoot_timer >= shoot_cooldown:
        shoot_timer = 0
        shoot()

    # cleanup any stray tracers (failsafe)
    for t in bullet_tracers[:]:
        if not t or t.enabled is False:
            bullet_tracers.remove(t)

def input(key):
    global score
    if key == 'escape':
        mouse.locked = not mouse.locked
    if key == 'right mouse down':
        # quick reload-esque shake just for feel
        gun.animate_rotation((0, -30, 20), duration=.06)
        gun.animate_rotation((0, -20, 10), duration=.1, delay=.06)
    if key == 'r':
        # reset game
        for e in targets_parent.children[:]:
            destroy(e)
        for _ in range(7):
            spawn_target()
        score = 0
        score_text.text = 'Score: 0'

# Optional sun light
DirectionalLight().look_at(Vec3(1, -1, -1))
Sky(color=color.cyan.tint(.2))

app.run()
