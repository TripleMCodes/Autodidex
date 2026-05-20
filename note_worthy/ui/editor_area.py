from pathlib import Path

from markdown import markdown
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSplitter, QTextEdit, QVBoxLayout, QWidget,
)

from note_worthy.ui.spell_check_edit import SpellCheckTextEdit


class EditorArea(QWidget):
    """
    The right-hand content area containing:
      - a splitter with the spell-checked editor (and optional MD preview)
      - a word-count label
      - a dictionary lookup panel (input + button + output label)

    Signals:
        text_changed()              – proxy from the text editor
        definition_requested(word)  – emitted when the search button is clicked
    """

    text_changed          = Signal()
    definition_requested  = Signal(str)

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path  = base_path
        self._md_mode   = False
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # ---- splitter + editor ----
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setMinimumSize(QSize(500, 500))

        self.text_edit = SpellCheckTextEdit()
        self.text_edit.setPlaceholderText("Type your notes here...")
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.textChanged.connect(self.text_changed.emit)
        self.splitter.addWidget(self.text_edit)

        layout.addWidget(self.splitter)

        # ---- word count ----
        wc_icon = self.base_path / "Icons/icons8-word-file-64.png"
        self._wc_icon_path = str(wc_icon)
        self.word_count_label = QLabel(
            f'<img src="{self._wc_icon_path}" width="40" height="40">'
            f'<span style="font-size:20px;"> ⁚ 0</span>'
        )
        self.word_count_label.setToolTip("word count")
        layout.addWidget(self.word_count_label)

        # ---- dictionary panel ----
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word for definition...")
        layout.addWidget(self.word_input)

        enter_icon = self.base_path / "Icons/icons8-enter-64.png"
        self.search_btn = QPushButton("")
        self.search_btn.setIcon(QIcon(str(enter_icon)))
        self.search_btn.setIconSize(QSize(30, 30))
        self.search_btn.clicked.connect(
            lambda: self.definition_requested.emit(self.word_input.text())
        )
        layout.addWidget(self.search_btn)

        self.definition_label = QLabel()
        self.definition_label.setWordWrap(True)
        self.definition_label.setMinimumSize(14, 18)
        layout.addWidget(self.definition_label)

    # ------------------------------------------------------------------
    # Public helpers called by main_window
    # ------------------------------------------------------------------
    def update_word_count(self):
        count = len(self.text_edit.toPlainText().split())
        self.word_count_label.setText(
            f'<img src="{self._wc_icon_path}" width="40" height="40">'
            f'<span style="font-size:20px;"> ⁚ {count}</span>'
        )

    def show_definition(self, text: str):
        self.definition_label.setText(text)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def set_text(self, text: str):
        self.text_edit.setText(text)

    def set_font_size(self, size: int):
        font = QFont("Arial", size)
        self.text_edit.setFont(font)
        # also apply to the MD preview panel if open
        count = self.splitter.count()
        if count > 1:
            self.splitter.widget(count - 1).setFont(font)

    def toggle_markdown_preview(self):
        """Show or hide the side-by-side markdown preview panel."""
        count = self.splitter.count()
        if count == 1:
            preview = QTextEdit()
            preview.setReadOnly(True)
            self.splitter.addWidget(preview)
            self._md_mode = True
            self._refresh_preview()
            self._refresh_preview()   # double-refresh matches original behaviour
        else:
            self.splitter.widget(count - 1).setParent(None)
            self._md_mode = False

    def refresh_markdown(self):
        """Called on every text change when MD mode is active."""
        if self._md_mode:
            self._refresh_preview()

    # ------------------------------------------------------------------
    def _refresh_preview(self):
        count = self.splitter.count()
        if count > 1:
            html = markdown(self.text_edit.toPlainText())
            self.splitter.widget(count - 1).setText(html)
