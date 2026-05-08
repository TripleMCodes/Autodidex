from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class Controls(QWidget):
    """Start / Pause / Stop buttons and reward-type selector."""

    REWARD_OPTIONS = ["None", "Video", "Music", "Image"]

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self._pause_icon_path = base_path / "Icons/icons8-pause-64.png"
        self._continue_icon_path = base_path / "Icons/icons8-continue-64.png"
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # ---- reward selector ----
        self.reward_selector = QComboBox()
        self.reward_selector.addItems(self.REWARD_OPTIONS)
        self.reward_selector.setStyleSheet(self._combo_style())
        layout.addWidget(self.reward_selector)

        # ---- buttons row ----
        btn_row = QHBoxLayout()

        self.start_btn = QPushButton("")
        start_icon = self.base_path / "Icons/icons8-play-64.png"
        self.start_btn.setIcon(QIcon(str(start_icon)))
        self.start_btn.setIconSize(QSize(40, 40))
        self.start_btn.setToolTip("start")
        self.start_btn.setStyleSheet(self._green_btn_style())

        self.pause_btn = QPushButton("")
        self.pause_btn.setIcon(QIcon(str(self._pause_icon_path)))
        self.pause_btn.setIconSize(QSize(40, 40))
        self.pause_btn.setToolTip("pause")
        self.pause_btn.setStyleSheet(
            "QPushButton { padding: 10px 20px; border-radius: 15px; border: none; }"
        )

        self.stop_btn = QPushButton("")
        stop_icon = self.base_path / "Icons/icons8-stop-64.png"
        self.stop_btn.setIcon(QIcon(str(stop_icon)))
        self.stop_btn.setIconSize(QSize(40, 40))
        self.stop_btn.setStyleSheet(self._red_btn_style())

        for btn in (self.start_btn, self.pause_btn, self.stop_btn):
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def set_paused_icon(self, paused: bool):
        icon = self._continue_icon_path if paused else self._pause_icon_path
        self.pause_btn.setIcon(QIcon(str(icon)))

    @property
    def reward(self) -> str:
        return self.reward_selector.currentText()

    # ------------------------------------------------------------------
    @staticmethod
    def _combo_style() -> str:
        return """
            QComboBox {
                background-color: #1e1e2f; color: #ffffff; font-size: 16px;
                padding: 6px 12px; border: 2px solid #ff5c8a; border-radius: 12px;
            }
            QComboBox:hover { border: 2px solid #ff85a2; }
            QComboBox::drop-down {
                border: none; background-color: #ff5c8a;
                border-top-right-radius: 12px; border-bottom-right-radius: 12px; width: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e2f; color: #ffffff;
                selection-background-color: #ff5c8a; padding: 6px; border-radius: 10px;
            }
        """

    @staticmethod
    def _green_btn_style() -> str:
        return """
            QPushButton {
                background-color: #1a4d14; padding: 10px 20px;
                border-radius: 15px; border: none;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1c7430; border-style: inset; }
        """

    @staticmethod
    def _red_btn_style() -> str:
        return """
            QPushButton {
                background-color: #380101; color: white;
                border: 4px solid #b21f2d; font-size: 18px;
                font-weight: bold; padding: 10px;
            }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:pressed { background-color: #a71d2a; border-style: inset; }
        """
