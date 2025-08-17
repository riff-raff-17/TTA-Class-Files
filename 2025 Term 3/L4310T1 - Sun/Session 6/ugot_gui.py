#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from ugot_guiui import UgotGUIUI

from ugot import ugot
got = ugot.UGOT()
got.initialize("192.168.1.218")

got.open_camera()

class UgotGUI(UgotGUIUI):
    def __init__(self, master=None):
        super().__init__(master)

    def fwd_pressed(self, event=None):
        got.mecanum_move_speed(direction=0, speed=45)

    def btn_release(self, event=None):
        got.mecanum_stop()

    def left_pressed(self, event=None):
        got.mecanum_turn_speed(turn=2, speed=45)

    def back_press(self, event=None):
        got.mecanum_move_speed(direction=1, speed=45)

    def right_press(self, event=None):
        got.mecanum_turn_speed(turn=3, speed=45)

    def talk_pressed(self):
        entry_widget = self.builder.get_object('speech_entry')
        text = entry_widget.get()
        got.play_audio_tts(data=text, voice_type=0, wait=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = UgotGUI(root)
    app.run()