"""Settings window for text_rec.py.

Run it from the project folder: uv run word_commands/text_rec_gui.py

The settings live in text_rec.py itself: this window reads them from there, and
Save writes each changed value back into its own place, leaving comments and the
rest of the file alone. Editing the file directly still works; use "Reload from
file" to pick up those edits.
"""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from common import script_constants
from common.runner_window import RunnerWindow
from common.script_constants import ConstantsError, Field, whole_number

SCRIPT_PATH = Path(__file__).with_name("text_rec.py")

FIELDS = [
    Field("ROBOT_IP", "Robot IP", "ip"),
    Field(
        "WORDS_MISSED_FRAMES_TO_STOP",
        "Missed frames to stop",
        "frame_count",
        "frames in a row with no command word before stopping",
    ),
]

# Action in text_rec.py -> how this window shows it
ACTIONS = {
    "forward": "Forward",
    "backward": "Backward",
    "turn_left": "Turn left",
    "turn_right": "Turn right",
    "strafe": "Strafe",
}
TURNS = {"turn_left", "turn_right"}
UNTIL_GONE = "until the word is gone"
# Unit in text_rec.py -> how this window shows it
RUNS = {
    "seconds": "for seconds",
    "cm": "for cm",
    "degrees": "for degrees",
}

# Ranges from the ugot docs; the robot quietly clamps values outside them
MOVE_SPEEDS = (5, 80)  # cm/s
TURN_SPEEDS = (5, 280)  # degrees/s
ANGLES = (-180, 180)
TIMES = (1, 360)  # With 0 the robot ignores the command

NEW_COMMAND = {"action": "forward", "speed": 30}

TABLE_HEIGHT = 200  # px; enough rows to see at a glance, scrolls past that


def units_for(action):
    return ("seconds", "degrees") if action in TURNS else ("seconds", "cm")


def runs_for(action):
    """The choices in the "Runs" box for an action."""
    return [UNTIL_GONE] + [RUNS[unit] for unit in units_for(action)]


# --- Checking commands ---


def _whole_number_in(text, limits, what):
    try:
        value = whole_number(text)
    except ValueError:
        raise ValueError(f"{what} must be a whole number") from None
    low, high = limits
    if not low <= value <= high:
        raise ValueError(f"{what} must be {low} to {high}")
    return value


def parse_command(texts):
    """Turns one row of the word table into a command for COMMANDS.

    texts is (action, speed, angle, runs, amount) as shown in the row. Raises
    ValueError with a short reason if they aren't valid.
    """
    action_text, speed_text, angle_text, runs_text, amount_text = texts
    actions = {text: action for action, text in ACTIONS.items()}
    if action_text not in actions:
        raise ValueError("pick an action")
    action = actions[action_text]

    speeds = TURN_SPEEDS if action in TURNS else MOVE_SPEEDS
    command = {"action": action, "speed": _whole_number_in(speed_text, speeds, "speed")}
    if action == "strafe":
        command["angle"] = _whole_number_in(angle_text, ANGLES, "angle")
    if runs_text != UNTIL_GONE:
        units = {RUNS[unit]: unit for unit in units_for(action)}
        if runs_text not in units:
            raise ValueError(f"{ACTIONS[action]} can't run {runs_text}")
        command["times"] = _whole_number_in(amount_text, TIMES, "amount")
        command["unit"] = units[runs_text]
    return command


def command_to_texts(command):
    """The texts a row of the word table shows for a command."""
    if not isinstance(command, dict) or command.get("action") not in ACTIONS:
        raise ValueError(
            'must be like {"action": "forward", "speed": 30}, with action one of '
            + ", ".join(ACTIONS)
        )
    if "times" in command or "unit" in command:
        if command.get("unit") not in RUNS:
            raise ValueError(
                'needs both "times" and "unit", with unit one of ' + ", ".join(RUNS)
            )
        runs = RUNS[command["unit"]]
    else:
        runs = UNTIL_GONE
    return (
        ACTIONS[command["action"]],
        str(command.get("speed", "")),
        str(command.get("angle", "")),
        runs,
        str(command.get("times", "")),
    )


