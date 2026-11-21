"""
Tetris

How to customise:
  1. Pick who is playing in section 1 (or run:  python milestone_7.py sam).
  2. Each player has a profile in section 2 that lists ONLY what is different
     from DEFAULTS (section 3). Copy a profile to make a new player.
  3. Themes, difficulties, key layouts and sound packs (section 4) are named
     bundles a profile picks by name - then tweaks single values if it wants.

A typo in a profile stops the game with a message saying what is wrong
(and usually what you meant), instead of a crash halfway through a round.
"""

import difflib
import random
import sys

import arcade

# =============================================================================
#  1. WHO IS PLAYING?
# =============================================================================
PLAYER = "default"

if __name__ == "__main__" and len(sys.argv) > 1:  # python milestone_7.py sam
    PLAYER = sys.argv[1]


# =============================================================================
#  2. PLAYER PROFILES - list only what is DIFFERENT from DEFAULTS (section 3)
# =============================================================================
PROFILES = {
    # The original game.
    "default": {},
    # Alex: neon and fast, sees three pieces ahead.
    "alex": {
        "name": "Alex",
        "theme": "neon",
        "block_style": "outline",
        "ghost_style": "fill",
        "difficulty": "speedrun",
        "next_count": 3,
        "sound_pack": "arcade",
        "messages": {
            "big_clear": "MEGA CLEAR!",
            "level_up": "WARP {level}!",
            "game_over": "SYSTEM CRASH",
        },
    },
    # Sam: soft colours, relaxed speed, WASD, a smaller board, no S or Z pieces.
    "sam": {
        "name": "Sam",
        "theme": "pastel",
        "block_style": "rounded",
        "show_grid": False,
        "difficulty": "chill",
        "keymap": "wasd",
        "board": {"cols": 8, "rows": 16, "cell": 34},
        "remove_pieces": ["S", "Z"],
        "sound_pack": "soft",
        "messages": {
            "big_clear": "WOW!",
            "game_over": "Nice try!",
            "paused": "Break time",
        },
    },
    # Jordan: retro green screen, wide board, two bonus pieces, no hold.
    "jordan": {
        "name": "Jordan",
        "title": "JORDAN-OS v1.0",
        "theme": "retro",
        "block_style": "beveled",
        "board": {"cols": 12, "rows": 22, "cell": 26},
        "hold": False,
        "next_count": 2,
        "randomizer": "random",
        "keymap": "arrows",
        "keys": {"hard_drop": ["SPACE", "ENTER"]},
        "handling": {"auto_shift_delay": 0.12},
        "line_scores": {4: 1200},
        "extra_pieces": {
            # cells are (column, row) around the point the piece rotates about
            "+": {
                "cells": [(0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)],
                "color": (210, 255, 90),
            },
            "i": {"cells": [(-1, 0), (0, 0), (1, 0)], "color": (40, 140, 70)},
        },
    },
}


# =============================================================================
#  3. DEFAULTS - every setting there is. A profile can override any of them.
# =============================================================================
DEFAULTS = {
    # ----- who -----
    "name": "",  # shown above the score ("" = no name)
    "title": "{name}'s Tetris",  # window title; {name} becomes the name
    # ----- look -----
    "theme": "classic",  # a name from THEMES
    "colors": {},  # change single theme colours, e.g. {"board": (0, 0, 0)}
    #   or pieces: {"pieces": {"T": (255, 0, 255)}}
    "block_style": "flat",  # flat / beveled / outline / rounded / gem
    "ghost_style": "outline",  # outline / fill / off
    "show_grid": True,
    # ----- words -----
    "messages": {
        "big_clear": "TETRIS!",  # 4 or more lines at once
        "level_up": "LEVEL {level}!",
        "game_over": "GAME OVER",
        "paused": "PAUSED",
    },
    # ----- sound -----
    "sound_pack": "classic",  # a name from SOUND_PACKS
    "sounds": {},  # change single sounds, e.g. {"lock": ":resources:sounds/coin1.wav"}
    #   None = silent for that event
    "volume": 0.35,  # 0.0 to 1.0
    # ----- controls -----
    "keymap": "classic",  # a name from KEYMAPS
    "keys": {},  # change single actions, e.g. {"hold": ["LSHIFT", "C"]}
    #   the FIRST key listed is the one the help text shows
    # ----- speed and handling -----
    "difficulty": "classic",  # a name from DIFFICULTIES
    "handling": {},  # change single values, e.g. {"auto_shift_delay": 0.12}
    "start_level": 1,
    # ----- rules -----
    "hold": True,  # False = no hold box, hold key does nothing
    "next_count": 1,  # how many upcoming pieces to show: 0 to 3
    "randomizer": "bag",  # bag = each piece once per round of 7 / random = anything goes
    "line_scores": {1: 100, 2: 300, 3: 500, 4: 800},  # multiplied by the level
    "soft_drop_points": 1,
    "hard_drop_points": 2,
    # ----- board and pieces -----
    "board": {"cols": 10, "rows": 20, "cell": 30},  # cell = pixels per square
    "remove_pieces": [],  # e.g. ["S", "Z"]
    "extra_pieces": {},  # see the "jordan" profile for the format
}


