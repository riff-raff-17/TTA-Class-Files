from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image

app = Ursina()

MC_RGB = [
    (112, 192, 87), # grass green
    (183, 157, 97), # grass brown
    (47, 242, 255) # ice blue
]

def make_dirt(path='dirt.png', size=16):
    img = Image.new("RGB", (size, size))
    p = img.load()
    base = (159, 104, 62)

    for y in range(size):
        for x in range(size):
            # Add some per pixel noise so they don't all look the same
            n = random.randint(-14, 14)
            r = max(0, min(255, base[0] + n))
            g = max(0, min(255, base[1] + n))
            b = max(0, min(255, base[2] + n))

            # Occasional dark
            if random.random() < 0.06:
                r, g, b = int(r*0.7), int(g*0.7), int(b*0.7)

            # Occasional light
            if random.random() < 0.05:
                r, g, b = min(255, int(r*1.15)),min(255, int(g*1.15)), min(255, int(b*1.15))

            p[x, y] = (r, g, b)
        img.save(path)
        return path
    
def make_grass(path='grass.png', size=16):
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

DIRT_PATH = 'dirt.png'
GRASS_PATH = 'grass.png'
if not os.path.exists(DIRT_PATH):
    make_dirt(DIRT_PATH, size=16)
if not os.path.exists(GRASS_PATH):
    make_grass(GRASS_PATH, size=16)

tex_dirt = load_texture(DIRT_PATH)
tex_grass = load_texture(GRASS_PATH)

class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            origin_y=0.5,
            model=None,
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

        cap_height = 0.04
        self.cap = Entity(
            parent=self,
            model='cube',
            texture=tex_grass,
            color=color.white,
            scale=(1.001, cap_height, 1.001),
        )

# Build some ground
for z in range(8):
    for x in range(8):
        Voxel(position=(x, 0, z))

# Interactions
def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)
    
    if key == 'right mouse down' and mouse.hovered_entity:
        # Destroy the Voxel 'parent' if you clicked any of its parts
        to_destroy = mouse.hovered_entity
        while to_destroy and not isinstance(to_destroy, Voxel):
            to_destroy = to_destroy.parent
        if to_destroy:
            destroy(to_destroy)

player = FirstPersonController()
player.y=2
app.run()