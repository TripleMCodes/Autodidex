from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    """
    Collapsible left-hand sidebar.
    Exposes: progress_btn, theme_btn, exit_btn.
    The toggle button lives *outside* this widget (in the main layout)
    so it stays visible when the sidebar is hidden.
    """

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self.setFixedWidth(200)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        p_icon = self.base_path / "Icons/icons8-progress-64.png"
        self.progress_btn = QPushButton("")
        self.progress_btn.setIcon(QIcon(str(p_icon)))
        self.progress_btn.setIconSize(QSize(30, 30))
        self.progress_btn.setToolTip("progress")

        self.theme_btn = QPushButton("")
        self.theme_btn.setIconSize(QSize(30, 30))

        exit_icon = self.base_path / "Icons/icons8-exit-sign-64.png"
        self.exit_btn = QPushButton("")
        self.exit_btn.setIcon(QIcon(str(exit_icon)))
        self.exit_btn.setIconSize(QSize(30, 30))
        self.exit_btn.setToolTip("exit")

        for btn in (self.progress_btn, self.theme_btn, self.exit_btn):
            layout.addWidget(btn)