# =============================================================================
#  4. PRESETS - named bundles a profile picks by name
# =============================================================================
THEMES = {
    "classic": {
        "background": (47, 79, 79),  # around the board
        "board": (20, 24, 32),
        "grid": (44, 50, 64),
        "border": (211, 211, 211),
        "text": (255, 255, 255),
        "text_dim": (211, 211, 211),
        "accent": (255, 215, 0),  # clear messages and the player's name
        "overlay": (0, 0, 0, 170),  # darkens the board on pause / game over
        "pieces": {
            "I": (0, 220, 230),
            "O": (240, 210, 0),
            "T": (170, 70, 240),
            "S": (60, 210, 70),
            "Z": (230, 50, 60),
            "J": (50, 100, 240),
            "L": (245, 150, 30),
        },
    },
    "neon": {
        "background": (12, 4, 24),
        "board": (6, 6, 16),
        "grid": (36, 22, 60),
        "border": (255, 40, 200),
        "text": (245, 240, 255),
        "text_dim": (160, 150, 210),
        "accent": (0, 255, 210),
        "overlay": (0, 0, 0, 180),
        "pieces": {
            "I": (0, 255, 255),
            "O": (255, 255, 0),
            "T": (255, 0, 255),
            "S": (57, 255, 20),
            "Z": (255, 20, 80),
            "J": (30, 144, 255),
            "L": (255, 140, 0),
        },
    },
    "pastel": {
        "background": (236, 226, 244),
        "board": (255, 251, 246),
        "grid": (238, 228, 232),
        "border": (190, 170, 205),
        "text": (80, 60, 100),
        "text_dim": (125, 110, 145),
        "accent": (220, 90, 140),
        "overlay": (255, 255, 255, 190),
        "pieces": {
            "I": (140, 215, 230),
            "O": (250, 225, 140),
            "T": (200, 165, 235),
            "S": (165, 220, 165),
            "Z": (245, 165, 165),
            "J": (155, 175, 240),
            "L": (245, 195, 145),
        },
    },
    "retro": {
        "background": (8, 16, 8),
        "board": (0, 0, 0),
        "grid": (0, 40, 0),
        "border": (60, 200, 60),
        "text": (140, 255, 140),
        "text_dim": (70, 170, 70),
        "accent": (200, 255, 120),
        "overlay": (0, 0, 0, 190),
        "pieces": {
            "I": (120, 255, 120),
            "O": (180, 255, 100),
            "T": (60, 200, 90),
            "S": (100, 230, 170),
            "Z": (40, 170, 60),
            "J": (150, 210, 120),
            "L": (90, 255, 200),
        },
    },
    "mono": {
        "background": (30, 30, 30),
        "board": (12, 12, 12),
        "grid": (40, 40, 40),
        "border": (200, 200, 200),
        "text": (240, 240, 240),
        "text_dim": (160, 160, 160),
        "accent": (255, 255, 255),
        "overlay": (0, 0, 0, 180),
        "pieces": {
            "I": (235, 235, 235),
            "O": (200, 200, 200),
            "T": (170, 170, 170),
            "S": (140, 140, 140),
            "Z": (115, 115, 115),
            "J": (215, 215, 215),
            "L": (185, 185, 185),
        },
    },
}

DIFFICULTIES = {
    # fall_every:          seconds per row at the first level
    # fall_step_per_level: each level is this much faster...
    # min_fall_every:      ...but never faster than this
    # auto_shift_delay:    hold left/right this long before the piece starts sliding
    # auto_shift_repeat:   then move one column this often
    "chill": {
        "fall_every": 0.9,
        "fall_step_per_level": 0.04,
        "min_fall_every": 0.15,
        "soft_drop_every": 0.05,
        "lines_per_level": 12,
        "auto_shift_delay": 0.22,
        "auto_shift_repeat": 0.07,
    },
    "classic": {
        "fall_every": 0.6,
        "fall_step_per_level": 0.05,
        "min_fall_every": 0.08,
        "soft_drop_every": 0.04,
        "lines_per_level": 10,
        "auto_shift_delay": 0.17,
        "auto_shift_repeat": 0.05,
    },
    "speedrun": {
        "fall_every": 0.4,
        "fall_step_per_level": 0.04,
        "min_fall_every": 0.04,
        "soft_drop_every": 0.02,
        "lines_per_level": 8,
        "auto_shift_delay": 0.11,
        "auto_shift_repeat": 0.03,
    },
}

# Key names are arcade.key names: LEFT, SPACE, A, LSHIFT, ENTER, ...
KEYMAPS = {
    "classic": {
        "left": ["LEFT", "A"],
        "right": ["RIGHT", "D"],
        "rotate": ["UP", "W"],
        "rotate_back": ["Z"],
        "hold": ["C"],
        "soft_drop": ["DOWN", "S"],
        "hard_drop": ["SPACE"],
        "pause": ["P"],
        "mute": ["M"],
        "restart": ["R"],
        "quit": ["ESCAPE"],
    },
    "wasd": {
        "left": ["A"],
        "right": ["D"],
        "rotate": ["W"],
        "rotate_back": ["Q"],
        "hold": ["E"],
        "soft_drop": ["S"],
        "hard_drop": ["SPACE"],
        "pause": ["P"],
        "mute": ["M"],
        "restart": ["BACKSPACE"],
        "quit": ["ESCAPE"],
    },
    "arrows": {
        "left": ["LEFT"],
        "right": ["RIGHT"],
        "rotate": ["UP", "X"],
        "rotate_back": ["Z"],
        "hold": ["C", "LSHIFT"],
        "soft_drop": ["DOWN"],
        "hard_drop": ["SPACE"],
        "pause": ["P"],
        "mute": ["M"],
        "restart": ["R"],
        "quit": ["ESCAPE"],
    },
}

