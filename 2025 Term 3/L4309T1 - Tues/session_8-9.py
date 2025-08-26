# grass_top_dirt_sides.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image
import random, os


# ---------- Procedural textures ----------
def make_dirt_texture(path='dirt.png', size=16):
    """Creates a small noisy dirt tile."""
    img = Image.new('RGB', (size, size))
    p = img.load()
    base = (134, 96, 67)
    for y in range(size):
        for x in range(size):
            n = random.randint(-14, 14)
            r = max(0, min(255, base[0] + n))
            g = max(0, min(255, base[1] + n))
            b = max(0, min(255, base[2] + n))
            if random.random() < 0.06:  # darker specks
                r, g, b = int(r*0.7), int(g*0.7), int(b*0.7)
            if random.random() < 0.05:  # lighter specks
                r, g, b = min(255,int(r*1.15)), min(255,int(g*1.10)), min(255,int(b*1.05))
            p[x, y] = (r, g, b)
    img.save(path)
    return path

def make_grass_texture(path='grass.png', size=16):
    """Creates a grassy green tile with gentle noise so it looks organic."""
    img = Image.new('RGB', (size, size))
    p = img.load()
    base=(95, 159, 53)
    for y in range(size):
        for x in range(size):
            n = random.randint(-10, 10)
            r = max(0, min(255, base[0] + n))
            g = max(0, min(255, base[1] + n))
            b = max(0, min(255, base[2] + n))
            if random.random() < 0.03:
                r, g, b = min(255,int(r*1.1)), min(255,int(g*1.1)), min(255,int(b*1.05))
            p[x, y] = (r, g, b)
    img.save(path)
    return path


# Ensure textures exist
DIRT_PATH = 'dirt.png'
GRASS_PATH = 'grass.png'
if not os.path.exists(DIRT_PATH):
    make_dirt_texture(DIRT_PATH, size=16)
if not os.path.exists(GRASS_PATH):
    make_grass_texture(GRASS_PATH, size=16)


# ---------- Ursina setup ----------
app = Ursina()
window.color = color.rgb(180, 220, 255)  # sky-ish
Texture.default_filtering = None  # keep pixel art crisp

tex_dirt = load_texture(DIRT_PATH)
tex_grass = load_texture(GRASS_PATH)


# ---------- Voxel made of two parts: dirt base + thin grass cap ----------
class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            origin_y=.5,   # so it sits on the ground nicely
            model=None,    # we'll use child entities for visuals
            collider='box',
            highlight_color=color.lime
        )

        # Dirt base (full cube)
        self.base = Entity(
            parent=self,
            model='cube',
            texture=tex_dirt,
            color=color.white,
            scale=(1, 1, 1),
            y=0
        )

        # Grass cap: very thin cube on top to avoid z-fighting
        # origin_y=.5 means top surface is at y=+0.5
        # Make cap ~0.04 tall and place it so it sits on top
        cap_height = 0.04
        self.cap = Entity(
            parent=self,
            model='cube',
            texture=tex_grass,
            color=color.white,
            scale=(1.001, cap_height, 1.001),  # tiny overscale to avoid edge peeking
            y=(0.5 - cap_height/2) + 0.0005     # tiny offset to prevent z-fighting
        )


# Build some ground
for z in range(8):
    for x in range(8):
        Voxel(position=(x, 0, z))


# ---------- Interactions ----------
def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)

    if key == 'right mouse down' and mouse.hovered_entity:
        # Destroy the Voxel "parent" if you clicked any of its parts
        to_destroy = mouse.hovered_entity
        while to_destroy and not isinstance(to_destroy, Voxel):
            to_destroy = to_destroy.parent
        if to_destroy:
            destroy(to_destroy)


player = FirstPersonController()
player.y = 2
app.run()
