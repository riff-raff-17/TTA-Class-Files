import matplotlib.pyplot as plt
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Create a grid represented as a matrix (1 for walkable, 0 for obstacle)
matrix = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Intialize the grid and define start/end points
grid = Grid(matrix=matrix)
start = grid.node(0, 0)
end = grid.node(9, 9)

# Instantiate the A* finder
finder = AStarFinder()

# Find the path along with some statistics
path, runs = finder.find_path(start, end, grid)
print("Path found:", path)
print("Number of runs:", runs)