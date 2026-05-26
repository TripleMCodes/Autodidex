from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QWidget

class NotesSide(QWidget):


    def __init__(self, base_path=None, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.test_btn = QPushButton("testing")
        layout.addWidget(self.test_btn)
