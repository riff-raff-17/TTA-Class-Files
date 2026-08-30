import colorsys
import turtle

screen = turtle.Screen()
screen.title("My turtle")

t = turtle.Turtle()
t.shape("turtle")
t.speed(1)  # 0 = instant, 1-10 faster

# Basic movement
t.forward(100)  # Move forward 100 pixels
t.right(90)  # turn right 90 degrees
t.left(90)  # turn left 90 degrees
t.backward(50)  # move backward 50 pixels

# Changing pen settings

t.pensize(3)  # thicker lines
t.color("blue")  # change pen color

t.forward(80)
t.right(90)
t.forward(80)

t.color("red")  # new color
t.pensize(5)
t.forward(80)

# Pen Up / Pen Down
# Move the turtle without drawing

t.penup()
t.goto(-50, 50)  # move to a new position
t.pendown()

t.color("green")
t.circle(40)  # draw a circle with radius 40

n = 4
for i in range(n):
    # Cycle the hue smoothly through the rainbow
    hue = i / n
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    t.color(r, g, b)
    t.forward(60)
    t.right(90)

t.color("#70134E")

screen.mainloop()
