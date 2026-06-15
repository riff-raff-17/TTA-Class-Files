import pygame
import numpy as np
import sys

# --- Colors ---
BG = (10, 10, 18)
GRID_LINE = (25, 25, 40)
CELL_LIVE = (80, 220, 180)
UI_BAR = (16, 15, 28)
UI_TEXT = (160, 200, 190)
UI_ACCENT = (80, 220, 180)
UI_DIM = (60, 70, 80)

# --- Constants ---
WINDOW_W, WINDOW_H = 1100, 720
UI_BAR_H = 48
GRID_W, GRID_H = 400, 300
INITIAL_CELL_SIZE = 12.0
MIN_CELL = 2.0
MAX_CELL = 64.0
ZOOM_FACTOR = 1.15  # multiply/divide per scroll tick
FPS_CAP = 120
INITIAL_SPEED = 10  # generations per second

# --- simulation ---
def make_grid():
    return np.zeroes((GRID_H, GRID_W), dtype=np.uint8)

def randomize(grid):
    grid[:] = np.random.choice([0, 1], size=grid.shape, p=[0.65, 0.35])

def step(grid):
    top = np.roll(grid, -1, axis=0)
    bottom = np.roll(grid, 1, axis=0)
    neighbors = (
        np.roll(top, -1, axis=1) + top
        + np.roll(top, 1, axis=1)
        + np.roll(grid, -1, axis=1)
        + np.roll(grid, 1, axis=1)
        + np.roll(bottom, -1, axis=1) + bottom
        + np.roll(bottom, 1, axis=1)
    )
    born = (grid == 0) & (neighbors == 3)
    survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
    return (born | survive).astype(np.uint8)

# --- coordinate helpers ---
def screen_to_cell(sx, sy, pan_x, pan_y, cell_size):
    """Convert screen pixel to grid cell (float, for precise hits)."""
    cx = (sx - pan_x) / cell_size
    cy = (sy - UI_BAR_H - pan_y) / cell_size
    return cx, cy

def cell_to_screen(cx, cy, pan_x, pan_y, cell_size):
    sx = pan_x + cx * cell_size
    sy = UI_BAR_H + pan_y + cy * cell_size
    return sx, sy

# --- drawing ---
def draw_world(surface, grid, pan_x, pan_y, cell_size, view_w, view_h):
    surface.fill(BG)

    cs = cell_size
    # Visible cell range (with 1-cell margin)
    col0 = max(0, int(-pan_x / cs) - 1)
    row0 = max(0, int(-pan_y / cs) - 1)
    col1  = min(GRID_W, int((view_w - pan_x) / cs) + 2)
    row1  = min(GRID_H, int((view_h - pan_y) / cs) + 2)

    # Grid lines when zoomed in enough
    if cs >= 6:
        for cx in range(col0, col1 + 1):
            px = int(pan_x + cx * cs)
            pygame.draw.line(surface, GRID_LINE, (px, 0), (px, view_h))
        for cy in range(row0, row1 + 1):
            py = int(pan_y + cy * cs)
            pygame.draw.line(surface, GRID_LINE, (0, py), (view_w, py))

    # Live cells (only the visible slice)
    sub = grid[row0:row1, col0:col1]
    ys, xs = np.where(sub == 1)
    br = max(1, int(cs // 5))
    for ry, rx in zip(ys, xs):
        gx = col0 + rx
        gy = row0 + ry
        px = int(pan_x + gx * cs) + 1
        py = int(pan_y + gy * cs) + 1
        w = max(1, int(cs) - 1)
        pygame.draw.rect(
            surface, CELL_LIVE, pygame.Rect(px, py, w, w), border_radius=br
        )

def draw_ui(
        surface, font, small_font, paused, speed, 
        generation, population, cell_size, w
):
    pygame.draw.rect(surface, UI_BAR, (0, 0, w, UI_BAR_H))
    pygame.draw.line(surface, UI_ACCENT, (0, UI_BAR_H - 1), (w, UI_BAR_H - 1), 1)

    surface.blit(font.render("GAME OF LIFE", True, UI_ACCENT), (16, 12))