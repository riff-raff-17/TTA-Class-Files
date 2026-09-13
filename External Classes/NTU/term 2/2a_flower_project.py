"""
Mini Project: Polygon Flower
"""

import turtle

# --- Setup ---
screen = turtle.Screen()
screen.title("Polygon Flower")
screen.bgcolor("white")

t = turtle.Turtle()
t.speed(0)
t.shape("turtle")


def draw_polygon(turtle_obj, side_length, n_sides):
    """Draw an n-sided polygon of a certain side length."""
    for _ in range(n_sides):
        turtle_obj.forward(side_length)
        turtle_obj.right(360 / n_sides)


def draw_flower(turtle_obj, petals, sides, size, colors):
    """
    Draw 'petals' copies of a polygon, each rotated evenly around
    a full circle, cycling through the given lsit of colors.
    """
    turn_between_petals = 360 / petals
    for i in range(petals):
        color = colors[i % len(colors)]  # cycle through the list
        turtle_obj.color(color)
        draw_polygon(turtle_obj, sides, size)
        turtle_obj.right(turn_between_petals)


# --- Draw the flower ---
petal_colors = ["red", "orange", "gold", "purple", "deeppink", "blue"]
draw_flower(t, petals=12, sides=6, size=80, colors=petal_colors)
turtle.done()
