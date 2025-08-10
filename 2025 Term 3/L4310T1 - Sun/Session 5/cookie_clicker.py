#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from cookie_clickerui import CookieClickerUI

cookies = 1

class CookieClicker(CookieClickerUI):
    def __init__(self, master=None):
        super().__init__(master)

    def btn_clicked(self):
        global cookies
        cookies += 1100
        lbl = self.builder.get_object('num_cookies')
        lbl.configure(text=f'Cookies: {cookies}')


if __name__ == "__main__":
    root = tk.Tk()
    app = CookieClicker(root)
    app.run()
