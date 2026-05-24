from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LVector3, LVector4
from direct.task import Task


class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        # --- Scene ---
        self.setBackgroundColor(0.1, 0.1, 0.15, 1)  # dark background

        # Load a built-in box model and put it in the scene
        self.box = self.loader.loadModel("box")
        self.box.reparentTo(self.render)
        self.box.setScale(1.5)
        self.box.setPos(0, 10, 0)  # x, y (depth), z (height)

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
        for key in ["arrow_left", "arrow_right", "arrow_up", "arrow_down", "a", "d"]:
            self.keys[key] = 0
            self.accept(key, self.set_key, [key, 1])
            self.accept(key + "-up", self.set_key, [key, 0])

            # Tasls
            self.taskMgr.add(self.spin_box, "spin_box")
            self.taskMgr.add(self.move_camera, "move_camera")

            print("Controls:")
            print("Arrow Left / Right - rotate box")
            print("Arrow Up / Down - move camera forward / back")
            print("A / D - strafe camera left / right")

            # --- Helpers ---
            def set_key(self, key, value):
                self.keys[key] = value

            def spin_box(self, task):
                """Rotate the box a little every frame based on arrows keys."""
                dt = globalClock.getDt()
                speed = 360  # degrees per second

                if self.keys["arrow_left"]:
                    self.box.setH(self.box.getH() + speed * dt)
                if self.keys["arrow_right"]:
                    self.box.setH(self.box.getH() - speed * dt)

                return Task.cont  # keep running

        def move_camera(self, task):
            """Move the camera with arrow up/down and A/D"""
            dt = globalClock.getDt()
            speed = 8

            if self.keys["arrow_up"]:
                self.camera.setY(self.camera, speed * dt)  # forward
            if self.keys["arrow_down"]:
                self.camera.setY(self.camera, -speed * dt)  # backward
            if self.keys["a"]:
                self.camera.setX(self.camera, -speed * dt)  # strafe left
            if self.keys["d"]:
                self.camera.setX(self.camera, speed * dt)  # strafe left
            
            return Task.cont
        
game = MyGame()
game.run()