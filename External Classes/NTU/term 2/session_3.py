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


# def draw_polygon(turtle_obj, sides, size):
#     """Draw a regular polygon with the given number of sides and side length."""
#     angle = 360 / sides
#     for _ in range(sides):
#         turtle_obj.forward(size)
#         turtle_obj.right(angle)

# def draw_flower(turtle_obj, petals, sides, size, colors):
#     """
#     Draw 'petals' copies of a polygon, each rotated evenly around
#     a full circle, picking a random color and FILLING each petal.
#     """
#     turn_between_petals = 360 / petals
#     for _ in range(petals):
#         turtle_obj.color(random.choice(colors))
#         turtle_obj.begin_fill()
#         draw_polygon(turtle_obj, sides, size)
#         turtle_obj.end_fill()
#         turtle_obj.right(turn_between_petals)

petal_colors = ["red", "orange", "gold", "purple", "deeppink", "blue", "yellow", "green",
                "indigo", "violet"]
# draw_flower(t, petals=12, sides=6, size=60, colors=petal_colors)

t.clear()

turtle.tracer(1, 2)

# def spinner(turtle_obj, colors):
#     for i in range(360):
#         for color in colors:
#             turtle_obj.pencolor(color)
#             turtle_obj.forward(i)
#             turtle_obj.left(67)

# spinner(t, petal_colors)

t.clear()

for i in range(20):
    t.penup()
    t.goto(random.randint(-200, 200), random.randint(-200, 200))
    t.setheading(0)
    t.pendown()
    t.pencolor(random.choice(petal_colors))
    t.fillcolor(random.choice(petal_colors))
    t.begin_fill()
    t.circle(random.randint(40, 100))
    t.end_fill()

def draw_circle_flower(turtle_obj, petals, radius, colors):
    """
    An alternative to draw_flower: petals made of overlapping
    circles instead of polygons. No draw_polygon needed at all;
    circle() does the shape drawing for us.
    """
    turn_between_petals = 360 / petals
    for _ in range(petals):
        turtle_obj.fillcolor(random.choice(colors))
        turtle_obj.begin_fill()
        turtle_obj.circle(radius)
        turtle_obj.end_fill()
        turtle_obj.right(turn_between_petals)

t.clear()
for i in range(10):
    t.penup()
    t.goto(random.randint(-300, 300), random.randint(-300, 300))
    t.pendown()
    t.pencolor(random.choice(petal_colors))
    draw_circle_flower(t, petals=8, radius=random.randint(25, 100), colors=petal_colors)
    t.dot(14, "black")  # dot marks the center


turtle.done()