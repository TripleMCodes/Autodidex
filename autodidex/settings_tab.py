from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout, QPushButton, QVBoxLayout, QWidget,
)

from dashboard.ui.spinning_label import SpinningLabel


ABOUT_TEXT = (
    "📘 **Autodidex** — A Toolkit for the Self-Taught Mind\n\n"
    "Crafted with passion and purpose by Connor Connorson, Autodidex is an all-in-one "
    "productivity suite designed for autodidacts, creatives, and knowledge-hunters who "
    "believe learning never stops.\n\n"
    "📌 **What's Inside:**\n"
    "• 🧠 Habit Tracker — Build better routines\n"
    "• ⏳ Pomodoro Timer — Stay sharp, stay focused\n"
    "• 📝 NoteWorthy — Take notes that matter\n"
    "• 📆 Calendar Heatmap — Visualize your grind\n"
    "• 🎮 Dashboard + Minigames — Because learning should be fun\n\n"
    "💡 Whether you're mastering code, philosophy, languages, or just life itself, "
    "Autodidex is your digital companion on the quest for personal mastery.\n\n"
    "🛠️ Made with PySide6 and relentless curiosity.\n\n"
    "📬 Contact: khona6047@gmail.com\n"
    "🚀 Keep learning. Keep creating. Stay worthy."
)


class SettingsTab(QWidget):
    """
    Settings tab content.

    Exposes:
        theme_btn   — main_window connects this to the theme toggle
        about_btn   — main_window connects this to the about dialog
    """

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self._base_path = base_path
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        label  = SpinningLabel("⚙️ Settings")
        label.setObjectName("onloadlabel")
        header.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(header)

        # Buttons row
        btn_row = QHBoxLayout()

        self.theme_btn = QPushButton("")
        self.theme_btn.setIconSize(QSize(30, 30))

        win_icon = self._base_path / "Icons/icons8-brain-64.png"
        self.about_btn = QPushButton("About Autodidex")
        self.about_btn.setIcon(QIcon(str(win_icon)))
        self.about_btn.setIconSize(QSize(30, 30))

        for btn in (self.theme_btn, self.about_btn):
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    def update_theme_icon(self, icon_path: str):
        self.theme_btn.setIcon(QIcon(icon_path))
