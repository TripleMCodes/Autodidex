import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCalendarWidget, QLabel, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)

from calender.services.session_reader import SessionReader
from calender.services.theme_service  import ThemeService
from calender.ui.streak_tracker       import StreakTracker
from calender.ui.heatmap_widget import HeatmapWidget
from calender.ui.reminder_panel import ReminderPanel


SESSIONS_FILE = Path(__file__).parent.parent.parent / "cirillo/sessions.csv"


class CalendarHeatmap(QWidget):
    """
    Main window: calendar + streak label + heatmap + theme toggle.

    All data access goes through SessionReader; all theme logic goes
    through ThemeService.  The window itself only wires and reacts.
    """

    def __init__(self):
        super().__init__()
        self._path = Path(__file__).parent.parent.parent

        # ---- services ----
        self._themes  = ThemeService(self._path)
        self._reader  = SessionReader(SESSIONS_FILE)

        # ---- window chrome ----
        self.setWindowTitle("Autodidex Streak Calendar")
        self.resize(400, 300)

        # ---- build UI ----
        layout = QVBoxLayout(self)

        panel = ReminderPanel()
        layout.addWidget(panel)

        # theme toggle
        self._theme_btn = QPushButton("")
        self._theme_btn.setIconSize(QSize(30, 30))
        self._theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self._theme_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # ---- apply saved theme ----
        self._apply_current_theme()

    # ------------------------------------------------------------------
    def _on_date_selected(self, qdate: QDate):
        """Show the session count for the clicked day."""
        py_date = qdate.toPython()
        count   = self._streak.study_data.get(py_date)
        if count is not None:
            self._label.setText(
                f"Shows streak from {self._reader.load_first_date()} to {date.today()}\n"
                f"Sessions on {qdate.toString('dddd, MMMM d, yyyy')}: {count}"
            )
        else:
            QMessageBox.information(
                self,
                "Streak not found",
                f"There is no streak on {qdate.toString('dddd, MMMM d, yyyy')}",
            )

    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self._themes.toggle()
        self._apply_current_theme()

    def _apply_current_theme(self):
        self.setStyleSheet(self._themes.stylesheet())
        self._theme_btn.setIcon(QIcon(self._themes.icon_path()))


    def test_sig(self):
        print("this worked")


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication([])
    window = CalendarHeatmap()
    window.show()
    sys.exit(app.exec())
