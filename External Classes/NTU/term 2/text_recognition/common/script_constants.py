"""Reads and rewrites the constants at the top of a robot script.

The constants live in the script itself: a settings window reads them from
there, and saving writes each changed value back into its own place, leaving
comments and the rest of the file alone.
"""

import ast
import ipaddress
import json
import math
from dataclasses import dataclass

LINE_LENGTH = 88  # ruff's default, so a saved file is laid out as ruff would


@dataclass(frozen=True)
class Field:
    name: str  # Constant name in the script
    label: str
    kind: str  # How the value is checked; see parse_value()
    hint: str = ""


class ConstantsError(Exception):
    """The script's constants can't be read or safely rewritten."""


# --- Checking values ---


def whole_number(text):
    try:
        return int(text)
    except ValueError:
        raise ValueError("must be a whole number") from None


def _number(text):
    try:
        value = int(text)
    except ValueError:
        try:
            value = float(text)
        except ValueError:
            raise ValueError("must be a number") from None
    # inf / nan would be written as names Python doesn't know, breaking the script
    if not math.isfinite(value):
        raise ValueError("must be a number")
    return value


def parse_value(kind, texts):
    """Turns the text typed into a field into the value to save.

    texts has one string per input box (three for a pose). Raises ValueError
    with a short reason if the text isn't valid.
    """
    if kind == "pose":
        try:
            return tuple(int(text) for text in texts)
        except ValueError:
            raise ValueError("joint angles must be whole numbers") from None

    (text,) = texts
    if kind == "ip":
        try:
            ipaddress.ip_address(text)
        except ValueError:
            raise ValueError("must be an IP address like 192.168.1.204") from None
        return text
    if kind == "text":
        if not text.strip():
            raise ValueError("can't be empty")
        return text
    if kind == "int":
        return whole_number(text)
    if kind == "number":
        return _number(text)
    if kind == "delay":
        value = _number(text)
        # time.sleep() crashes on a negative delay
        if value < 0:
            raise ValueError("can't be negative")
        return value
    if kind == "frame_count":
        value = whole_number(text)
        # With 0 the robot would switch / stop even while it can still see
        if value < 1:
            raise ValueError("must be at least 1")
        return value
    raise ValueError(f"unknown field kind {kind!r}")


def value_to_texts(kind, value):
    """The text to show in a field's input box(es) for a value."""
    if kind == "pose":
        if not (isinstance(value, tuple) and len(value) == 3):
            raise ValueError("must be three joint angles, like (0, 45, 45)")
        return tuple(str(angle) for angle in value)
    return (str(value),)


# --- Reading and writing the script ---


def find_constants(source, names):
    """Finds each named constant in the script source (bytes).

    Returns {name: (start, end, value)}, where start/end are byte offsets of
    the value's text, so it can be replaced without touching anything else.
    """
    wanted = set(names)
    tree = ast.parse(source)
    # ast positions are (line, byte offset in that line); turn them into
    # offsets in the whole source
    line_starts = [0] + [i + 1 for i, byte in enumerate(source) if byte == ord("\n")]

    found = {}
    problems = []
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in wanted
        ):
            continue
        name = node.targets[0].id
        if name in found:
            problems.append(f"{name} is set more than once")
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            problems.append(
                f"{name} isn't a plain value (for example it's calculated), "
                "so this window can't edit it"
            )
            value = None
        start = line_starts[node.value.lineno - 1] + node.value.col_offset
        end = line_starts[node.value.end_lineno - 1] + node.value.end_col_offset
        found[name] = (start, end, value)

    for name in names:
        if name not in found:
            problems.append(f"{name} is missing")
    if problems:
        raise ConstantsError("\n".join(problems))
    return found


def read_constants(source, fields):
    """Returns {name: value} for each field, checked like the form checks input."""
    found = find_constants(source, [field.name for field in fields])
    values = {}
    problems = []
    for field in fields:
        value = found[field.name][2]
        # Round-trip through the form's checks: anything the form would reject
        # (or show differently, like a number stored as text) is a problem
        reason = "has the wrong type"
        try:
            ok = parse_value(field.kind, value_to_texts(field.kind, value)) == value
        except ValueError as error:
            ok = False
            reason = str(error)
        if ok:
            values[field.name] = value
        else:
            problems.append(f"{field.name} {reason} (it's {value!r})")
    if problems:
        raise ConstantsError("\n".join(problems))
    return values


def format_literal(value):
    """Python source text for a value, in the style the scripts already use.

    A dict is written one item per line with a trailing comma, like a constant
    list in the scripts; dicts inside it stay on one line unless that line
    would be too long.
    """
    if isinstance(value, dict) and value:
        return _format_dict_lines(value, indent=0)
    return _format_inline(value)


def _format_inline(value):
    if isinstance(value, str):
        # json.dumps gives a double-quoted string with Python-compatible escapes
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, tuple):
        return "(" + ", ".join(repr(item) for item in value) + ")"
    if isinstance(value, dict):
        items = (f"{_format_inline(k)}: {_format_inline(v)}" for k, v in value.items())
        return "{" + ", ".join(items) + "}"
    return repr(value)


def _format_dict_lines(value, indent):
    pad = " " * (indent + 4)
    lines = ["{"]
    for key, item in value.items():
        prefix = f"{pad}{_format_inline(key)}: "
        text = _format_inline(item)
        # +1 for the trailing comma
        if (
            isinstance(item, dict)
            and item
            and len(prefix) + len(text) + 1 > LINE_LENGTH
        ):
            text = _format_dict_lines(item, indent + 4)
        lines.append(f"{prefix}{text},")
    lines.append(" " * indent + "}")
    return "\n".join(lines)


def update_constants(source, values, read):
    """Returns the source with the given constants set to new values.

    Values that haven't changed are left exactly as written (so `1` doesn't
    become `1.0`). The result is read back with read(source) and checked
    before it's returned, so a bad edit can't reach the file.
    """
    found = find_constants(source, list(values))
    # A value written over several lines must use the file's own line endings
    newline = "\r\n" if b"\r\n" in source else "\n"
    edits = []
    for name, value in values.items():
        start, end, old = found[name]
        if value == old and type(value) is type(old):
            continue
        literal = format_literal(value).replace("\n", newline)
        edits.append((start, end, literal.encode()))

    # Replace from the end of the file backwards so earlier offsets stay valid
    for start, end, literal in sorted(edits, reverse=True):
        source = source[:start] + literal + source[end:]

    try:
        written = read(source)
    except (ConstantsError, SyntaxError) as error:
        raise ConstantsError(f"Saving would break the script:\n{error}") from None
    if any(written[name] != value for name, value in values.items()):
        raise ConstantsError("Saving would not store the values correctly")
    return source
