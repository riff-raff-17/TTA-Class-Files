import turtle
import random

# Screen and turtle setup
screen = turtle.Screen()
screen.bgcolor("black")

t = turtle.Turtle()
t.speed(0)
t.width(2)

colors = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "white"]

# Draw a firework
def draw_firework(x, y, radius=100, rays=36):
    t.penup()
    t.goto(x, y)
    t.pendown()

    t.color(random.choice(colors))

    angle = 360 / rays

    for _ in range(rays):
        t.forward(radius)
        t.backward(radius)
        t.right(angle)

