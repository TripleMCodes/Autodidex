from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import QWidget


@dataclass
class TabDefinition:
    """Describes a single tab: what to show, what icon to use, and the tooltip."""
    tooltip:        str
    icon_filename:  str           # relative to Icons/
    widget_factory: Callable[[], QWidget]   # called lazily to build the tab


def build_tab_definitions(base_path: Path, settings_widget: QWidget) -> list[TabDefinition]:
    """
    Single source of truth for every tab in the Autodidex shell.

    To add a new tab, append one TabDefinition here — nothing else needs
    to change in main_window.py.

    Imports are local to each factory so that a broken sub-app doesn't
    prevent the shell from opening at all.
    """

    def _dashboard():
        from dashboard.ui.main_window import MainWindow
        return MainWindow()

    def _habit_tracker():
        from habit_tracker.ui.main_window import CPTracker
        return CPTracker()

    def _cirillo():
        from cirillo.ui.main_window import PomodoroGUI
        return PomodoroGUI()

    def _noteworthy():
        from note_worthy.ui.main_window import NoteWorthy
        return NoteWorthy()

    def _calendar():
        from calender.ui.main_window import CalendarHeatmap
        return CalendarHeatmap()

    def _space_invader():
        from spaceinvader.widget import SpaceInvaderWidget
        return SpaceInvaderWidget()

    def _progress():
        from autodidex_progress.ui.main_window import ProgressWindow
        return ProgressWindow()

    def _browser():
        from browser.ui.browser_widget import BrowserWidget
        return BrowserWidget()

    return [
        TabDefinition("Dashboard",    "icons8-dashboard-64.png",   _dashboard),
        TabDefinition("Habit Tracker","icons8-to-do-list-64.png",  _habit_tracker),
        TabDefinition("Cirillo",      "icons8-pomodoro-50.png",    _cirillo),
        TabDefinition("NoteWorthy",   "icons8-notebook-64.png",    _noteworthy),
        TabDefinition("Calendar",     "icons8-calendar-64.png",    _calendar),
        TabDefinition("Browser",      "icons8-browser-64.png",     _browser),
        TabDefinition("Progress", "icons8-progress-64.png", _progress),
        TabDefinition("Settings",     "icons8-settings-64.png",    lambda: settings_widget),
        TabDefinition("Space Invader","ufo.png", _space_invader),
    ]
