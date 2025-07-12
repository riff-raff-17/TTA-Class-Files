import turtle
import time
import random
import collections

screen = turtle.Screen()

# Just for me ==================================================
rootwindow = screen.getcanvas().winfo_toplevel()
rootwindow.call('wm', 'attributes', '.', '-topmost', '1')
rootwindow.call('wm', 'attributes', '.', '-topmost', '0')
screen.title("Turtle Tutorial")
# ===============================================================

# config
CELL_SIZE = 20
GRID_W, GRID_H = 20, 15 # 20 cells across, 15 cells high
WALL_PROB = 0.25
DELAY = 0.01 # seconds between each step

# set up screen
screen.setup(GRID_W * CELL_SIZE + 50, GRID_H * CELL_SIZE + 50)
screen.title("BFS Pathfinding")
screen.tracer(0)

t = turtle.Turtle()
t.hideturtle()
t.penup()

# Draw our walls
def draw_cell(x, y, color):
    t.goto(x * CELL_SIZE - (GRID_W * CELL_SIZE) / 2,
           (GRID_H * CELL_SIZE) / 2 - y * CELL_SIZE)
    t.fillcolor(color)
    t.begin_fill()
    for i in range(4):
        t.pendown()
        t.forward(CELL_SIZE)
        t.right(90)
    t.end_fill()
    t.penup()

# generate random maze: True = wall, False = clear
grid = [[random.random() < WALL_PROB for i in range(GRID_W)] 
        for j in range(GRID_H)]

start = (0, 0)
goal = (GRID_W - 1, GRID_H - 1)
grid[start[1]][start[0]] = False
grid[goal[1]][goal[0]] = False

for y in range(GRID_H):
    for x in range(GRID_W):
        draw_cell(x, y, 'black' if grid[y][x] else 'white')

# mark the start and goal
draw_cell(*start, 'green')
draw_cell(*goal, 'red')
screen.update()

# DFS
stack = [start]
came_from = {start: None}
found = False

while stack:
    current = stack.pop()
    if current == goal:
        found = True
        break
    x, y = current
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            if not grid[ny][nx] and (nx, ny) not in came_from:
                came_from[(nx, ny)] = current
                stack.append((nx, ny))
                # animation
                draw_cell(nx, ny, "light blue")
                screen.update()
                time.sleep(DELAY)

# Reconstruct the path
if found:
    cur = goal
    while cur:
        draw_cell(*cur, "yellow")
        cur = came_from[cur]
        screen.update()
        time.sleep(DELAY)

else:
    t.goto(0, 0)
    t.write("No path found!", align="center", font=("Arial", 16, "bold"))

screen.exitonclick()