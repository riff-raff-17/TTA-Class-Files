#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from ugot_controllerui import UGOTControlUI

from ugot import ugot
got = ugot.UGOT()
# got.initialize('192.168.1.247')

class UGOTControl(UGOTControlUI):
    def __init__(self, master=None):
        super().__init__(master)

    def forward_clicked(self):
        got.wheelleg_move_speed_times(0, 30, 50, 1)

    def left_clicked(self):
        got.wheelleg_turn_speed_times(2, 45, 90, 2)

    def right_clicked(self):
        got.wheelleg_turn_speed_times(3, 45, 90, 2)

    def back_clicked(self):
        got.wheelleg_move_speed_times(1, 30, 50, 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = UGOTControl(root)
    app.run()
