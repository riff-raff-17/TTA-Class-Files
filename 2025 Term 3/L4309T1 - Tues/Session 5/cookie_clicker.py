#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from cookie_clickerui import CookieClickerUI

#start at x cookies
cookies = 1

class CookieClicker(CookieClickerUI):
    def __init__(self, master=None):
        super().__init__(master)

    def on_cookie_pressed(self):
        global cookies
        cookies *= 2
        lbl = self.builder.get_object('cookie_label')
        lbl.configure(text=f'Cookies: {cookies}')


if __name__ == "__main__":
    root = tk.Tk()
    app = CookieClicker(root)
    app.run()
