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
AMBER = (0, 130, 230)
BLUE = (230, 140, 40)
PURPLE = (200, 80, 180)
STEEL = (170, 150, 120)
GREY = (110, 110, 110)
FONT = cv2.FONT_HERSHEY_SIMPLEX
TOP = 60  # dots stay below the score line

# Every kind of dot starts from these settings...
DEFAULTS = {
    "color": RED,
    "shape": "circle",  # "circle", "square" or "diamond"
    "points": 1,  # added to the score when the dot is cleared
    "seconds": 0,  # added to the timer when the dot is cleared
    "size": 1.0,  # multiplier! 
    "life": 1.0,  # how long it lasts
    "hits": 1,  # clicks needed to clear it
    "move": None,  # None, "bounce" or "flee"
    "speed": 0,  # pixels moved each frame
    "flee_distance": 0,  # a "flee" dot runs when the mouse is this close
    "miss": True,  # does letting it vanish count as a miss?
    "label": "",  # text drawn in the middle
    "chance": 1,  # how often it appears
}

# ...and each kind only lists the settings it changes. To make your own
# kind of dot, add a line here.
TARGETS = {
    "normal": {"chance": 8},
    "gold": {"color": AMBER, "shape": "diamond", "points": 6, "size": 0.7, 
             "life": 0.6, "miss": False, "chance": 2},
    "armored": {"color": STEEL, "shape": "square", "points": 2, "size": 1.2,
                "life": 1.5, "hits": 3, "chance": 2},
    "mover": {"color": GREEN, "points": 2, "size": 0.8, "life": 1.5,
              "move": "bounce", "speed": 4, "chance": 2},
    "bomb": {"color": GREY, "points": -3, "label": "X", "miss": False,
             "chance": 1},
}

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


def is_hit(point, centre, radius, shape="circle"):
    """True if point is inside the circle (its distance from the centre is
    at most the radius)."""
    dx = abs(point[0] - centre[0])
    dy = abs(point[1] - centre[1])
    if shape == "square":
        return dx <= radius and dy <= radius
    if shape == "diamond":
        return dx + dy <= radius
    return math.dist(point, centre) <= radius


def draw_shape(canvas, shape, centre, radius, color, thickness):
    x, y =centre
    if shape == "square":
        cv2.rectangle(canvas, (x - radius, y - radius), (x + radius, y + radius),
                    color, thickness, cv2.LINE_AA)
    elif shape == "diamond":
        corners = np.array([(x, y - radius), (x + radius, y),
                            (x, y + radius), (x - radius, y)], np.int32)
        if thickness == cv2.FILLED:
            cv2.fillPoly(canvas, [corners], color, cv2.LINE_AA)
        else:
            cv2.polylines(canvas, [corners], True, color, thickness, cv2.LINE_AA)
    else:
        cv2.circle(canvas, centre, radius, color, thickness, cv2.LINE_AA)


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
