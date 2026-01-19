import turtle

# turtle screen setup
screen = turtle.Screen()
screen.title("Landy's LightReflection")

# makes ONE turtle object
class Pen:
    def __init__(self, color="green", speed=1):
        self.t = turtle.Turtle()
        self.t.color(color)
        self.t.shape("turtle")
        self.t.speed(1)

    # movement
    def square(self, size):
        for _ in range(4):
            self.t.forward(size)
            self.t.left(90)

# keeps the screen active
pen = Pen(color="brown")
pen2 = Pen(color="red")
pen.square(100)

screen.mainloop() 