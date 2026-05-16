import cv2
import mediapipe as mp
import pygame
import math
import random
import time

from hand_common import (
    make_detector,
    INDEX_TIP,
    THUMB_TIP,
    FPSCounter,
)