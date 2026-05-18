import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QInputDialog,
    QMessageBox, QVBoxLayout, QWidget,
)

from services.habit_service  import HabitService
from services.theme_service  import ThemeService
from services.trigger_service import TriggerService

from ui.sidebar     import Sidebar
from ui.habit_table import HabitTable


class CPTracker(QWidget):
    """
    Thin orchestration shell.

    Responsibilities:
      - Instantiate services and UI sub-widgets.
      - Connect widget signals → service calls.
      - Push service results back into the UI.
    """

    def __init__(self):
        super().__init__()
        self._path = Path(__file__).parent.parent

        # ---- services ----
        self._habits   = HabitService()
        self._themes   = ThemeService(self._path)
        self._triggers = TriggerService(self._path)

        # ---- window chrome ----
        self.setWindowTitle("Cerebral Pursuit Tracker")
        win_icon = self._path / "Icons/icons8-to-do-list-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))
        self.resize(600, 400)

        # ---- row counter (next free row in column 0) ----
        self._counter = 0

        # ---- build layout ----
        self._root = QHBoxLayout(self)

        self._sidebar = Sidebar(self._path)

        self._toggle_btn = self._make_toggle_btn()

        self._table = HabitTable(self._path)

        self._root.addWidget(self._sidebar)
        self._root.addWidget(self._toggle_btn)
        self._root.addWidget(self._table)
        self.setLayout(self._root)

        # ---- wire signals ----
        self._connect_signals()

        # ---- initialise state ----
        # self._init_wrapper()   # uncomment to enable on startup

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------
    def _connect_signals(self):
        # sidebar
        self._sidebar.progress_btn.clicked.connect(self._show_progress)
        self._sidebar.theme_btn.clicked.connect(self._toggle_theme)
        self._sidebar.exit_btn.clicked.connect(lambda: sys.exit())

        # toggle button
        self._toggle_btn.clicked.connect(self._toggle_sidebar)

        # table signals
        self._table.checkbox_toggled.connect(self._on_checkbox_toggled)
        self._table.habit_submitted.connect(self._add_habit)
        self._table.context_edit_requested.connect(self._edit_subject)
        self._table.context_delete_requested.connect(self._delete_subject)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def _init_wrapper(self):
        """Load DB state and handle weekly reset if needed."""
        if self._habits.needs_reset():
            self._counter = self._table.populate_habits(self._habits.get_habits())
            self._table.enable_checkbox_save = True
            msg = self._habits.clear_all_data()
            logging.debug(msg.get("message"))
        else:
            self._counter = self._table.populate_habits(self._habits.get_habits())
            states = self._habits.get_checkbox_states()
            self._table.apply_checkbox_states(states)
            self._table.enable_checkbox_save = True
        self._apply_current_theme()

    # ------------------------------------------------------------------
    # Habit CRUD
    # ------------------------------------------------------------------
    def _add_habit(self, text: str):
        text = text.strip()
        if not text:
            QMessageBox.warning(self, "WARNING", "Enter a valid habit")
            return
        msg = self._habits.add_habit(text)
        if not msg.get("status"):
            QMessageBox.warning(self, "WARNING", msg["message"])
            return
        from PySide6.QtWidgets import QTableWidgetItem
        self._table.table.setItem(self._counter, 0, QTableWidgetItem(text))
        self._counter += 1
        self._table.clear_input()
        QMessageBox.information(self, "Successful", msg["message"])
        self._triggers.notify_dashboard()

    def _edit_subject(self, row: int, old_subject: str):
        new_subject, ok = QInputDialog.getText(
            self, "Edit Subject", "New subject name:", text=old_subject
        )
        if not ok:
            return
        new_subject = new_subject.strip()
        if not new_subject:
            QMessageBox.warning(self, "Warning", "Enter a valid subject name")
            return
        if new_subject == old_subject:
            return
        msg = self._habits.edit_habit(old_subject, new_subject)
        if not msg.get("status"):
            QMessageBox.warning(self, "Warning", msg.get("message", "Failed to rename subject"))
            return
        QMessageBox.information(self, "Success", msg.get("message", "Subject renamed"))
        self._refresh_table()
        self._triggers.notify_dashboard()

    def _delete_subject(self, row: int, subject: str):
        reply = QMessageBox.question(
            self, "Delete Subject",
            f"Delete '{subject}'? This will remove its check marks.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        msg = self._habits.delete_habit(subject)
        if not msg.get("status"):
            QMessageBox.warning(self, "Warning", msg.get("message", "Failed to delete subject"))
            return
        QMessageBox.information(self, "Deleted", msg.get("message", "Subject deleted"))
        self._refresh_table()

    # ------------------------------------------------------------------
    # Checkbox
    # ------------------------------------------------------------------
    def _on_checkbox_toggled(self, row: int, col: int, day: str, subject: str):
        msg = self._habits.save_checkbox(row, col, subject, day)
        logging.debug(msg)
        QMessageBox.information(self, "Message", msg["message"])
        self._triggers.notify_db_ui()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _refresh_table(self):
        habits = self._habits.get_habits()
        self._counter = self._table.populate_habits(habits)

    def _toggle_sidebar(self):
        menu_icon = self._path / "Icons/icons8-menu-48.png"
        x_icon    = self._path / "Icons/icons8-close-64.png"
        if self._sidebar.isVisible():
            self._sidebar.hide()
            self._toggle_btn.setIcon(QIcon(str(menu_icon)))
        else:
            self._sidebar.show()
            self._toggle_btn.setIcon(QIcon(str(x_icon)))

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self._themes.toggle()
        self._apply_current_theme()

    def _apply_current_theme(self):
        self.setStyleSheet(self._themes.stylesheet())
        self._sidebar.theme_btn.setIcon(QIcon(self._themes.icon_path()))

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------
    def _show_progress(self):
        counts = self._habits.get_cp_with_check_marks()
        if not counts:
            QMessageBox.information(self, "Progress", "No data to display yet.")
            return
        habits      = list(counts.keys())
        frequencies = list(counts.values())
        plt.figure(figsize=(10, 6))
        bars = plt.bar(habits, frequencies, color="mediumpurple", edgecolor="black")
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
                     f"{int(h)}", ha="center", va="bottom", fontsize=10)
        plt.title("Habit Completion Frequency", fontsize=16)
        plt.xlabel("Habits", fontsize=12)
        plt.ylabel("Check-ins", fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------
    # Toggle button factory (sits outside the sidebar in the layout)
    # ------------------------------------------------------------------
    def _make_toggle_btn(self):
        x_icon = self._path / "Icons/icons8-close-64.png"
        btn = __import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton("")
        btn.setIcon(QIcon(str(x_icon)))
        btn.setIconSize(QSize(40, 40))
        return btn


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication([])
    window = CPTracker()
    window.show()
    sys.exit(app.exec())
