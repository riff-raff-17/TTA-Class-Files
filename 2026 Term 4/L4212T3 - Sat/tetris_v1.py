import arcade

# --- board ---
COLS = 10
ROWS = 20
CELL = 30
BOARD_LEFT = 40
BOARD_BOTTOM = 40
BOARD_WIDTH = COLS * CELL
BOARD_HEIGHT = ROWS * CELL

PANEL_X = BOARD_LEFT + BOARD_WIDTH + 30
SCREEN_WIDTH = BOARD_LEFT + BOARD_WIDTH + 250
SCREEN_HEIGHT = BOARD_BOTTOM + BOARD_HEIGHT + 40
TITLE = "Betris"

BOARD_COLOR = (20, 24, 32)
GRID_LINE_COLOR = (44, 50, 64)


def make_grid():
    return [[None] * COLS for _ in range(ROWS)]


def cell_rect(col, row):
    x = BOARD_LEFT + col * CELL
    y = BOARD_BOTTOM + row * CELL
    # Shrink by one pixel on each side so the grid lines show between blocks.
    return arcade.LBWH(x + 1, y + 1, CELL - 2, CELL - 2)


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.background_color = arcade.color.DARK_SLATE_GRAY
        self.grid = make_grid()

        self.grid[0][0] = (230, 50, 60)  # bottom-left
        self.grid[0][COLS - 1] = (50, 100, 240)  # bottom-right
        self.grid[ROWS - 1][0] = (60, 210, 70)  # top-left
        self.grid[1][4] = (240, 210, 0)  # col 4, row 1 - just above the floor

        def on_key_press(self, symbol, modifiers):
            if symbol == arcade.key.ESCAPE:
                self.close()

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

    def on_draw(self):
        self.clear()
        self._draw_board()
        self._draw_locked()

        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_outline(board, arcade.color.LIGHT_GRAY, border_width=2)


window = Tetris()
arcade.run()