def word_problems(words):
    """Problems with the words of the table, in order."""
    problems = []
    seen = set()
    for word in words:
        if not isinstance(word, str) or not word.strip():
            problems.append("a word is empty")
        elif word != word.strip():
            problems.append(f"{word!r} starts or ends with a space")
        # Words match in any case, so "Left" and "left" would be the same word
        elif word.casefold() in seen:
            problems.append(f"{word!r} is used more than once (in any case)")
        else:
            seen.add(word.casefold())
    return problems


def check_commands(commands):
    """Raises ConstantsError if COMMANDS (as read from the script) isn't valid."""
    if not isinstance(commands, dict) or not commands:
        raise ConstantsError(
            "COMMANDS must hold at least one word, like "
            '{"Forward": {"action": "forward", "speed": 30}}'
        )
    problems = [f"COMMANDS {problem}" for problem in word_problems(commands)]
    for word, command in commands.items():
        # Round-trip through the table's checks, like read_constants() does
        reason = "isn't a valid command"
        try:
            ok = parse_command(command_to_texts(command)) == command
        except ValueError as error:
            ok = False
            reason = str(error)
        if not ok:
            problems.append(f"COMMANDS[{word!r}] {reason} (it's {command!r})")
    if problems:
        raise ConstantsError("\n".join(problems))


# --- Reading and writing the script ---


def read_settings(source):
    """Returns {name: value} for every setting in text_rec.py's source."""
    values = script_constants.read_constants(source, FIELDS)
    found = script_constants.find_constants(source, ["COMMANDS"])
    commands = found["COMMANDS"][2]
    check_commands(commands)
    values["COMMANDS"] = commands
    return values


def update_settings(source, values):
    """Returns the source with its settings set to new values."""
    return script_constants.update_constants(source, values, read_settings)


# --- The window ---


class CommandRow:
    """One word and its command in the word table."""

    def __init__(self, parent, row, on_remove):
        self.word = tk.StringVar()
        self.action = tk.StringVar()
        self.speed = tk.StringVar()
        self.angle = tk.StringVar()
        self.runs = tk.StringVar()
        self.amount = tk.StringVar()

        word_entry = ttk.Entry(parent, textvariable=self.word, width=18)
        action_box = ttk.Combobox(
            parent,
            textvariable=self.action,
            values=list(ACTIONS.values()),
            state="readonly",
            width=10,
        )
        speed_entry = ttk.Entry(parent, textvariable=self.speed, width=5)
        self.angle_entry = ttk.Entry(parent, textvariable=self.angle, width=5)
        self.runs_box = ttk.Combobox(
            parent, textvariable=self.runs, state="readonly", width=20
        )
        self.amount_entry = ttk.Entry(parent, textvariable=self.amount, width=5)
        remove = ttk.Button(parent, text="Remove", command=lambda: on_remove(self))
        self.widgets = [
            word_entry,
            action_box,
            speed_entry,
            self.angle_entry,
            self.runs_box,
            self.amount_entry,
            remove,
        ]
        for column, widget in enumerate(self.widgets):
            widget.grid(row=row, column=column, sticky="w", padx=(0, 6), pady=2)
        self.word_entry = word_entry

        self.action.trace_add("write", lambda *_: self._action_changed())
        self.runs.trace_add("write", lambda *_: self._runs_changed())

    def set(self, word, command):
        action, speed, angle, runs, amount = command_to_texts(command)
        self.word.set(word)
        self.action.set(action)
        self.speed.set(speed)
        self.angle.set(angle)
        self.runs.set(runs)
        self.amount.set(amount)

    def texts(self):
        """(word, action, speed, angle, runs, amount) as typed into the row."""
        return tuple(
            var.get()
            for var in (
                self.word,
                self.action,
                self.speed,
                self.angle,
                self.runs,
                self.amount,
            )
        )

    def destroy(self):
        for widget in self.widgets:
            widget.destroy()

    def _action_changed(self):
        actions = {text: action for action, text in ACTIONS.items()}
        action = actions.get(self.action.get())
        # Only a strafe has an angle
        self.angle_entry["state"] = "normal" if action == "strafe" else "disabled"
        choices = runs_for(action)
        self.runs_box["values"] = choices
        # e.g. "for degrees" after switching from a turn to a move
        if self.runs.get() not in choices:
            self.runs.set(UNTIL_GONE)

    def _runs_changed(self):
        timed = self.runs.get() != UNTIL_GONE
        self.amount_entry["state"] = "normal" if timed else "disabled"


