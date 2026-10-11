import re
import signal

import cv2
import numpy as np
from ugot import ugot

from common import video_link

# --- CONSTANTS TO CHANGE --- (text_rec_gui.py edits these too)
ROBOT_IP = "192.168.1.182"
WORDS_MISSED_FRAMES_TO_STOP = 2  # Frames in a row with no command word before stopping

# Word or phrase to look for -> what the robot does when it sees it
#   action: "forward", "backward", "turn_left", "turn_right" or "strafe"
#   speed:  cm/s (5-80), or degrees/s for turns (5-280)
#   angle:  strafe only: 0 is ahead, -90 left, 90 right (-180 to 180)
#   times + unit: optional. Without them the move lasts until the word is gone;
#     with them it runs for that long and then stops by itself. unit is
#     "seconds" or "cm" ("seconds" or "degrees" for turns), times 1-360
COMMANDS = {
    "Forward": {"action": "forward", "speed": 30},
    "Backward": {"action": "backward", "speed": 30},
    "Left": {"action": "turn_left", "speed": 45},
    "Right": {"action": "turn_right", "speed": 45},
}

got = ugot.UGOT()
got.initialize(ROBOT_IP)

got.load_models(["word_recognition"])
got.open_camera()

# Set only when text_rec_gui.py runs this script: the video then shows in the GUI
video = video_link.sender_from_env()

MOVE_DIRECTIONS = {"forward": 0, "backward": 1}
TURN_DIRECTIONS = {"turn_left": 2, "turn_right": 3}
UNITS = {"seconds": 0, "cm": 1, "degrees": 2}

# Longest first, so "Turn left" wins over "Left" when both could match
WORDS = sorted(COMMANDS, key=len, reverse=True)
# Any case, and only whole words: "move forward" matches "Forward" but "Leftover"
# doesn't. Recognition joins what it reads with commas ("Turn,left"), so spaces in
# a phrase match spaces or commas
COMMAND_PATTERN = re.compile(
    r"(?<!\w)(?:"
    + "|".join(
        "(" + r"[\s,]+".join(re.escape(part) for part in word.split()) + ")"
        for word in WORDS
    )
    + r")(?!\w)",
    re.IGNORECASE,
)


def find_command(text):
    """Return the COMMANDS key of the first command word in text, or None."""
    match = COMMAND_PATTERN.search(text)
    if match is None:
        return None
    # Each word has its own group, so the group that matched says which word
    return WORDS[match.lastindex - 1]


def run_command(command):
    """Starts a command's move; a timed move returns once it's finished."""
    action = command["action"]
    speed = command["speed"]
    times = command.get("times")
    unit = UNITS.get(command.get("unit"))

    if action in MOVE_DIRECTIONS:
        direction = MOVE_DIRECTIONS[action]
        if times is None:
            got.mecanum_move_speed(direction=direction, speed=speed)
        else:
            got.mecanum_move_speed_times(
                direction=direction, speed=speed, times=times, unit=unit
            )
    elif action in TURN_DIRECTIONS:
        turn = TURN_DIRECTIONS[action]
        if times is None:
            got.mecanum_turn_speed(turn=turn, speed=speed)
        else:
            got.mecanum_turn_speed_times(turn=turn, speed=speed, times=times, unit=unit)
    elif action == "strafe":
        angle = command["angle"]
        if times is None:
            got.mecanum_translate_speed(angle=angle, speed=speed)
        else:
            got.mecanum_translate_speed_times(
                angle=angle, speed=speed, times=times, unit=unit
            )
    else:
        print(f"Unknown action {action!r}")


def main():
    got.mecanum_stop()
    current_word = None
    missed_frames = 0

    while True:
        frame = got.read_camera_data()
        if frame:
            if video:
                video.send(frame)
            else:
                data = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow("Robot Feed", data)

        # The result can be empty (or None) when no text is in view
        text = got.get_words_result() or ""
        word = find_command(text)

        # Recognition can drop the word for a frame; keep the current command
        # until it has been missing for several frames in a row
        if word is None:
            missed_frames += 1
            if missed_frames < WORDS_MISSED_FRAMES_TO_STOP:
                word = current_word
        else:
            missed_frames = 0

        # Only act when the word changes: a continuous move keeps going by itself,
        # and a timed one shouldn't repeat while its word stays in view
        if word != current_word:
            print(f"Saw {text!r} -> {word or 'Stop'}")
            if word is None:
                got.mecanum_stop()
            else:
                run_command(COMMANDS[word])
            current_word = word

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    # The Stop button in text_rec_gui.py sends Ctrl+Break on Windows; treat it like
    # Ctrl+C
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)

    try:
        main()
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        # However the run ends, stop the wheels: otherwise the robot keeps its last
        # motion. Wheels first, so a window error can't prevent it
        got.mecanum_stop()
        cv2.destroyAllWindows()
