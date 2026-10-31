import random

import arcade

# ----- board -----
COLS = 10
ROWS = 20
CELL = 30
BOARD_LEFT = 40
BOARD_BOTTOM = 40
BOARD_WIDTH = COLS * CELL
BOARD_HEIGHT = ROWS * CELL

SCREEN_WIDTH = BOARD_LEFT + BOARD_WIDTH + 250
SCREEN_HEIGHT = BOARD_BOTTOM + BOARD_HEIGHT + 40
TITLE = "Tetris"

BOARD_COLOR = (20, 24, 32)
GRID_LINE_COLOR = (44, 50, 64)

# ----- gravity -----
BASE_FALL_EVERY = 0.6  # seconds per row (levels will speed this up later)
SOFT_DROP_EVERY = 0.04 

# ----- pieces -----
SPAWN_COL = COLS // 2 - 1
SPAWN_ROW = ROWS - 2
KICKS = [0, -1, 1, -2, 2]

SHAPES = {
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "S": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "Z": [(-1, 1), (0, 1), (0, 0), (1, 0)],
    "J": [(-1, 1), (-1, 0), (0, 0), (1, 0)],
    "L": [(-1, 0), (0, 0), (1, 0), (1, 1)],
}
COLORS = {
    "I": (0, 220, 230),
    "O": (240, 210, 0),
    "T": (170, 70, 240),
    "S": (60, 210, 70),
    "Z": (230, 50, 60),
    "J": (50, 100, 240),
    "L": (245, 150, 30),
}


# ---------------------------------------------------------------- pure logic


def make_grid():
    return [[None] * COLS for _ in range(ROWS)]


def piece_blocks(cells, col, row):
    return [(col + c, row + r) for c, r in cells]


def fits(grid, cells, col, row):
    for x, y in piece_blocks(cells, col, row):
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return False
        if grid[y][x] is not None:
            return False
    return True

def rotate_cw(cells):
    """(c, r) -> (r, -c): a quarter turn clockwise around the (0, 0) cell."""
    return [(r, -c) for c, r in cells]


# ---------------------------------------------------------------- drawing helpers


def cell_rect(col, row):
    x = BOARD_LEFT + col * CELL
    y = BOARD_BOTTOM + row * CELL
    return arcade.LBWH(x + 1, y + 1, CELL - 2, CELL - 2)


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.background_color = arcade.color.DARK_SLATE_GRAY

        self.grid = make_grid()
        self.fall_timer = 0.0
        self.game_over = False
        self.soft_drop = False  # True while Down is held
        self._spawn_piece()

    # ------------------------------------------------ pieces

    def _spawn_piece(self):
        self.piece_kind = random.choice(list(SHAPES))
        self.piece_cells = SHAPES[self.piece_kind]
        self.piece_col = SPAWN_COL
        self.piece_row = SPAWN_ROW
        self.fall_timer = 0.0

        if not fits(self.grid, self.piece_cells, self.piece_col, self.piece_row):
            self.game_over = True
            print("Game over. Press Esc to close.")

    def _lock_piece(self):
        color = COLORS[self.piece_kind]
        for col, row in piece_blocks(self.piece_cells, self.piece_col, self.piece_row):
            self.grid[row][col] = color
        self._spawn_piece()

    def _try_move(self, d_col, d_row):
        new_col = self.piece_col + d_col
        new_row = self.piece_row + d_row
        if fits(self.grid, self.piece_cells, new_col, new_row):
            self.piece_col = new_col
            self.piece_row = new_row
            return True
        return False

    def _step_down(self):
        if not self._try_move(0, -1):
            self._lock_piece()

    # ------------------------------------------------ input

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()

    # ------------------------------------------------ update

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.fall_timer += delta_time
        if self.fall_timer >= BASE_FALL_EVERY:
            self.fall_timer -= BASE_FALL_EVERY
            self._step_down()

    # ------------------------------------------------ drawing

    def _draw_board(self):
        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_filled(board, BOARD_COLOR)
        for col in range(1, COLS):
            x = BOARD_LEFT + col * CELL
            arcade.draw_line(
                x,
                BOARD_BOTTOM,
                x,
                BOARD_BOTTOM + BOARD_HEIGHT,
                GRID_LINE_COLOR,
                line_width=1,
            )
        for row in range(1, ROWS):
            y = BOARD_BOTTOM + row * CELL
            arcade.draw_line(
                BOARD_LEFT,
                y,
                BOARD_LEFT + BOARD_WIDTH,
                y,
                GRID_LINE_COLOR,
                line_width=1,
            )

    def _draw_locked(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = self.grid[row][col]
                if color is not None:
                    arcade.draw_rect_filled(cell_rect(col, row), color)

    def _draw_piece(self):
        color = COLORS[self.piece_kind]
        for col, row in piece_blocks(self.piece_cells, self.piece_col, self.piece_row):
            arcade.draw_rect_filled(cell_rect(col, row), color)

    def on_draw(self):
        self.clear()
        self._draw_board()
        self._draw_locked()
        if not self.game_over:
            self._draw_piece()

        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_outline(board, arcade.color.LIGHT_GRAY, border_width=2)


window = Tetris()
arcade.run()
