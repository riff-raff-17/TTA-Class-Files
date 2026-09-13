import random
import turtle

# --- Setup ---
screen = turtle.Screen()
screen.title("Randomness")
screen.bgcolor("white")

t = turtle.Turtle()
t.speed(0)

# --- The random module ---
# whole number, both ends included
print("random.randint(1, 6) ->", random.randint(1, 6))
# one item from a list
print("random.choice([...]) ->", random.choice(["red", "blue", "green"]))
# float between 0.0 and 1.0
print("random.random()      ->", random.random())


def draw_polygon(turtle_obj, sides, size):
    """Draw a regular polygon with the given number of sides and side length."""
    angle = 360 / sides
    for _ in range(sides):
        turtle_obj.forward(size)
        turtle_obj.right(angle)

def draw_flower(turtle_obj, petals, sides, size, colors):
    """
    Draw 'petals' copies of a polygon, each rotated evenly around
    a full circle, picking a random color and FILLING each petal.
    """
    turn_between_petals = 360 / petals
    for _ in range(petals):
        turtle_obj.color(random.choice(colors))
        turtle_obj.begin_fill()
        draw_polygon(turtle_obj, sides, size)
        turtle_obj.end_fill()
        turtle_obj.right(turn_between_petals)

petal_colors = ["red", "orange", "gold", "purple", "deeppink", "blue"]
draw_flower(t, petals=12, sides=6, size=60, colors=petal_colors)

t.clear()

turtle.tracer(10, 0.5)

def spinner(turtle_obj, colors):
    for i in range(360):
        for color in colors:
            turtle_obj.pencolor(color)
            turtle_obj.forward(i)
            turtle_obj.left(124)

spinner(t, petal_colors)

turtle.done()