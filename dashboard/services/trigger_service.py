import logging
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QFileSystemWatcher


class TriggerService:
    """
    Watches one or more trigger files and calls a registered callback
    whenever any of them changes.

    Usage:
        svc = TriggerService()
        svc.watch(Path("update.txt"), on_new_cp)
        svc.watch(Path("update_db_ui.txt"), on_db_ui_update)
    """

    def __init__(self):
        self._watcher  = QFileSystemWatcher()
        self._handlers: dict[str, Callable] = {}
        self._watcher.fileChanged.connect(self._dispatch)

    def watch(self, path: Path, callback: Callable):
        """Register *callback* to be called when *path* changes."""
        key = str(path)
        self._handlers[key] = callback
        if path.exists():
            self._watcher.addPath(key)
        else:
            logging.warning(f"TriggerService: path does not exist yet: {path}")

    def _dispatch(self, path: str):
        # QFileSystemWatcher can drop the path after an overwrite — re-add it.
        if path not in self._watcher.files():
            self._watcher.addPath(path)

        handler = self._handlers.get(path)
        if handler:
            logging.debug(f"TriggerService: change detected in {path}")
            handler()
        else:
            logging.warning(f"TriggerService: no handler for {path}")
