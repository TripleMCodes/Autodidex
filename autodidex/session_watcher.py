import csv
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QFileSystemWatcher


class SessionWatcher:
    """
    Watches the Cirillo sessions CSV for new entries.
    When the session count increases, calls `on_new_session` so the
    caller can award lumens or refresh the UI.

    The original awarded lumens directly inside the Autodidex widget —
    extracted here so the shell class has no CSV knowledge.
    """

    def __init__(self, session_file: Path, on_new_session: callable):
        self._file            = session_file
        self._on_new_session  = on_new_session
        self._last_count: int = self._read_session_count() or 0

        self._watcher = QFileSystemWatcher()
        if session_file.exists():
            self._watcher.addPath(str(session_file))
        self._watcher.fileChanged.connect(self._on_file_changed)

    # ------------------------------------------------------------------
    def _on_file_changed(self, path: str):
        # QFileSystemWatcher can drop the path after an overwrite — re-add it
        if path not in self._watcher.files():
            self._watcher.addPath(path)

        new_count = self._read_session_count()
        if new_count is not None and new_count > self._last_count:
            self._last_count = new_count
            self._on_new_session()

    def _read_session_count(self) -> Optional[int]:
        """Return the session count from the last row of the CSV, or None."""
        try:
            with open(self._file, "r") as f:
                rows = list(csv.DictReader(f))
            if rows:
                return int(rows[-1]["sessions"])
        except (FileNotFoundError, KeyError, ValueError) as e:
            logging.debug(f"SessionWatcher: could not read count: {e}")
        return None
