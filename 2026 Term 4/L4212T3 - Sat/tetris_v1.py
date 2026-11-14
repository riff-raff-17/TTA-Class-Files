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
BOARD_HEIGHT = ROWS * CELL

PANEL_X = BOARD_LEFT + BOARD_WIDTH + 30
SCREEN_WIDTH = BOARD_LEFT + BOARD_WIDTH + 250
SCREEN_HEIGHT = BOARD_BOTTOM + BOARD_HEIGHT + 40
TITLE = "Tetris"

BOARD_COLOR = (20, 24, 32)
GRID_LINE_COLOR = (44, 50, 64)

# ----- gravity and levels -----
BASE_FALL_EVERY = 0.6  # seconds per row at level 1
FALL_STEP_PER_LEVEL = 0.05  # each level is this much faster...
MIN_FALL_EVERY = 0.08  # ...but never faster than this (Part 2, Section 14)
SOFT_DROP_EVERY = 0.04
LINES_PER_LEVEL = 10

# ----- holding left/right (auto-shift) -----
AUTO_SHIFT_DELAY = 0.17  # hold this long before the piece starts sliding
AUTO_SHIFT_REPEAT = 0.05  # then move one column this often

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

# ----- scoring -----
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}  # multiplied by the level
SOFT_DROP_POINTS = 1
HARD_DROP_POINTS = 2

# ----- preview and sound -----
PREVIEW_CELL = 22
VOLUME = 0.35

HELP_LINES = [
    "Left/Right:  move (hold)",
    "Up:  rotate",
    "Down:  soft drop",
    "Space:  hard drop",
    "P pause   M mute   R restart",
]


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
    return [(r, -c) for c, r in cells]


def clear_full_rows(grid):
    kept = [row for row in grid if None in row]
    cleared = ROWS - len(kept)
    for _ in range(cleared):
        kept.append([None] * COLS)
    return kept, cleared


def load_sound_safely(path):
    """Part 2, Section 14: one bad file costs one sound, never the game."""
    try:
        return arcade.load_sound(path)
    except Exception as error:
        print(f"could not load {path}: {error}")
        return None


# ---------------------------------------------------------------- drawing helpers


