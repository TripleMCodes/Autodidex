"""
ui/nav_bar.py

Toolbar strip for a single browser tab — back/forward/reload/stop,
a URL bar, and a thin progress indicator. Purely presentational; it
emits signals and lets BrowserTab decide what to do with them.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QToolButton, QLineEdit, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Signal, Qt


class NavBar(QWidget):
    back_clicked = Signal()
    forward_clicked = Signal()
    reload_clicked = Signal()
    stop_clicked = Signal()
    url_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 0)
        layout.setSpacing(4)

        self.back_btn = QToolButton(text="\u2190")     # ←
        self.forward_btn = QToolButton(text="\u2192")  # →
        self.reload_btn = QToolButton(text="\u21bb")   # ↻
        self.stop_btn = QToolButton(text="\u2715")     # ✕

        for btn in (self.back_btn, self.forward_btn, self.reload_btn, self.stop_btn):
            btn.setAutoRaise(True)
            layout.addWidget(btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search…")
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.url_bar, stretch=1)

        self.back_btn.clicked.connect(self.back_clicked)
        self.forward_btn.clicked.connect(self.forward_clicked)
        self.reload_btn.clicked.connect(self.reload_clicked)
        self.stop_btn.clicked.connect(self.stop_clicked)
        self.url_bar.returnPressed.connect(
            lambda: self.url_submitted.emit(self.url_bar.text().strip())
        )

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 100)
        self.progress.hide()

    def set_url_text(self, text: str) -> None:
        if not self.url_bar.hasFocus():
            self.url_bar.setText(text)

    def set_progress(self, percent: int) -> None:
        if percent >= 100:
            self.progress.hide()
        else:
            self.progress.show()
            self.progress.setValue(percent)

    def set_nav_enabled(self, can_back: bool, can_forward: bool) -> None:
        self.back_btn.setEnabled(can_back)
        self.forward_btn.setEnabled(can_forward)