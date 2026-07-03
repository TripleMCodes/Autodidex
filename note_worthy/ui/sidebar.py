from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    """
    Collapsible left-hand sidebar containing all editor action buttons
    and the font-size selector.

    Exposes every button as a public attribute so main_window can connect
    signals without knowing anything about the layout.
    """

    FONT_SIZES = ["10", "12", "14", "16", "18", "20", "22", "24", "26"]

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        # self.setFixedWidth(200)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        def _btn(icon_name: str, tooltip: str) -> QPushButton:
            btn = QPushButton("")
            btn.setIcon(QIcon(str(self.base_path / icon_name)))
            btn.setIconSize(QSize(30, 30))
            btn.setToolTip(tooltip)
            return btn

        self.file_btn    = _btn("Icons/icons8-new-document-48.png", "open file")
        self.theme_btn   = _btn("Icons/icons8-dark-mode-48.png",    "theme")
        self.theme_btn.setIconSize(QSize(30, 30))

        self.font_size_box = QComboBox()
        self.font_size_box.addItems(self.FONT_SIZES)
        self.font_size_box.setCurrentText("14")

        self.copy_btn    = _btn("Icons/icons8-copy-64.png",         "copy")
        self.cut_btn     = _btn("Icons/icons8-cut-48.png",          "cut")
        self.paste_btn   = _btn("Icons/icons8-paste-64.png",        "paste")
        self.save_btn    = _btn("Icons/icons8-save-64.png",         "save")
        self.md_btn      = _btn("Icons/icons8-markdown-64.png",     "markdown preview")

        widgets = [
            self.file_btn,
            self.theme_btn,
            self.font_size_box,
            self.save_btn,
            self.md_btn,
        ]
        for w in widgets:
            layout.addWidget(w)
            