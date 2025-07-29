#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UGOTControl.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class UGOTControlUI:
    def __init__(
        self,
        master=None,
        translator=None,
        on_first_object_cb=None,
        data_pool=None
    ):
        self.builder = pygubu.Builder(
            translator=translator,
            on_first_object=on_first_object_cb,
            data_pool=data_pool
        )
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: ttk.Frame = self.builder.get_object("frame1", master)
        self.builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def forward_clicked(self):
        pass

    def left_clicked(self):
        pass

    def right_clicked(self):
        pass

    def back_clicked(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = UGOTControlUI(root)
    app.run()