SOUND_PACKS = {
    "classic": {
        "lock": ":resources:sounds/hit1.wav",
        "clear": ":resources:sounds/upgrade1.wav",
        "big_clear": ":resources:sounds/upgrade5.wav",
        "game_over": ":resources:sounds/gameover1.wav",
    },
    "arcade": {
        "lock": ":resources:sounds/hit3.wav",
        "clear": ":resources:sounds/coin2.wav",
        "big_clear": ":resources:sounds/coin5.wav",
        "game_over": ":resources:sounds/gameover3.wav",
    },
    "soft": {
        "lock": None,
        "clear": ":resources:sounds/coin1.wav",
        "big_clear": ":resources:sounds/upgrade2.wav",
        "game_over": ":resources:sounds/gameover2.wav",
    },
    "silent": {"lock": None, "clear": None, "big_clear": None, "game_over": None},
}

STANDARD_SHAPES = {
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "S": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "Z": [(-1, 1), (0, 1), (0, 0), (1, 0)],
    "J": [(-1, 1), (-1, 0), (0, 0), (1, 0)],
    "L": [(-1, 0), (0, 0), (1, 0), (1, 1)],
}

BLOCK_STYLES = ("flat", "beveled", "outline", "rounded", "gem")
GHOST_STYLES = ("outline", "fill", "off")
RANDOMIZERS = ("bag", "random")


# =============================================================================
#  Everything below is the game itself. You shouldn't need to edit below this
#  line to customise a player.
# =============================================================================

# ---------------------------------------------------------------- reading the profile

# Dicts whose keys are open-ended (anything goes), rather than a fixed list.
FREE_FORM = {
    "colors",
    "sounds",
    "keys",
    "handling",
    "pieces",
    "line_scores",
    "extra_pieces",
}


def _fail(message):
    """Stop with a readable message instead of a traceback."""
    raise SystemExit(f"\nProblem with profile '{PLAYER}': {message}\n")


def _choose(value, choices, what):
    """Return value if it is one of choices; otherwise stop and suggest the closest one."""
    if value in choices:
        return value
    names = [str(c) for c in choices]
    close = difflib.get_close_matches(str(value), names, n=1)
    hint = f" Did you mean '{close[0]}'?" if close else ""
    _fail(f"unknown {what} {value!r}.{hint} Options: {', '.join(names)}")


def _same_kind(value, example):
    if isinstance(example, bool):
        return isinstance(value, bool)
    if isinstance(example, (int, float)):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if isinstance(example, (list, tuple)):
        return isinstance(value, (list, tuple))
    return isinstance(value, type(example))


def _merge(base, changes, where, check_types=True):
    """A copy of base with changes laid over it. Nested dicts merge key by key.
    An unknown key is almost always a typo, so it stops the game (except in FREE_FORM dicts)."""
    if not isinstance(changes, dict):
        _fail(f"'{where}' should be a dict like {{...}}, got {changes!r}")
    result = dict(base)
    free = where.split(".")[-1] in FREE_FORM
    for key, value in changes.items():
        if key not in base:
            if not free:
                _choose(key, list(base), f"setting in '{where}':")
            result[key] = value
        elif isinstance(base[key], dict):
            result[key] = _merge(base[key], value, f"{where}.{key}", check_types)
        else:
            if (
                check_types
                and base[key] is not None
                and not _same_kind(value, base[key])
            ):
                _fail(f"'{where}.{key}' should look like {base[key]!r}, got {value!r}")
            result[key] = value
    return result


def _check_color(value, where):
    ok = (
        isinstance(value, (list, tuple))
        and len(value) in (3, 4)
        and all(isinstance(v, int) and 0 <= v <= 255 for v in value)
    )
    if not ok:
        _fail(f"{where} should be a colour like (255, 120, 0), got {value!r}")
    return tuple(value)


def _check_number(value, where, low, high=None, whole=False):
    if whole and not isinstance(value, int):
        _fail(f"{where} should be a whole number, got {value!r}")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        _fail(f"{where} should be a number, got {value!r}")
    if high is None and value < low:
        _fail(f"{where} should be at least {low}, got {value!r}")
    if high is not None and not low <= value <= high:
        _fail(f"{where} should be between {low} and {high}, got {value!r}")
    return value


def _normalized(cells):
    min_c = min(c for c, r in cells)
    min_r = min(r for c, r in cells)
    return sorted((c - min_c, r - min_r) for c, r in cells)


S = _merge(DEFAULTS, PROFILES[_choose(PLAYER, list(PROFILES), "player")], "profile")

# ----- who -----
PLAYER_NAME = S["name"]
TITLE = S["title"].replace("{name}", PLAYER_NAME) if PLAYER_NAME else "Tetris"

# ----- look -----
_choose(S["theme"], list(THEMES), "theme")
THEME = _merge(THEMES[S["theme"]], S["colors"], f"colors (theme '{S['theme']}')")
for _key in THEME:
    if _key != "pieces":
        THEME[_key] = _check_color(THEME[_key], f"colour '{_key}'")
