import colorsys
import turtle

def draw_spiral_galaxy(steps=300, angle=59, growth=0.35):
    screen = turtle.Screen()
    screen.bgcolor("black")
    screen.title("Rainbow Spiral Galaxy")

    t = turtle.Turtle()
    t.speed(20)
    t.width(2)
    t.hideturtle()

    for i in range(steps):
        hue = (i / steps) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        t.color(r, g, b)

        t.forward(i * growth)  # each segment is a little longer than the last
        t.left(angle)

    screen.update()
    screen.exitonclick()

draw_spiral_galaxy()