"""Runs a robot script in its own process for a settings window."""

import os
import queue
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

STOP_TIMEOUT_S = 5  # How long Stop waits for a clean exit before force-killing


class ScriptRunner:
    """Runs the robot script in its own process and collects its output.

    A separate process keeps the script's OpenCV camera window from fighting
    with the settings window over the main thread.
    """

    def __init__(self, script_path, stop_timeout=STOP_TIMEOUT_S):
        self.script_path = Path(script_path)
        self.stop_timeout = stop_timeout
        self.proc = None
        self._output = queue.Queue()
        self._stop_deadline = None
        self._killed = False

    @property
    def active(self):
        """True from start() until poll() has reported that the script exited."""
        return self.proc is not None

    @property
    def stopping(self):
        return self.proc is not None and self._stop_deadline is not None

    def start(self, extra_env=None):
        if self.active:
            raise RuntimeError("the script is already running")
        # Windows can only deliver Ctrl+Break to a child in its own process group
        flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        self.proc = subprocess.Popen(
            # The Python running this window is the project's, so it has the
            # script's packages; -u so output shows up in the log right away
            [sys.executable, "-u", str(self.script_path)],
            cwd=self.script_path.parent,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
            # Otherwise Windows uses its local code page, and printing
            # non-English text (a face name, a seen word) could crash the script
            env={**os.environ, "PYTHONIOENCODING": "utf-8", **(extra_env or {})},
            creationflags=flags,
        )
        self._stop_deadline = None
        self._killed = False
        self._reader = threading.Thread(
            target=self._read_output, args=(self.proc.stdout,), daemon=True
        )
        self._reader.start()

    def _read_output(self, stream):
        for line in stream:
            self._output.put(line)
        stream.close()

    def request_stop(self):
        """Asks the script to stop cleanly; it stops the wheels on its way out."""
        if self.proc is None or self.proc.poll() is not None or self.stopping:
            return
        self._stop_deadline = time.monotonic() + self.stop_timeout
        try:
            if sys.platform == "win32":
                self.proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.proc.send_signal(signal.SIGINT)
        except OSError:
            # e.g. Windows without a console window to send Ctrl+Break through
            self._kill()

    def _kill(self):
        self.proc.kill()
        self._killed = True
        self._output.put(
            "--- The script didn't stop in time and was force-killed. "
            "The robot may still be moving! ---\n"
        )

    def poll(self):
        """Returns new log text. Call regularly while active."""
        if self.proc is None:
            return []
        if (
            self.stopping
            and not self._killed
            and self.proc.poll() is None
            and time.monotonic() > self._stop_deadline
        ):
            self._kill()

        texts = []
        while True:
            try:
                texts.append(self._output.get_nowait())
            except queue.Empty:
                break

        # Only finished once the reader has passed on everything the script printed
        if (
            self.proc.poll() is not None
            and not self._reader.is_alive()
            and self._output.empty()
        ):
            texts.append(f"--- Script exited (code {self.proc.returncode}) ---\n")
            self.proc = None
        return texts
