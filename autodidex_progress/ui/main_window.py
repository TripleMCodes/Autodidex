from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QInputDialog,
    QMessageBox, QVBoxLayout, QWidget, QLabel,
)

from habit_tracker.ui.habit_chart import HabitBarChartWidget
from calender.ui.streak_tracker       import StreakTracker
from calender.ui.main_window import SESSIONS_FILE
from habit_tracker.services.habit_service  import HabitService


class ProgressWindow(QWidget):
    """
    Main window: habit chart + streak label + heatmap + theme toggle.

    All data access goes through SessionReader; all theme logic goes
    through ThemeService.  The window itself only wires and reacts.
    """

    def __init__(self):
        super().__init__()
        self._path = Path(__file__).parent.parent.parent

        # ---- window chrome ----
        self.setWindowTitle("Autodidex Progress")
        self.resize(400, 300)
        self._habits   = HabitService()


        # ---- build UI ----
        layout = QVBoxLayout(self)
        heat_map_label = QLabel("Pomodoro Sessions' Heatmap")
        heat_map_label.setAlignment(Qt.AlignCenter)
        heat_map_label.setStyleSheet(
            "font-size: 13px;"
            "font-weight: bold;"
            
            "margin-top: 6px;"
            "margin-bottom: 4px;"
        )

        # habit chart
        self._habit_chart = HabitBarChartWidget()
        layout.addWidget(self._habit_chart)
        layout.addWidget(heat_map_label, alignment=Qt.AlignCenter)
        self._streak = StreakTracker(SESSIONS_FILE)
        # heatmap (owns its own file watcher)
        
        layout.addWidget(self._streak)

        self.load_progress()

    def load_progress(self):
        print(f"self._habits is: {self._habits}")
        self._habit_chart.load_from(self._habits)