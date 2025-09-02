from ursina import *

app = Ursina()

# Add a ground plane
ground = Entity(
    model='plane',
    texture='grass',
    collider='box',
    scale=(10, 1, 10)
)

cube = Entity(
    model='cube',
    color=color.orange,
    texture="perlin_noise", # other textures: grass, brick, shore, arrow_right
    # circle, circle_outline, radial_gradient, perlin_noise, rainbow
    position=(0, 1, 0),
    collider='box',
    scale=(2,3,4)
)

# Add a light source and camera
DirectionalLight().look_at((1, -1, 1))
EditorCamera() # lets you move around with right mouse click

def input(key):
    if key == "left mouse down":
        # Add a cube where the mouse points
        hit_info = mouse.hovered_entity
        if hit_info and hit_info.collider:
            new_cube = Entity(
                    model='cube',
                    color=color.orange,
                    texture="perlin_noise",
                    position=hit_info.position + mouse.normal,
                    collider='box',
                    scale=(2,3,4)
            )

    if key == "right mouse down" and mouse.hovered_entity:
        # Delete the cube we clicked on (but NOT the ground)
        if mouse.hovered_entity != ground:
            destroy(mouse.hovered_entity)

app.run()