BLOCK_STYLE = _choose(S["block_style"], BLOCK_STYLES, "block_style")
GHOST_STYLE = _choose(S["ghost_style"], GHOST_STYLES, "ghost_style")
SHOW_GRID = S["show_grid"]
MESSAGES = S["messages"]

# ----- sound -----
_choose(S["sound_pack"], list(SOUND_PACKS), "sound_pack")
SOUNDS = _merge(
    SOUND_PACKS[S["sound_pack"]],
    S["sounds"],
    f"sounds (sound pack '{S['sound_pack']}')",
    check_types=False,
)
for _event, _path in SOUNDS.items():
    if _path is not None and not isinstance(_path, str):
        _fail(f"sound '{_event}' should be a file path or None, got {_path!r}")
VOLUME = _check_number(S["volume"], "volume", 0, 1)

# ----- controls -----
_choose(S["keymap"], list(KEYMAPS), "keymap")
_key_names = _merge(
    KEYMAPS[S["keymap"]], S["keys"], f"keys (keymap '{S['keymap']}')", check_types=False
)
KEYS = {}  # action -> list of key names, e.g. "hold" -> ["C"]
KEY_TO_ACTION = {}  # arcade key code -> action
for _action, _names in _key_names.items():
    if isinstance(_names, str):
        _names = [_names]
    if not _names:
        _fail(f"action '{_action}' needs at least one key")
    KEYS[_action] = []
    for _name in _names:
        _code = getattr(arcade.key, str(_name).upper(), None)
        if not isinstance(_code, int):
            _fail(
                f"'{_name}' (for {_action}) is not an arcade key name - "
                f"try names like LEFT, SPACE, A, LSHIFT, ENTER"
            )
        if KEY_TO_ACTION.get(_code, _action) != _action:
            _fail(
                f"key {_name} is used for both '{KEY_TO_ACTION[_code]}' and '{_action}'"
            )
        KEY_TO_ACTION[_code] = _action
        KEYS[_action].append(str(_name).upper())

# ----- speed and handling -----
_choose(S["difficulty"], list(DIFFICULTIES), "difficulty")
_h = _merge(
    DIFFICULTIES[S["difficulty"]],
    S["handling"],
    f"handling (difficulty '{S['difficulty']}')",
)
for _key, _value in _h.items():
    _check_number(
        _value, f"handling '{_key}'", 0.001, whole=(_key == "lines_per_level")
    )
BASE_FALL_EVERY = _h["fall_every"]
FALL_STEP_PER_LEVEL = _h["fall_step_per_level"]
MIN_FALL_EVERY = _h["min_fall_every"]  # never faster than this (Part 2, Section 14)
SOFT_DROP_EVERY = _h["soft_drop_every"]
LINES_PER_LEVEL = _h["lines_per_level"]
AUTO_SHIFT_DELAY = _h["auto_shift_delay"]
AUTO_SHIFT_REPEAT = _h["auto_shift_repeat"]
START_LEVEL = _check_number(S["start_level"], "start_level", 1, whole=True)

# ----- rules -----
HOLD_ENABLED = S["hold"]
NEXT_COUNT = _check_number(S["next_count"], "next_count", 0, 3, whole=True)
RANDOMIZER = _choose(S["randomizer"], RANDOMIZERS, "randomizer")
LINE_SCORES = S["line_scores"]
for _lines, _points in LINE_SCORES.items():
    if not isinstance(_lines, int) or _lines < 1 or not isinstance(_points, int):
        _fail(
            f"line_scores should look like {{1: 100, 2: 300}}, got {_lines!r}: {_points!r}"
        )
SOFT_DROP_POINTS = S["soft_drop_points"]
HARD_DROP_POINTS = S["hard_drop_points"]

# ----- pieces -----
for _kind in S["remove_pieces"]:
    _choose(_kind, list(STANDARD_SHAPES), "piece in remove_pieces")
SHAPES = {k: list(v) for k, v in STANDARD_SHAPES.items() if k not in S["remove_pieces"]}
_extra_colors = {}
for _kind, _piece in S["extra_pieces"].items():
    if not isinstance(_piece, dict) or "cells" not in _piece:
        _fail(
            f"extra piece '{_kind}' should look like {{'cells': [(0, 0), (1, 0)], 'color': (255, 0, 0)}}"
        )
    for _key in _piece:
        _choose(_key, ["cells", "color"], f"setting in extra piece '{_kind}':")
    _cells = _piece["cells"]
    _ok = (
        isinstance(_cells, (list, tuple))
        and len(_cells) > 0
        and all(
            isinstance(c, (list, tuple))
            and len(c) == 2
            and all(isinstance(v, int) for v in c)
            for c in _cells
        )
    )
    if not _ok:
        _fail(
            f"cells of extra piece '{_kind}' should be (column, row) pairs like [(0, 0), (1, 0)]"
        )
    _cells = [tuple(c) for c in _cells]
    if len(set(_cells)) != len(_cells):
        _fail(f"extra piece '{_kind}' lists the same cell twice")
    SHAPES[_kind] = _cells
    if "color" in _piece:
        _extra_colors[_kind] = _check_color(
            _piece["color"], f"colour of extra piece '{_kind}'"
        )
if not SHAPES:
    _fail("every piece has been removed - there is nothing left to drop")

_piece_color_changes = S["colors"].get("pieces", {})
for _kind in _piece_color_changes:
    _choose(_kind, list(SHAPES), "piece in colors -> pieces")