class App(RunnerWindow):
    title = "UGOT Text Recognition"

    def __init__(self, root):
        self.vars = {}  # Field name -> StringVar
        self.rows = []  # CommandRows, in table order
        super().__init__(root, SCRIPT_PATH)

    def build_form(self, parent):
        box = ttk.LabelFrame(parent, text="Robot", padding=(10, 5))
        box.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for i, field in enumerate(FIELDS):
            ttk.Label(box, text=field.label).grid(
                row=i, column=0, sticky="w", padx=(0, 10), pady=2
            )
            var = tk.StringVar()
            width = 18 if field.kind == "ip" else 8
            ttk.Entry(box, textvariable=var, width=width).grid(
                row=i, column=1, sticky="w"
            )
            ttk.Label(box, text=field.hint, foreground="gray").grid(
                row=i, column=2, sticky="w", padx=(10, 0)
            )
            self.vars[field.name] = var

        box = ttk.LabelFrame(parent, text="Words", padding=(10, 5))
        box.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        box.columnconfigure(0, weight=1)

        canvas = tk.Canvas(box, height=TABLE_HEIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(box, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._bind_table_scroll(canvas)

        self.table = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.table, anchor="nw")
        self.table.bind(
            "<Configure>",
            # Match the canvas's width to the table's, so the window still grows
            # to fit wide rows; only its height is capped, with a scrollbar.
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all"), width=event.width
            ),
        )
        for column, heading in enumerate(
            ["Word or phrase", "Action", "Speed", "Angle", "Runs", "Amount"]
        ):
            ttk.Label(self.table, text=heading).grid(
                row=0, column=column, sticky="w", padx=(0, 6)
            )
        self.next_row = 1  # Grid row for the next CommandRow

        ttk.Button(box, text="Add word", command=self._add_word).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 4)
        )
        ttk.Label(
            box,
            text=(
                "Words match in any case, also inside longer text: "
                '"Move forward" triggers "Forward".\n'
                "Speed: cm/s (5-80), or degrees/s for turns (5-280). "
                "Angle (strafe only): 0 ahead, -90 left, 90 right.\n"
                'Runs "for ..." moves for the amount (1-360), then stops by '
                "itself; the camera pauses meanwhile."
            ),
            foreground="gray",
            justify="left",
        ).grid(row=2, column=0, sticky="w")

    def _bind_table_scroll(self, canvas):
        """Mouse wheel scrolls the word table while the pointer is over it."""

        def scroll(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

        def bind(_):
            canvas.bind_all("<MouseWheel>", scroll)
            canvas.bind_all("<Button-4>", scroll)
            canvas.bind_all("<Button-5>", scroll)

        def unbind(_):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", bind)
        canvas.bind("<Leave>", unbind)

    def _new_row(self, word, command):
        row = CommandRow(self.table, self.next_row, self._remove_row)
        self.next_row += 1
        row.set(word, command)
        self.rows.append(row)
        return row

    def _add_word(self):
        self._new_row("", NEW_COMMAND).word_entry.focus_set()

    def _remove_row(self, row):
        row.destroy()
        self.rows.remove(row)

    # --- Form contents ---

    def read_settings(self, source):
        return read_settings(source)

    def write_settings(self, source, values):
        return update_settings(source, values)

    def form_state(self):
        return (
            {name: var.get() for name, var in self.vars.items()},
            [row.texts() for row in self.rows],
        )

    def show_values(self, values):
        for field in FIELDS:
            (text,) = script_constants.value_to_texts(field.kind, values[field.name])
            self.vars[field.name].set(text)
        for row in self.rows:
            row.destroy()
        self.rows = []
        for word, command in values["COMMANDS"].items():
            self._new_row(word, command)

    def read_form(self):
        values = {}
        problems = []
        for field in FIELDS:
            try:
                values[field.name] = script_constants.parse_value(
                    field.kind, (self.vars[field.name].get(),)
                )
            except ValueError as error:
                problems.append(f"{field.label}: {error}")

        commands = {}
        if not self.rows:
            problems.append("Words: add at least one word")
        words = [row.word.get().strip() for row in self.rows]
        problems += [f"Words: {problem}" for problem in word_problems(words)]
        for word, row in zip(words, self.rows):
            try:
                commands[word] = parse_command(row.texts()[1:])
            except ValueError as error:
                problems.append(f"{word or 'Empty word'}: {error}")
        values["COMMANDS"] = commands
        return values, problems


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
