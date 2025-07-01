from ursina import *

app = Ursina()

# Rotation speed (degrees per second)
rot_speed = 100

# Create a cube in the center of the scene
cube = Entity(model='cube', color=color.azure, scale=1)

# Create some on-screen text
text = Text(text="ANY AWESOME AUSTIN", parent=camera.ui, position=(-0.02, 0), 
            scale=0.15, color=color.white)

def update():
    # Rotate the cube a bit each frame
    cube.rotation_x += time.dt * 40
    cube.rotation_y += time.dt * 30

    # Rotate with wasd
    if held_keys['up arrow']:
        cube.rotation_x += rot_speed * time.dt
    if held_keys['down arrow']:
        cube.rotation_x -= rot_speed * time.dt
    if held_keys['left arrow']:
        cube.rotation_y += rot_speed * time.dt
    if held_keys['right arrow']:
        cube.rotation_y -= rot_speed * time.dt

    # Update the text every frame
    text.text = f"ANY AWESOME AUSTIN \nFPS: {round(1/time.dt)}"

app.run()