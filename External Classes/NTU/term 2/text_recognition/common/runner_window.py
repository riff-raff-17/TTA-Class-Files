"""The parts every settings window shares: running the robot script, its camera
video, its output log, and loading / saving the settings in the script.

Each window subclasses RunnerWindow and fills in its own settings form.
"""

import base64
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from common import video_link
from common.script_constants import ConstantsError
from common.script_runner import ScriptRunner

POLL_MS = 33  # Also how often the video updates: about 30 frames a second
VIDEO_SIZE = (480, 360)  # Camera frames are scaled down to fit this


class RunnerWindow:
    """Settings on the left, camera on the right, log underneath.

    Subclasses fill in the settings form by overriding the methods marked
    "for subclasses" below.
    """

    title = ""

    def __init__(self, root, script_path):
        self.root = root
        self.script_path = script_path
        self.runner = ScriptRunner(script_path)
        self.loaded_source = None  # File contents as last loaded / saved
        self.loaded_state = None  # form_state() matching loaded_source
        self.closing = False
        self.frame_image = None  # Keeps the shown frame alive; Tk drops it otherwise
        try:
            self.video = video_link.FrameReceiver(VIDEO_SIZE)
        except OSError:
            # The script then shows the video in its own OpenCV window instead
            self.video = None

        self._build()
        self.reload(confirm=False)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._poll()

    # --- For subclasses ---

    def build_form(self, parent):
        """Adds the settings inputs to parent (a frame with one column)."""
        raise NotImplementedError

    def read_settings(self, source):
        """Returns the settings in the script source.

        Raises ConstantsError (or SyntaxError) if they can't be read.
        """
        raise NotImplementedError

    def write_settings(self, source, values):
        """Returns the script source with its settings changed to values."""
        raise NotImplementedError

    def show_values(self, values):
        """Fills the form with values, as returned by read_settings()."""
        raise NotImplementedError

    def read_form(self):
        """Returns ({name: value}, [problems]) for what's typed into the form."""
        raise NotImplementedError

    def form_state(self):
        """Something that changes whenever anything typed into the form does."""
        raise NotImplementedError

    # --- Building the window ---

    def _build(self):
        self.root.title(self.title)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        # Settings and buttons on the left, camera on the right, log underneath
        settings = ttk.Frame(main)
        settings.grid(row=0, column=0, sticky="nsew")
        settings.columnconfigure(0, weight=1)
        self._build_video(main)
        self.log = ScrolledText(main, height=10, state="disabled")
        self.log.grid(row=1, column=0, columnspan=2, sticky="nsew")

        form = ttk.Frame(settings)
        form.grid(row=0, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)
        self.build_form(form)

        buttons = ttk.Frame(settings)
        buttons.grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.reload_button = ttk.Button(
            buttons, text="Reload from file", command=self.reload
        )
        self.save_button = ttk.Button(buttons, text="Save", command=self.save)
        self.run_button = ttk.Button(
            buttons, text="Save & Run", command=self.save_and_run
        )
        self.stop_button = ttk.Button(buttons, text="Stop", command=self.stop)
        for button in (
            self.reload_button,
            self.save_button,
            self.run_button,
            self.stop_button,
        ):
            button.pack(side="left", padx=(0, 6))

    def _build_video(self, parent):
        box = ttk.LabelFrame(parent, text="Camera", padding=5)
        box.grid(row=0, column=1, sticky="n", padx=(10, 0), pady=(0, 8))
        # Fixed size, so the layout doesn't jump when frames start or stop
        screen = tk.Frame(box, width=VIDEO_SIZE[0], height=VIDEO_SIZE[1], bg="black")
        screen.pack()
        screen.pack_propagate(False)
        self.video_label = tk.Label(screen, bg="black", fg="white", bd=0)
        self.video_label.pack(expand=True)
        if self.video is None:
            self.video_label["text"] = (
                "The video can't be shown here.\n"
                "It will open in its own window instead."
            )

    # --- Form contents ---

    def _show(self, values):
        self.show_values(values)
        self.loaded_state = self.form_state()

    def _is_dirty(self):
        return self.loaded_state is not None and self.form_state() != self.loaded_state

    # --- Buttons ---

    def reload(self, confirm=True):
        if (
            confirm
            and self._is_dirty()
            and not messagebox.askyesno(
                "Unsaved changes", "Discard your changes and reload from the file?"
            )
        ):
            return
        name = self.script_path.name
        try:
            source = self.script_path.read_bytes()
            values = self.read_settings(source)
        except (OSError, SyntaxError, ConstantsError) as error:
            self.loaded_source = None
            messagebox.showerror(
                "Can't read the settings",
                f"Couldn't read the constants from {name}:\n\n{error}\n\n"
                "Fix the file, then press Reload from file.",
            )
        else:
            self.loaded_source = source
            self._show(values)
        self._update_buttons()

    def save(self):
        """Writes the form to the script. Returns True if it's saved."""
        values, problems = self.read_form()
        if problems:
            messagebox.showerror(
                "Can't save", "Please fix these first:\n\n" + "\n".join(problems)
            )
            return False
        try:
            current = self.script_path.read_bytes()
            if current != self.loaded_source and not messagebox.askyesno(
                "File changed",
                f"{self.script_path.name} was changed outside this window since it "
                "was loaded.\n\nOverwrite its settings with the ones in this window? "
                "(Choose No, then Reload from file, to see the file's settings.)",
                icon="warning",
            ):
                return False
            updated = self.write_settings(current, values)
            if updated != current:
                self.script_path.write_bytes(updated)
        except (OSError, SyntaxError, ConstantsError) as error:
            messagebox.showerror("Can't save", str(error))
            return False
        self.loaded_source = updated
        self._show(values)
        return True

    def save_and_run(self):
        if self.runner.active or not self.save():
            return
        try:
            if self.video is None:
                self.runner.start()
            else:
                self.video.take_image()  # Drop the last frame of the previous run
                self.runner.start(self.video.env())
        except OSError as error:
            messagebox.showerror("Can't run", f"Couldn't start the script:\n\n{error}")
            return
        self._log(f"--- Running {self.script_path.name} ---\n")
        self._update_buttons()

    def stop(self):
        self._log("--- Stopping... ---\n")
        self.runner.request_stop()
        self._update_buttons()

    def on_close(self):
        if self._is_dirty() and not messagebox.askyesno(
            "Unsaved changes", "Close without saving your changes?"
        ):
            return
        if self.runner.active:
            if not messagebox.askyesno(
                "Script running",
                "The robot script is still running. Stop it and close?",
            ):
                return
            # _poll() closes the window once the script has exited
            self.closing = True
            self.stop()
            return
        self.root.destroy()

    # --- Updating the window ---

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _update_buttons(self):
        loaded = self.loaded_source is not None
        active = self.runner.active
        stoppable = active and not self.runner.stopping
        self.save_button["state"] = "normal" if loaded else "disabled"
        self.run_button["state"] = "normal" if loaded and not active else "disabled"
        self.stop_button["state"] = "normal" if stoppable else "disabled"

    def _update_video(self):
        if self.video is None:
            return
        image = self.video.take_image()
        if not self.runner.active:
            # Black between runs, including late frames from a run that just ended
            if self.frame_image is not None:
                self.video_label["image"] = ""
                self.frame_image = None
        elif image is not None:
            # base64 text is the form of PNG data every Tk version accepts
            self.frame_image = tk.PhotoImage(
                data=base64.b64encode(image).decode("ascii"), format="png"
            )
            self.video_label["image"] = self.frame_image

    def _poll(self):
        for text in self.runner.poll():
            self._log(text)
        if self.closing and not self.runner.active:
            self.root.destroy()
            return
        self._update_video()
        self._update_buttons()
        self.root.after(POLL_MS, self._poll)
