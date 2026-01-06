#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from ugot_controllerui import UgotGUIUI

from ugot import ugot
got = ugot.UGOT()
got.initialize('192.168.1.217')

class UgotGUI(UgotGUIUI):
    def __init__(self, master=None):
        super().__init__(master)

    def forward_press(self, event=None):
        got.mecanum_move_speed(direction=0, speed=30)

    def forward_release(self, event=None):
        got.mecanum_stop()

    def left_press(self, event=None):
        got.mecanum_turn_speed(turn=2, speed=45)

    def left_release(self, event=None):
        got.mecanum_stop()

    def back_press(self, event=None):
        got.mecanum_move_speed(direction=1, speed=30)

    def back_release(self, event=None):
        got.mecanum_stop()

    def right_press(self, event=None):
        got.mecanum_turn_speed(turn=3, speed=45)

    def right_release(self, event=None):
        got.mecanum_stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = UgotGUI(root)
    app.run()
