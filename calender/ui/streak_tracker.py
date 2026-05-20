import logging
from datetime import date
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtWidgets import QVBoxLayout, QWidget

from calender.services.session_reader import SessionReader
from calender.ui.heatmap_widget import HeatmapWidget


class StreakTracker(QWidget):
    """
    Watches the Cirillo sessions CSV for changes and rebuilds
    the HeatmapWidget whenever new data is detected.

    Owns the SessionReader and the file watcher — HeatmapWidget
    stays a pure visual component that only receives parsed data.
    """

    def __init__(self, sessions_file: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub-Style Streak Tracker")
        self.resize(800, 250)

        self._reader    = SessionReader(sessions_file)
        self._layout    = QVBoxLayout(self)
        self._heatmap: HeatmapWidget | None = None

        self.study_data: dict[date, int] = {}

        # Watch the CSV for live updates
        self._watcher = QFileSystemWatcher()
        if sessions_file.exists():
            self._watcher.addPath(str(sessions_file))
        self._watcher.fileChanged.connect(self._on_file_changed)

        self._reload()

    # ------------------------------------------------------------------
    def _on_file_changed(self, path: str):
        """Re-add the path (it can be dropped on overwrite) then reload."""
        logging.debug(f"StreakTracker: detected change in {path}")
        if not self._watcher.files():
            self._watcher.addPath(path)
        self._reload()

    def _reload(self):
        new_data = self._reader.load_study_data()
        if new_data == self.study_data:
            return                              # nothing actually changed
        self.study_data = new_data
        start, end = self._reader.load_date_range()
        self._rebuild_heatmap(start, end)

    def _rebuild_heatmap(self, start_date: date, end_date: date):
        if self._heatmap:
            self._layout.removeWidget(self._heatmap)
            self._heatmap.setParent(None)
        self._heatmap = HeatmapWidget(self.study_data, start_date, end_date)
        self._layout.addWidget(self._heatmap)