COLORS = {}
for _kind in SHAPES:
    if _kind in _piece_color_changes:
        _color = _piece_color_changes[_kind]
    elif _kind in _extra_colors:
        _color = _extra_colors[_kind]
    else:
        _color = THEME["pieces"].get(_kind, THEME["accent"])
    COLORS[_kind] = _check_color(_color, f"colour of piece '{_kind}'")

# A piece that looks the same after a quarter turn (like O) would only wobble, so it doesn't turn.
NO_ROTATE = {
    k
    for k, cells in SHAPES.items()
    if _normalized([(r, -c) for c, r in cells]) == _normalized(cells)
}

# ----- board -----
_board = S["board"]
COLS = _check_number(_board["cols"], "board cols", 1, whole=True)
ROWS = _check_number(_board["rows"], "board rows", 1, whole=True)
CELL = _check_number(_board["cell"], "board cell", 12, whole=True)
_biggest = max(
    max(
        max(c for c, r in cells) - min(c for c, r in cells),
        max(r for c, r in cells) - min(r for c, r in cells),
    )
    + 1
    for cells in SHAPES.values()
)
if COLS < max(4, _biggest):
    _fail(
        f"board cols must be at least {max(4, _biggest)} for these pieces, got {COLS}"
    )
if ROWS < _biggest + 4:
    _fail(f"board rows must be at least {_biggest + 4} for these pieces, got {ROWS}")


# ---------------------------------------------------------------- layout (worked out from the settings)

BOARD_LEFT = 40
BOARD_WIDTH = COLS * CELL
BOARD_HEIGHT = ROWS * CELL
PANEL_X = BOARD_LEFT + BOARD_WIDTH + 30
PANEL_WIDTH = 210
SCREEN_WIDTH = BOARD_LEFT + BOARD_WIDTH + 250

PREVIEW_BOX = (120, 84)  # the first NEXT box, and the HOLD box
SMALL_PREVIEW_BOX = (120, 60)  # 2nd and 3rd NEXT boxes
PREVIEW_CELL = 22
SMALL_PREVIEW_CELL = 16


def _panel_layout():
    """Where things go in the side panel, in pixels DOWN from the top of the window.
    Each section starts below the last, so turning NEXT or HOLD off just closes the gap."""
    at = {
        "name": 30,
        "score_label": 60,
        "score": 96,
        "best": 122,
        "level": 160,
        "lines": 186,
        "clear": 216,
        "next_boxes": [],
    }
    y = 260
    if NEXT_COUNT:
        at["next_label"] = y
        y += 16
        for i in range(NEXT_COUNT):
            height = PREVIEW_BOX[1] if i == 0 else SMALL_PREVIEW_BOX[1]
            at["next_boxes"].append((y, height))  # (top, height)
            y += height + 8
        y += 22
    if HOLD_ENABLED:
        at["hold_label"] = y
        at["hold_box"] = (y + 16, PREVIEW_BOX[1])
        y += 16 + PREVIEW_BOX[1] + 30
    at["help"] = [y + i * 24 for i in range(len(HELP_LINES))]
    at["bottom"] = at["help"][-1] + 40
    return at


def key_label(action):
    """How the first key for an action is written in the help text."""
    name = KEYS[action][0]
    pretty = {
        "LEFT": "Left",
        "RIGHT": "Right",
        "UP": "Up",
        "DOWN": "Down",
        "SPACE": "Space",
        "ESCAPE": "Esc",
        "LSHIFT": "Shift",
        "RSHIFT": "Shift",
        "LCTRL": "Ctrl",
        "RCTRL": "Ctrl",
        "RETURN": "Enter",
        "ENTER": "Enter",
        "BACKSPACE": "Bksp",
    }
    return pretty.get(name, name if len(name) == 1 else name.title())


# Built from the key map, so the help can never disagree with the real keys.
HELP_LINES = [
    f"{key_label('left')}/{key_label('right')}:  move (hold)",
    f"{key_label('rotate')} / {key_label('rotate_back')}:  rotate / rotate back",
]
if HOLD_ENABLED:
    HELP_LINES.append(f"{key_label('hold')}:  hold")
HELP_LINES += [
    f"{key_label('soft_drop')}:  soft drop",
    f"{key_label('hard_drop')}:  hard drop",
    f"{key_label('pause')} pause   {key_label('mute')} mute   {key_label('restart')} restart",
]

PANEL = _panel_layout()
SCREEN_HEIGHT = max(BOARD_HEIGHT + 80, PANEL["bottom"])
BOARD_BOTTOM = (
    SCREEN_HEIGHT - BOARD_HEIGHT
) // 2  # centred if the panel is the taller one


def from_top(offset):
    return SCREEN_HEIGHT - offset


# ---------------------------------------------------------------- pure logic

KICKS = [0, -1, 1, -2, 2]  # sideways nudges to try when a rotation is blocked


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


def rotate_ccw(cells):
    """(c, r) -> (-r, c): the clockwise rule, run backwards."""
    return [(-r, c) for c, r in cells]


def clear_full_rows(grid):
    kept = [row for row in grid if None in row]
    cleared = ROWS - len(kept)
    for _ in range(cleared):
        kept.append([None] * COLS)
    return kept, cleared


