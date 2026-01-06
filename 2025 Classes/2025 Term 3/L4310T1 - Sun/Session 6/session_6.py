import cv2
import numpy as np
from ugot import ugot

got = ugot.UGOT()
got.initialize('192.168.1.218')
got.open_camera()

def main():
    while True:
        frame = got.read_camera_data()