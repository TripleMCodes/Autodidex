from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from dashboard.ui.spinning_label import SpinningLabel


class OnloadScreen(QWidget):
    """
    Splash screen shown when no user is registered yet.

    Emits:
        name_submitted(str)  — when the user confirms their name
    """

    name_submitted = Signal(str)

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self._build_ui(base_path)

    def _build_ui(self, base_path: Path):
        layout = QVBoxLayout(self)

        self._label = SpinningLabel("Autodidex")
        self._label.setObjectName("onloadlabel")
        layout.addWidget(self._label)

        row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter your name")
        self._input.returnPressed.connect(self._submit)

        enter_icon = base_path / "Icons/icons8-enter-64.png"
        self._btn = QPushButton("")
        self._btn.setIcon(QIcon(str(enter_icon)))
        self._btn.setIconSize(QSize(30, 30))
        self._btn.clicked.connect(self._submit)

        row.addWidget(self._input)
        row.addWidget(self._btn)
        layout.addLayout(row)

    def _submit(self):
        name = self._input.text().strip()
        if name:
            self.name_submitted.emit(name)
