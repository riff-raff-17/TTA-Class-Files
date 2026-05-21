from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LVector3, LVector4
from direct.task import Task

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        # --- Scene ---
        self.setBackgroundColor(0.1, 0.1, 0.15, 1) # dark background

        # Load a built-in box model and put it in the scene
        self.box = self.loader.loadModel("box")
        self.box.reparentTo(self.render)
        self.box.setScale(1.5)
        self.box.setPos(0, 10, 0) # x, y (depth), z (height)

        # --- Lighting ---
        # Ambient light so nothing is pitch black
        ambient = AmbientLight("ambient")
        ambient.setColor(LVector4(0.3, 0.3, 0.3, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        # Directional light (like the sun)
        sun = DirectionalLight("sun")
        sun.setColor(LVector4(1, 0.95, 0.8, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)
        self.render.setLight(sun_np)

        # --- Input ---
        # Disable the default mouse-based camera control
        self.disableMouse()
        self.camera.setPos(0, -15, 5)
        self.camera.lookAt(self.box)

        self.keys = {}