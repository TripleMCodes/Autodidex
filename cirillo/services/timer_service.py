import datetime
import logging
from typing import Callable, Optional

from PySide6.QtCore import QTimer, Signal


class TimerService:
    
    """
    Pure-logic Pomodoro state machine.

    Emits callbacks so the UI can react without this service knowing
    anything about widgets.

    Callbacks (all optional, set as attributes):
        on_tick(mins: int, secs: int)       – called every second while running
        on_work_complete()                  – work session finished
        on_break_complete()                 – break finished
    """


    def __init__(self):
        self._qtimer = QTimer()
        self._qtimer.timeout.connect(self._tick)

        self.mode: str = "Work"           # "Work" | "Break"
        self.paused: bool = False
        self.end_time: Optional[datetime.datetime] = None
        self.remaining: Optional[datetime.timedelta] = None

        # Session counters
        self.sessions_this_run: int = 0   # resets on quit
        self.sessions_tracker: int = 0    # triggers long-break every 4
        self.time_studied_mins: int = 120 # accumulates across sessions

        # Callbacks – assign from outside
        self.on_tick: Optional[Callable[[int, int], None]] = None
        self.on_work_complete: Optional[Callable[[], None]] = None
        self.on_break_complete: Optional[Callable[[], None]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start_work(self, duration_mins: int):
        """Start (or restart) a work session."""
        self.mode = "Work"
        self.paused = False
        self._start(duration_mins)

    def start_break(self, duration_mins: int):
        """Start a break session."""
        self.mode = "Break"
        self.paused = False
        self._start(duration_mins)

    def toggle_pause(self):
        """Pause or resume the running timer. Returns new paused state."""
        if self.end_time is None:
            return self.paused
        if not self.paused:
            self.remaining = self.end_time - datetime.datetime.now()
            self._qtimer.stop()
            self.paused = True
        else:
            self.end_time = datetime.datetime.now() + self.remaining
            self._qtimer.start(1000)
            self.paused = False
        return self.paused

    def stop(self):
        """Hard-stop; resets session counters."""
        self._qtimer.stop()
        self.end_time = None
        self.paused = False
        self.mode = "Work"
        self.sessions_this_run = 0

    def is_running(self) -> bool:
        return self.end_time is not None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _start(self, duration_mins: int):
        self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration_mins)
        self._qtimer.start(1000)

    def _tick(self):
        remaining = self.end_time - datetime.datetime.now()
        if remaining.total_seconds() <= 0:
            self._qtimer.stop()
            self._handle_complete()
        else:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            if self.on_tick:
                self.on_tick(mins, secs)

    def _handle_complete(self):
        if self.mode == "Work":
            self.sessions_this_run += 1
            self.sessions_tracker += 1
            logging.debug(f"Work session complete. tracker={self.sessions_tracker}")
            if self.on_work_complete:
                self.on_work_complete()
        else:
            logging.debug("Break complete.")
            if self.on_break_complete:
                self.on_break_complete()

    # ------------------------------------------------------------------
    # Helpers used by the window
    # ------------------------------------------------------------------
    def needs_long_break(self) -> bool:
        return self.sessions_tracker % 4 == 0 and self.sessions_tracker != 0


   