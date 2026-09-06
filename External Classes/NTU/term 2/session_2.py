import turtle

# --- Setup ---
screen = turtle.Screen()
screen.title("Functions, Loops, and Lists")

t = turtle.Turtle()
t.shape("turtle")
t.speed(0)  # 0 is fastest

# --- Variables ---
side_length = 60
turn_angle = 90

for _ in range(4):
    t.forward(side_length)
    t.right(turn_angle)


# --- Functions ---
def draw_square(turtle_obj, size):
    """Draw a square of the given size using the given turtle."""
    for _ in range(4):
        turtle_obj.forward(size)
        turtle_obj.right(90)


t.penup()
t.goto(-150, 100)
t.pendown()
draw_square(t, 40)


def draw_polygon(turtle_obj, side_length, n_sides):
    """Draw an n-sided polygon of a certain side length."""
    for _ in range(n_sides):
        turtle_obj.forward(side_length)
        turtle_obj.right(360 / n_sides)


t.penup()
t.goto(50, 100)
t.pendown()
draw_polygon(turtle_obj=t, side_length=10, n_sides=60)

# --- Nested loops ---
t.clear()  # clear screen
t.penup()
t.goto(0, 0)
t.pendown()

for i in range(5):
    size = 20 + i * 15  # grows: 20, 35, 50, 65, 80
    draw_polygon(turtle_obj=t, side_length=size, n_sides=4)
    t.penup()
    t.forward(size + 20)  # move over before the next shape
    t.pendown()

# --- A TRULY nested loop ---
t.penup()
t.goto(-150, -250)
t.pendown()

rows = 3
cols = 4
grid_start_x, grid_start_y = -150, -250

for row in range(rows):
    for col in range(cols):
        t.penup()
        t.goto(grid_start_x + col * 40, grid_start_y - row * 40)
        t.pendown()
        draw_polygon(turtle_obj=t, side_length=20, n_sides=5)

# --- Lists as containers of related values ---
# A list stores multiple values in one variable. We can loop
# over it directly with "for x in my_list"

colors = ["red", "blue", "green", "purple", "orange"]

def draw_colored_square(turtle_obj, size, color):
    turtle_obj.color(color)
    draw_polygon(turtle_obj=turtle_obj, side_length=size, n_sides=4)

t.penup()
t.goto(-150, -150)
t.pendown()

for color in colors:
    draw_colored_square(t, 30, color)
    t.penup()
    t.forward(50)
    t.pendown()

# --- If/elif/else conditionals ---
t.clear()
t.penup()
t.goto(0, 0)
t.pendown()

turtle.done()
