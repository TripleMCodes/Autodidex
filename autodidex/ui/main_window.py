import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QTabWidget, QVBoxLayout, QWidget,
)

from autodidex.services.tab_registry   import build_tab_definitions
from autodidex.services.theme_service  import ThemeService
from autodidex.services.session_watcher import SessionWatcher

from autodidex.ui.settings_tab import SettingsTab, ABOUT_TEXT
from autodidex.ui.exit_button  import make_exit_button
from calender.ui.main_window import  CalendarHeatmap
from habit_tracker.ui.main_window import CPTracker


class Autodidex(QWidget):

    change = Signal(str)
    """
    Thin orchestration shell for the Autodidex tab container.

    Responsibilities:
      - Build and register all tabs via TabRegistry.
      - Own the ThemeService and broadcast theme changes to child widgets.
      - Own the SessionWatcher and reward lumens on new sessions.
      - Wire Settings tab signals.
    """

    def __init__(self):
        super().__init__()
        self._path = Path(__file__).parent.parent.parent

        # ---- services ----
        self._themes = ThemeService(self._path)

        # ---- window chrome ----
        self.setWindowTitle("Autodidex")
        win_icon = self._path / "Icons/icons8-brain-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))

        # ---- build settings tab first (needed by tab registry) ----
        self._settings = SettingsTab(self._path)
        self._settings.theme_btn.clicked.connect(self._toggle_theme)
        self._settings.about_btn.clicked.connect(self._show_about)


        # self._cal = CalendarHeatmap()
        # self.change.connect(self._cal.test_sig)

        self.habit_tracker = CPTracker()
        self.change.connect(self.habit_tracker._toggle_theme)

        # ---- tab widget ----
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.West)
        self._tabs.tabBar().setIconSize(QSize(36, 36))

        # ---- register tabs from registry (single source of truth) ----
        self._tab_widgets: list[QWidget] = []
        for tab_def in build_tab_definitions(self._path, self._settings):
            widget = tab_def.widget_factory()
            self._tab_widgets.append(widget)
            icon_path = self._path / "Icons" / tab_def.icon_filename
            self._tabs.addTab(widget, QIcon(str(icon_path)), "")
            self._tabs.setTabToolTip(
                self._tabs.count() - 1, tab_def.tooltip
            )

        # ---- exit button ----
        exit_btn = make_exit_button(self._path)
        exit_btn.clicked.connect(self._exit)

        # ---- root layout ----
        root = QVBoxLayout(self)
        root.addWidget(self._tabs)
        root.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # ---- session watcher (awards lumens on new Cirillo sessions) ----
        session_file = self._path / "cirillo" / "sessions.csv"
        self._watcher = SessionWatcher(session_file, self._on_new_session)

        # ---- apply saved theme ----
        self._apply_theme()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self._themes.toggle()
        self._apply_theme()
        self.change.emit(self._themes.current_mode)

    def _apply_theme(self):
        """Apply current theme to the shell and all child tab widgets."""
        sheet = self._themes.stylesheet()
        self.setStyleSheet(sheet)
        self._settings.update_theme_icon(self._themes.icon_path())

        # Broadcast to every tab widget that exposes _toggle_theme()
        # Only call if the child's current mode differs from ours so we
        # don't double-toggle widgets that manage their own state.
        for widget in self._tab_widgets:
            if hasattr(widget, "_apply_current_theme"):
                widget._apply_current_theme()
        self.change.emit(self._themes.current_mode)

    # ------------------------------------------------------------------
    # Session watcher callback
    # ------------------------------------------------------------------
    def _on_new_session(self):
        """Called by SessionWatcher when the Cirillo CSV gains a new session row."""
        # Award lumens via the dashboard's bank service if available
        dashboard = next(
            (w for w in self._tab_widgets if hasattr(w, "_bank")), None
        )
        if dashboard:
            dashboard._bank.wallet = 3
        # Uncomment to also refresh the dashboard UI after awarding:
        if dashboard and hasattr(dashboard, "_on_db_ui_update"):
            dashboard._on_db_ui_update()

    # ------------------------------------------------------------------
    # About
    # ------------------------------------------------------------------
    def _show_about(self):
        QMessageBox.information(self, "About Autodidex", ABOUT_TEXT)

    # ------------------------------------------------------------------
    # Exit
    # ------------------------------------------------------------------
    def _exit(self):
        self.close()
        self.destroy()


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Autodidex()
    window.show()
    sys.exit(app.exec())
