"""Lesson 4: the mouse, trackbars, and a first game: click the dots.

Run from the workspace folder: uv run opencv_course/basics/04_mouse.py
Click each dot before it disappears. Keys: r restart, q or Esc quit.
The "Size" and "Seconds x10" sliders change the dots while you play.
"""

import math
import random
import time

import cv2
import numpy as np

WIDTH = 800
HEIGHT = 600
WINDOW = "Lesson 4"
GAME_SECONDS = 30

WHITE = (255, 255, 255)
RED = (60, 60, 230)
GREEN = (80, 200, 80)
YELLOW = (40, 210, 240)
FONT = cv2.FONT_HERSHEY_SIMPLEX

# The mouse callback only writes down what happened; the main loop decides
# what it means. Keeping game rules in one place makes them easier to follow.
clicks = []
mouse = (0, 0)


def on_mouse(event, x, y, flags, param):
    # OpenCV calls this for every mouse event in the window
    global mouse
    mouse = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append((x, y))


def is_hit(point, centre, radius):
    """True if point is inside the circle (its distance from the centre is
    at most the radius)."""
    return math.dist(point, centre) <= radius


def new_dot(radius):
    # Random, but kept fully inside the window
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius + 60, HEIGHT - radius)  # below the score
    return (x, y), time.perf_counter()


cv2.namedWindow(WINDOW)
cv2.setMouseCallback(WINDOW, on_mouse)
# A trackbar is a slider: name, window, starting value, highest value, and a
# function to call when it moves (we read it each frame instead)
cv2.createTrackbar("Size", WINDOW, 40, 100, lambda value: None)
cv2.createTrackbar("Seconds x10", WINDOW, 15, 50, lambda value: None)

score = 0
misses = 0
radius = 40
dot, dot_born = new_dot(radius)
game_start = time.perf_counter()

while True:
    # Trackbars start at 0, which would make an invisible or instant dot
    radius = max(10, cv2.getTrackbarPos("Size", WINDOW))
    lifetime = max(3, cv2.getTrackbarPos("Seconds x10", WINDOW)) / 10
    now = time.perf_counter()
    time_left = GAME_SECONDS - (now - game_start)
    playing = time_left > 0

    if playing:
        for click in clicks:
            if is_hit(click, dot, radius):
                score += 1
                dot, dot_born = new_dot(radius)
        if now - dot_born > lifetime:
            misses += 1
            dot, dot_born = new_dot(radius)
    clicks.clear()

    canvas = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    if playing:
        # The dot shrinks as its time runs out
        left = 1 - (now - dot_born) / lifetime
        cv2.circle(canvas, dot, radius, RED, cv2.FILLED, cv2.LINE_AA)
        cv2.circle(canvas, dot, int(radius * left), YELLOW, 2, cv2.LINE_AA)
        # Highlight the dot when the mouse is over it
        if is_hit(mouse, dot, radius):
            cv2.circle(canvas, dot, radius + 6, WHITE, 2, cv2.LINE_AA)
        status = f"Score {score}   Missed {misses}   Time {time_left:.0f}"
        cv2.putText(canvas, status, (20, 40), FONT, 1, WHITE, 2, cv2.LINE_AA)
    else:
        cv2.putText(canvas, "Time's up!", (250, 250), FONT, 2, YELLOW, 3, cv2.LINE_AA)
        result = f"Score {score}   Missed {misses}"
        cv2.putText(canvas, result, (250, 320), FONT, 1, WHITE, 2, cv2.LINE_AA)
        cv2.putText(canvas, "r: again", (250, 380), FONT, 0.8, GREEN, 2, cv2.LINE_AA)
    cv2.imshow(WINDOW, canvas)

    key = cv2.waitKey(16) & 0xFF  # about 60 frames a second
    if key in (ord("q"), 27):
        break
    if key == ord("r"):
        score = 0
        misses = 0
        dot, dot_born = new_dot(radius)
        game_start = time.perf_counter()
    if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
