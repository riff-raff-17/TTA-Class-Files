from ursina import *

app = Ursina()

# rotation speed (degrees per second)
rot_speed = 100

# Create a cube in the center of the screen
cube = Entity(
    model='cube',
    color=color.azure,
    scale=1,
    position=(0,0,0)
)

# Create on screen text
test_text = Text(
    text="minecraft",
    parent=camera.ui,
    position = (-0.01, 0.01),
    scale = 0.05,
    color = color.white
)

def update():
    if held_keys['up arrow']:
        cube.rotation_x += rot_speed * time.dt # tilt forward
    if held_keys['down arrow']:
        cube.rotation_x -= rot_speed * time.dt # tilt backwards
    if held_keys['left arrow']:
        cube.rotation_y += rot_speed * time.dt # tilt left
    if held_keys['right arrow']:
        cube.rotation_y -= rot_speed * time.dt # tilt right
    
app.run()