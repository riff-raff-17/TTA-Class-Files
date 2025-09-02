from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Add a ground plane
ground = Entity(
    model='plane',
    texture='grass',
    collider='box',
    scale=(100, 1, 100)
)

# Add a cube the player can look at
cube = Entity(
    model='cube',
    color=color.orange,
    texture='rainbow',
    position=(0, 0.5, 0),
    collider='box'
)

# Add a light source
DirectionalLight().look_at((1,-1,-1))

# Replace EditorCamera with FirstPersonController
player = FirstPersonController()
player.gravity = 0          # optional: no falling, free-fly style
player.cursor.visible = True
player.speed = 5

def input(key):
    if key == 'left mouse down':
        # Add a cube where the mouse points
        hit_info = mouse.hovered_entity
        if hit_info and hit_info.collider:
            new_cube = Entity(
                model='cube',
                color=color.white,
                texture='white_cube',
                position=hit_info.position + mouse.normal,
                collider='box'
            )
    if key == 'right mouse down' and mouse.hovered_entity:
        # Delete the cube we clicked on (but not the ground)
        if mouse.hovered_entity != ground:
            destroy(mouse.hovered_entity)

app.run()