def spawn_position(cells):
    """Middle of the top row, nudged so every piece starts fully on the board."""
    min_c = min(c for c, r in cells)
    max_c = max(c for c, r in cells)
    max_r = max(r for c, r in cells)
    col = min(max(COLS // 2 - 1, -min_c), COLS - 1 - max_c)
    row = min(ROWS - 2, ROWS - 1 - max_r)
    return col, row


def line_points(cleared):
    """Points for clearing this many lines at level 1. Beyond the table, scale the top entry."""
    if cleared in LINE_SCORES:
        return LINE_SCORES[cleared]
    top = max(LINE_SCORES)
    return LINE_SCORES[top] * cleared // top


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


def shade(color, amount):
    """amount > 0 mixes toward white, amount < 0 toward black. Alpha is kept."""
    r, g, b = color[:3]
    alpha = color[3] if len(color) > 3 else 255
    if amount >= 0:
        r, g, b = (int(v + (255 - v) * amount) for v in (r, g, b))
    else:
        r, g, b = (int(v * (1 + amount)) for v in (r, g, b))
    return (r, g, b, alpha)


def draw_block(left, bottom, size, color, style=None):
    """One square of a piece, in the player's block style.
    Only rectangles and circles: they are fast to draw, polygons are not."""
    style = style or BLOCK_STYLE
    x, y, s = left + 1, bottom + 1, size - 2
    alpha = color[3] if len(color) > 3 else 255
    if s < 8 or (style == "rounded" and alpha < 255):
        style = "flat"  # tiny previews, and see-through rounded blocks
    rect = arcade.LBWH(x, y, s, s)
    if style == "flat":
        arcade.draw_rect_filled(rect, color)
    elif style == "beveled":
        e = max(2, s / 6)
        light, dark = shade(color, 0.45), shade(color, -0.4)
        arcade.draw_rect_filled(rect, color)
        arcade.draw_rect_filled(arcade.LBWH(x, y + s - e, s, e), light)  # top
        arcade.draw_rect_filled(arcade.LBWH(x, y, e, s - e), light)  # left
        arcade.draw_rect_filled(arcade.LBWH(x + e, y, s - e, e), dark)  # bottom
        arcade.draw_rect_filled(
            arcade.LBWH(x + s - e, y + e, e, s - 2 * e), dark
        )  # right
    elif style == "outline":
        arcade.draw_rect_filled(rect, (*color[:3], alpha * 70 // 255))
        arcade.draw_rect_outline(rect, color, border_width=2)
    elif style == "rounded":
        rad = s / 4
        arcade.draw_rect_filled(arcade.LBWH(x + rad, y, s - 2 * rad, s), color)
        arcade.draw_rect_filled(arcade.LBWH(x, y + rad, s, s - 2 * rad), color)
        for cx in (x + rad, x + s - rad):
            for cy in (y + rad, y + s - rad):
                arcade.draw_circle_filled(cx, cy, rad, color)
    elif style == "gem":
        inset = s / 4
        arcade.draw_rect_filled(rect, shade(color, -0.25))
        arcade.draw_rect_filled(
            arcade.LBWH(x + inset, y + inset, s - 2 * inset, s - 2 * inset),
            shade(color, 0.35),
        )


class Tetris(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.background_color = THEME["background"]

        # ---------- things that outlive a round ----------
        self.best_score = 0  # NOT reset by _reset()
        self.muted = False

        self.sounds = {
            event: load_sound_safely(path) if path else None
            for event, path in SOUNDS.items()
        }

        text, dim, accent = THEME["text"], THEME["text_dim"], THEME["accent"]

        def panel_text(key, words, color, size):
            return arcade.Text(words, PANEL_X, from_top(PANEL[key]), color, size)

        self.t_name = panel_text("name", "", accent, 16)
        self._set_text(self.t_name, PLAYER_NAME, 16, PANEL_WIDTH)
        self.t_score_label = panel_text("score_label", "SCORE", dim, 13)
        self.t_score = panel_text("score", "", text, 28)
        self.t_best = panel_text("best", "", dim, 13)
        self.t_level = panel_text("level", "", text, 16)
        self.t_lines = panel_text("lines", "", text, 16)
        self.t_clear = panel_text("clear", "", accent, 14)
        self.panel_labels = [
            self.t_name,
            self.t_score_label,
            self.t_score,
            self.t_best,
            self.t_level,
            self.t_lines,
            self.t_clear,
        ]
        if NEXT_COUNT:
            self.panel_labels.append(panel_text("next_label", "NEXT", dim, 13))
        if HOLD_ENABLED:
            self.panel_labels.append(panel_text("hold_label", "HOLD", dim, 13))
        self.help_texts = []
        for line, y in zip(HELP_LINES, PANEL["help"]):
            help_text = arcade.Text("", PANEL_X, from_top(y), dim, 12)
            self._set_text(
                help_text, line, 12, PANEL_WIDTH
            )  # long key names shrink to fit
            self.help_texts.append(help_text)

        mid_x = BOARD_LEFT + BOARD_WIDTH / 2
        mid_y = BOARD_BOTTOM + BOARD_HEIGHT / 2
        self.t_big = arcade.Text("", mid_x, mid_y + 40, text, 30, anchor_x="center")
        self.t_mid = arcade.Text("", mid_x, mid_y, accent, 18, anchor_x="center")
        self.t_small = arcade.Text("", mid_x, mid_y - 30, dim, 14, anchor_x="center")
        self.t_hint = arcade.Text("", mid_x, mid_y - 70, dim, 14, anchor_x="center")

        self._reset()

    # ------------------------------------------------ state

    def _reset(self):
        """Everything that defines one round. Called by __init__ AND by the restart key."""
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

        self.hold_kind = None  # nothing held yet
        self.hold_used = False  # one hold per piece, or you could stall forever

        self.bag = []
        self.queue = [self._random_kind() for _ in range(max(1, NEXT_COUNT))]
        self._spawn_piece()

    @property
    def level(self):
        return START_LEVEL + self.lines // LINES_PER_LEVEL

    @property
    def fall_every(self):
        """Faster every level, but never past the floor."""
        return max(
            MIN_FALL_EVERY, BASE_FALL_EVERY - FALL_STEP_PER_LEVEL * (self.level - 1)
        )

    def _play(self, event):
        sound = self.sounds.get(event)
        if self.muted or sound is None:
            return
        arcade.play_sound(sound, volume=VOLUME)

    # ------------------------------------------------ pieces

    def _random_kind(self):
        if RANDOMIZER == "random":
            return random.choice(list(SHAPES))
        # The bag: every piece once, in a shuffled order, then a fresh bag.
        if not self.bag:  # empty list is falsy (Part 1, Section 5)
            self.bag = list(SHAPES)
            random.shuffle(self.bag)  # shuffles IN PLACE, returns None
        return self.bag.pop()

    def _spawn_piece(self, kind=None):
        if kind is None:
            kind = self.queue.pop(0)
            self.queue.append(self._random_kind())
        self.piece_kind = kind
        self.piece_cells = SHAPES[self.piece_kind]
        self.piece_col, self.piece_row = spawn_position(self.piece_cells)
        self.fall_timer = 0.0

        if not fits(self.grid, self.piece_cells, self.piece_col, self.piece_row):
            self._end_game()

    def _end_game(self):
        self.game_over = True
        self.best_score = max(self.best_score, self.score)
        self._play("game_over")

    def _lock_piece(self):
        color = COLORS[self.piece_kind]
        for col, row in piece_blocks(self.piece_cells, self.piece_col, self.piece_row):
            self.grid[row][col] = color

        level_before = self.level
        self.grid, cleared = clear_full_rows(self.grid)
        if cleared > 0:
            points = line_points(cleared) * level_before
            self.score += points
            self.lines += cleared
            if cleared >= 4:
                self.clear_message = f"{MESSAGES['big_clear']} +{points:,}"
                self._play("big_clear")
            else:
                self.clear_message = (
                    f"{cleared} line{'s' if cleared > 1 else ''}  +{points:,}"
                )
                self._play("clear")
            if self.level > level_before:
                self.clear_message = MESSAGES["level_up"].replace(
                    "{level}", str(self.level)
                )
        else:
            self._play("lock")

        self.hold_used = False  # a new piece may be held again
        self._spawn_piece()

    def _try_move(self, d_col, d_row):
        new_col = self.piece_col + d_col
        new_row = self.piece_row + d_row
        if fits(self.grid, self.piece_cells, new_col, new_row):
            self.piece_col = new_col
            self.piece_row = new_row
            return True
        return False

    def _hold(self):
        if not HOLD_ENABLED or self.hold_used:
            return
        held = self.hold_kind
        self.hold_kind = self.piece_kind
        self._spawn_piece(held)  # held is None the first time -> take the next piece
        self.hold_used = True

    def _ghost_row(self):
        """Where would the piece land? Exactly the hard-drop loop, without moving it."""
        row = self.piece_row
        while fits(self.grid, self.piece_cells, self.piece_col, row - 1):
            row -= 1
        return row

    def _try_rotate(self, clockwise=True):
        if self.piece_kind in NO_ROTATE:
            return False
        if clockwise:
            rotated = rotate_cw(self.piece_cells)
        else:
            rotated = rotate_ccw(self.piece_cells)
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
        action = KEY_TO_ACTION.get(symbol)
        if action is None:
            return

        # Always available - above the guard on purpose (Part 2, Section 13).
        if action == "restart":
            self._reset()
            return
        if action == "mute":
            self.muted = not self.muted
            return
        if action == "pause" and not self.game_over:
            self.paused = not self.paused
            return
        if action == "quit":
            self.close()
            return

        if self.game_over or self.paused:
            return

        # Left/right: move once NOW, then on_update takes over if the key stays down.
        # The "not self.left_down" check ignores key-repeat presses from the OS.
        if action == "left" and not self.left_down:
            self.left_down = True
            self.shift_timer = 0.0
            self._try_move(-1, 0)
        elif action == "right" and not self.right_down:
            self.right_down = True
            self.shift_timer = 0.0
            self._try_move(1, 0)
        elif action == "rotate":
            self._try_rotate()
        elif action == "rotate_back":
            self._try_rotate(clockwise=False)
        elif action == "hold":
            self._hold()
        elif action == "soft_drop":
            self.soft_drop = True
        elif action == "hard_drop":
            self._hard_drop()

    def on_key_release(self, symbol, modifiers):
        # NO guard. A release is a fact about the keyboard. (Part 2, Section 13)
        action = KEY_TO_ACTION.get(symbol)
        if action == "left":
            self.left_down = False
        elif action == "right":
            self.right_down = False
        elif action == "soft_drop":
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

    @staticmethod
    def _set_text(text, words, size, max_width):
        """Change a Text's words, shrinking the font if they would spill past max_width.
        Only does work when the words change - re-laying-out text every frame is slow."""
        if text.value == words:
            return
        text.value = words
        text.font_size = size
        if words and text.content_width > max_width:
            text.font_size = max(8, size * max_width / text.content_width)

    def _draw_board(self):
        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_filled(board, THEME["board"])
        if not SHOW_GRID:
            return
        for col in range(1, COLS):
            x = BOARD_LEFT + col * CELL
            arcade.draw_line(
                x,
                BOARD_BOTTOM,
                x,
                BOARD_BOTTOM + BOARD_HEIGHT,
                THEME["grid"],
                line_width=1,
            )
        for row in range(1, ROWS):
            y = BOARD_BOTTOM + row * CELL
            arcade.draw_line(
                BOARD_LEFT, y, BOARD_LEFT + BOARD_WIDTH, y, THEME["grid"], line_width=1
            )

    def _draw_locked(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = self.grid[row][col]
                if color is not None:
                    draw_block(
                        BOARD_LEFT + col * CELL, BOARD_BOTTOM + row * CELL, CELL, color
                    )

    def _draw_ghost(self):
        if GHOST_STYLE == "off":
            return
        r, g, b = COLORS[self.piece_kind][:3]
        ghost_row = self._ghost_row()
        for col, row in piece_blocks(self.piece_cells, self.piece_col, ghost_row):
            if GHOST_STYLE == "outline":
                arcade.draw_rect_outline(
                    cell_rect(col, row), (r, g, b, 150), border_width=2
                )
            else:
                arcade.draw_rect_filled(cell_rect(col, row), (r, g, b, 60))

    def _draw_piece(self):
        color = COLORS[self.piece_kind]
        for col, row in piece_blocks(self.piece_cells, self.piece_col, self.piece_row):
            draw_block(BOARD_LEFT + col * CELL, BOARD_BOTTOM + row * CELL, CELL, color)

    def _draw_preview(self, kind, top, height, max_cell=PREVIEW_CELL, faded=False):
        """Draw a piece kind centered in a box. Used for NEXT and for HOLD."""
        box = arcade.LBWH(PANEL_X, from_top(top) - height, PREVIEW_BOX[0], height)
        arcade.draw_rect_filled(box, THEME["board"])
        arcade.draw_rect_outline(box, THEME["border"], border_width=1)
        if kind is None:
            return

        r, g, b = COLORS[kind][:3]
        color = (r, g, b, 90) if faded else (r, g, b)
        cells = SHAPES[kind]
        min_c = min(c for c, r in cells)
        max_c = max(c for c, r in cells)
        min_r = min(r for c, r in cells)
        max_r = max(r for c, r in cells)
        # Shrink the squares if a big custom piece wouldn't fit the box.
        size = min(
            max_cell,
            (box.width - 12) / (max_c - min_c + 1),
            (box.height - 12) / (max_r - min_r + 1),
        )
        width = (max_c - min_c + 1) * size
        height = (max_r - min_r + 1) * size
        left = box.center_x - width / 2
        bottom = box.center_y - height / 2

        for c, r in cells:
            draw_block(
                left + (c - min_c) * size, bottom + (r - min_r) * size, size, color
            )

    def _draw_panel(self):
        self._set_text(self.t_score, f"{self.score:,}", 28, PANEL_WIDTH)
        self.t_best.value = f"best this session: {self.best_score:,}"
        self.t_level.value = f"level {self.level}"
        self.t_lines.value = f"lines {self.lines}"
        self._set_text(
            self.t_clear,
            self.clear_message + ("   (muted)" if self.muted else ""),
            14,
            PANEL_WIDTH,
        )
        for text in self.panel_labels:
            text.draw()
        for i, (top, height) in enumerate(PANEL["next_boxes"]):
            self._draw_preview(
                self.queue[i],
                top,
                height,
                PREVIEW_CELL if i == 0 else SMALL_PREVIEW_CELL,
            )
        if HOLD_ENABLED:
            top, height = PANEL["hold_box"]
            self._draw_preview(self.hold_kind, top, height, faded=self.hold_used)
        for text in self.help_texts:
            text.draw()

    def _draw_overlay(self, big, mid, small, hint):
        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_filled(board, THEME["overlay"])
        room = BOARD_WIDTH - 16
        self._set_text(self.t_big, big, 30, room)
        self._set_text(self.t_mid, mid, 18, room)
        self._set_text(self.t_small, small, 14, room)
        self._set_text(self.t_hint, hint, 14, room)
        for text in (self.t_big, self.t_mid, self.t_small, self.t_hint):
            text.draw()

    def on_draw(self):
        self.clear()
        self._draw_board()
        self._draw_locked()
        if not self.game_over:
            self._draw_ghost()
            self._draw_piece()

        board = arcade.LBWH(BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT)
        arcade.draw_rect_outline(board, THEME["border"], border_width=2)
        self._draw_panel()

        if self.game_over:
            self._draw_overlay(
                MESSAGES["game_over"],
                f"{self.score:,} points",
                f"{self.lines} lines - level {self.level}",
                f"press {key_label('restart')} to play again",
            )
        elif self.paused:
            self._draw_overlay(
                MESSAGES["paused"], "", "", f"press {key_label('pause')} to continue"
            )


if __name__ == "__main__":
    window = Tetris()
    arcade.run()
