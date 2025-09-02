from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
                         position = position,
                         model = "cube",
                         origin_y=.5,
                         texture="grass",
                         color=color.hsv(0, 0, random.uniform(.9, 1.0)),
                         highlight_color=color.lime)

for z in range(8):
    for x in range(8):
        voxel=Voxel(position=(x,0,z))

def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)
    if key == 'right mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)

player = FirstPersonController()
player.cursor.scale = 0.001
app.run()