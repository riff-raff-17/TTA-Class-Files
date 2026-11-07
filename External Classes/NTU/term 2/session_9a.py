import os

import cv2
import numpy as np

WIDTH = 600
HEIGHT = 400
SAVE_AS = "output/flag.png"

# A blank (black) image: HEIGHT rows, WIDTH columns, 3 numbers per pixel.
# uint8 means each number is a whole number form 0 to 255.
canvas = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

# One pixel. Indexing is [row, column], i.e. [y, x], with (0, 0) at the
# top left and y going DOWN the image.
# OpenCV's colors are Blue, Green, Red (BGR) not RGB.
canvas[10, 20] = (255, 255, 255)

# Slices paint whole areas at once: rows 50-149, columns 100-299
canvas[50:150, 100:300] = (0, 0, 255)

cv2.imshow("Part 1", canvas)
cv2.waitKey(0)

# A flag from three column slices. ":" on its own means "eery row".
third = WIDTH // 3
flag = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
flag[:, :third] = (164, 85, 0) # blue
flag[:, third : 2 * third] = (255, 255, 255) # white
flag[:, 2 * third : ] = (53, 65, 239) # red

# A copy is a new image.
darker = flag.copy()
darker[:] = darker // 2 # every number halved: the same flag, darker

cv2.imshow("Flags", np.hstack([flag, darker]))
cv2.waitKey(0)

cv2.destroyAllWindows()