def cell_rect(col, row):
    x = BOARD_LEFT + col * CELL
    y = BOARD_BOTTOM + row * CELL
    return arcade.LBWH(x + 1, y + 1, CELL - 2, CELL - 2)


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.background_color = arcade.color.DARK_SLATE_GRAY

        # ---------- things that outlive a round ----------
        self.best_score = 0  # NOT reset by _reset()
        self.muted = False

        self.snd_lock = load_sound_safely(":resources:sounds/hit1.wav")
        self.snd_clear = load_sound_safely(":resources:sounds/upgrade1.wav")
        self.snd_tetris = load_sound_safely(":resources:sounds/upgrade5.wav")
        self.snd_over = load_sound_safely(":resources:sounds/gameover1.wav")

        top = SCREEN_HEIGHT
        self.t_score_label = arcade.Text(
            "SCORE", PANEL_X, top - 60, arcade.color.LIGHT_GRAY, 13
        )
        self.t_score = arcade.Text("", PANEL_X, top - 96, arcade.color.WHITE, 28)
        self.t_best = arcade.Text("", PANEL_X, top - 122, arcade.color.LIGHT_GRAY, 13)
        self.t_level = arcade.Text("", PANEL_X, top - 160, arcade.color.WHITE, 16)
        self.t_lines = arcade.Text("", PANEL_X, top - 186, arcade.color.WHITE, 16)
        self.t_clear = arcade.Text("", PANEL_X, top - 216, arcade.color.GOLD, 14)
        self.t_next = arcade.Text(
            "NEXT", PANEL_X, top - 260, arcade.color.LIGHT_GRAY, 13
        )
        self.help_texts = [
            arcade.Text(line, PANEL_X, 140 - i * 24, arcade.color.LIGHT_GRAY, 12)
            for i, line in enumerate(HELP_LINES)
        ]

        mid_x = BOARD_LEFT + BOARD_WIDTH / 2
        mid_y = BOARD_BOTTOM + BOARD_HEIGHT / 2
        self.t_big = arcade.Text(
            "", mid_x, mid_y + 40, arcade.color.WHITE, 30, anchor_x="center"
        )
        self.t_mid = arcade.Text(
            "", mid_x, mid_y, arcade.color.GOLD, 18, anchor_x="center"
        )
        self.t_small = arcade.Text(
            "", mid_x, mid_y - 30, arcade.color.LIGHT_GRAY, 14, anchor_x="center"
        )
        self.t_hint = arcade.Text(
            "", mid_x, mid_y - 70, arcade.color.LIGHT_GRAY, 14, anchor_x="center"
        )

        self._reset()

    # ------------------------------------------------ state

    def _reset(self):
        """Everything that defines one round. Called by __init__ AND by the R key."""
        self.grid = make_grid()
        self.score = 0
        self.lines = 0
        self.clear_message = ""

        self.fall_timer = 0.0
        self.paused = False
        self.game_over = False

        # held keys (Part 2, Section 10) - a restart must clear these too
        self.left_down = False
        self.right_down = False
        self.soft_drop = False
        self.shift_timer = 0.0

        self.bag = []
        self.next_kind = self._next_from_bag()
        self._spawn_piece()

    @property
    def level(self):
        return 1 + self.lines // LINES_PER_LEVEL

    @property
    def fall_every(self):
        """Faster every level, but never past the floor."""
        return max(
            MIN_FALL_EVERY, BASE_FALL_EVERY - FALL_STEP_PER_LEVEL * (self.level - 1)
        )

    def _play(self, sound):
        if self.muted or sound is None:
            return
        arcade.play_sound(sound, volume=VOLUME)

    # ------------------------------------------------ pieces

    def _next_from_bag(self):
        """The 7-bag: every piece once, in a shuffled order, then a fresh bag."""
        if not self.bag:  # empty list is falsy (Part 1, Section 5)
            self.bag = list(SHAPES)
            random.shuffle(self.bag)  # shuffles IN PLACE, returns None
        return self.bag.pop()

    def _spawn_piece(self):
        self.piece_kind = self.next_kind
        self.next_kind = self._next_from_bag()
        self.piece_cells = SHAPES[self.piece_kind]
        self.piece_col = SPAWN_COL
        self.piece_row = SPAWN_ROW
        self.fall_timer = 0.0

        if not fits(self.grid, self.piece_cells, self.piece_col, self.piece_row):
            self._end_game()

    def _end_game(self):
        self.game_over = True
        self.best_score = max(self.best_score, self.score)
        self._play(self.snd_over)

    def _lock_piece(self):
        color = COLORS[self.piece_kind]
        for col, row in piece_blocks(self.piece_cells, self.piece_col, self.piece_row):
            self.grid[row][col] = color

        level_before = self.level
        self.grid, cleared = clear_full_rows(self.grid)
        if cleared > 0:
            points = LINE_SCORES[cleared] * level_before
            self.score += points
            self.lines += cleared
            if cleared == 4:
                self.clear_message = f"TETRIS! +{points:,}"
                self._play(self.snd_tetris)
            else:
                self.clear_message = (
                    f"{cleared} line{'s' if cleared > 1 else ''}  +{points:,}"
                )
                self._play(self.snd_clear)
            if self.level > level_before:
                self.clear_message = f"LEVEL {self.level}!"
        else:
            self._play(self.snd_lock)

        self._spawn_piece()

    def _try_move(self, d_col, d_row):
        new_col = self.piece_col + d_col
        new_row = self.piece_row + d_row
        if fits(self.grid, self.piece_cells, new_col, new_row):
            self.piece_col = new_col
            self.piece_row = new_row
            return True
        return False

    def _try_rotate(self):
        if self.piece_kind == "O":
            return False
        rotated = rotate_cw(self.piece_cells)
        for kick in KICKS:
            if fits(self.grid, rotated, self.piece_col + kick, self.piece_row):
                self.piece_cells = rotated
                self.piece_col += kick
                return True
        return False

    def _step_down(self):
        if self._try_move(0, -1):
            if self.soft_drop:
                self.score += SOFT_DROP_POINTS
        else:
            self._lock_piece()

    def _hard_drop(self):
        rows = 0
        while fits(self.grid, self.piece_cells, self.piece_col, self.piece_row - 1):
            self.piece_row -= 1
            rows += 1
        self.score += rows * HARD_DROP_POINTS
        self._lock_piece()

    # ------------------------------------------------ input

    def on_key_press(self, symbol, modifiers):
        # Always available - above the guard on purpose (Part 2, Section 13).
        if symbol == arcade.key.R:
            self._reset()
            return
        if symbol == arcade.key.M:
            self.muted = not self.muted
            return
        if symbol == arcade.key.P and not self.game_over:
            self.paused = not self.paused
            return
        if symbol == arcade.key.ESCAPE:
            self.close()
            return

        if self.game_over or self.paused:
            return

        # Left/right: move once NOW, then on_update takes over if the key stays down.
        # The "not self.left_down" check ignores key-repeat presses from the OS.
        if symbol in (arcade.key.LEFT, arcade.key.A) and not self.left_down:
            self.left_down = True
            self.shift_timer = 0.0
            self._try_move(-1, 0)
        elif symbol in (arcade.key.RIGHT, arcade.key.D) and not self.right_down:
            self.right_down = True
            self.shift_timer = 0.0
            self._try_move(1, 0)
        elif symbol in (arcade.key.UP, arcade.key.W):
            self._try_rotate()
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.soft_drop = True
        elif symbol == arcade.key.SPACE:
            self._hard_drop()

    def on_key_release(self, symbol, modifiers):
        # NO guard. A release is a fact about the keyboard. (Part 2, Section 13)
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.left_down = False
        if symbol in (arcade.key.RIGHT, arcade.key.D):
            self.right_down = False
        if symbol in (arcade.key.DOWN, arcade.key.S):
            self.soft_drop = False

    # ------------------------------------------------ update

    def _auto_shift(self, delta_time):
        """Holding a direction: wait AUTO_SHIFT_DELAY, then step every AUTO_SHIFT_REPEAT."""
        direction = (1 if self.right_down else 0) - (1 if self.left_down else 0)
        if direction == 0:
            self.shift_timer = 0.0
            return
        self.shift_timer += delta_time
        if self.shift_timer >= AUTO_SHIFT_DELAY:
            self.shift_timer -= AUTO_SHIFT_REPEAT  # an accumulator with a head start
            self._try_move(direction, 0)

    def on_update(self, delta_time):
        if self.game_over or self.paused:
            return

        self._auto_shift(delta_time)

        interval = (
            min(SOFT_DROP_EVERY, self.fall_every) if self.soft_drop else self.fall_every
        )
        self.fall_timer += delta_time
        if self.fall_timer >= interval:
            self.fall_timer -= interval
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

    def _draw_preview(self):
        """Draw next_kind centered in a box, using its offsets - no grid involved."""
        box = arcade.LBWH(PANEL_X, SCREEN_HEIGHT - 360, 120, 84)
        arcade.draw_rect_filled(box, BOARD_COLOR)
        arcade.draw_rect_outline(box, arcade.color.LIGHT_GRAY, border_width=1)

        cells = SHAPES[self.next_kind]
        min_c = min(c for c, r in cells)
        max_c = max(c for c, r in cells)
        min_r = min(r for c, r in cells)
        max_r = max(r for c, r in cells)
        width = (max_c - min_c + 1) * PREVIEW_CELL
        height = (max_r - min_r + 1) * PREVIEW_CELL
        left = box.center_x - width / 2
        bottom = box.center_y - height / 2

        for c, r in cells:
            x = left + (c - min_c) * PREVIEW_CELL
            y = bottom + (r - min_r) * PREVIEW_CELL
            rect = arcade.LBWH(x + 1, y + 1, PREVIEW_CELL - 2, PREVIEW_CELL - 2)
            arcade.draw_rect_filled(rect, COLORS[self.next_kind])

    def _draw_panel(self):
        self.t_score.value = f"{self.score:,}"
        self.t_best.value = f"best this session: {self.best_score:,}"
        self.t_level.value = f"level {self.level}"
        self.t_lines.value = f"lines {self.lines}"
        self.t_clear.value = self.clear_message + ("   (muted)" if self.muted else "")
        for text in (
            self.t_score_label,
            self.t_score,
            self.t_best,
            self.t_level,
            self.t_lines,
            self.t_clear,
            self.t_next,
        ):
            text.draw()
        self._draw_preview()
        for text in self.help_texts:
            text.draw()

    def _draw_overlay(self, big, mid, small, hint):
        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_filled(board, (0, 0, 0, 170))
        self.t_big.value = big
        self.t_mid.value = mid
        self.t_small.value = small
        self.t_hint.value = hint
        for text in (self.t_big, self.t_mid, self.t_small, self.t_hint):
            text.draw()

    def on_draw(self):
        self.clear()
        self._draw_board()
        self._draw_locked()
        if not self.game_over:
            self._draw_piece()

        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_outline(board, arcade.color.LIGHT_GRAY, border_width=2)
        self._draw_panel()

        if self.game_over:
            self._draw_overlay(
                "GAME OVER",
                f"{self.score:,} points",
                f"{self.lines} lines - level {self.level}",
                "press R to play again",
            )
        elif self.paused:
            self._draw_overlay("PAUSED", "", "", "press P to continue")


window = Tetris()
arcade.run()
