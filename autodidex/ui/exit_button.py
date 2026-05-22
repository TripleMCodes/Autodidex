from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton


def make_exit_button(base_path: Path) -> QPushButton:
    """
    Build and return the styled Autodidex exit button.
    Kept here so the gradient style block doesn't clutter main_window.
    """
    btn = QPushButton("")
    icon_path = base_path / "Icons/icons8-power-button-50.png"
    btn.setIcon(QIcon(str(icon_path)))
    btn.setIconSize(QSize(50, 50))
    btn.setToolTip("Exit Autodidex")
    btn.setStyleSheet("""
        QPushButton {
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #D5C8FF,
                stop:1 #BBA9F2
            );
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #E0D4FF;
            border: 1px solid #967BE3;
        }
        QPushButton:pressed {
            background-color: #BFA9FF;
            border: 1px solid #6F54D8;
        }
    """)
    return btn
