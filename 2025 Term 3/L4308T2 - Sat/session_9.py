from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Ground
'''
Textures: noise, grass, vignette, arrow_right, test_tileset, 
tilemap_test_level, shore, file_icon, sky_sunset, radial_gradient, 
circle, perlin_noise, brick, grass_tintable, circle_outlined, 
ursina_logo, arrow_down, cog, vertical_gradient, white_cube, 
horizontal_gradient, folder, rainbow, heightmap_1, sky_default
'''

ground = Entity(model='plane', scale=(50, 1, 50), texture="grass", 
                texure_scale=(50, 50), collider='box')

# Basic player 
player = FirstPersonController(collider='box', y=1)
player.cursor.color = color.white
player.cursor.scale = 0.001
player.cursor.model = 'circle'
player.speed = 5 

# UI
score = 0
total_cubes = 3
score_text = Text(text=f"Cubes: {score}/{total_cubes}", parent=camera.ui, 
                  position=(-0.02, 0.02), origin=(0, 0), world_scale=1)

cubes = []
for _ in range(total_cubes):
    pos = Vec3(random.randint(-10, 10), 0.5, random.randint(-10, 10))
    cube = Entity(model='cube', texture='brick', collider='box', position=pos, 
                  color=color.orange)
    cubes.append(cube)

def update():
    global score
    hit = player.intersects()
    if hit.hit and hit.entity in cubes:
        destroy(hit.entity)
        cubes.remove(hit.entity)
        score += 1
        score_text.text = f"Cubes: {score}/{total_cubes}"

app.run()