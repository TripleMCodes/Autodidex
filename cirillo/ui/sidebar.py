from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget,
)


class Sidebar(QWidget):
    """Left-hand sidebar: music controls, progress, theme toggle, exit."""

    SOUND_OPTIONS = ["None", "lofi", "Forest", "Rain", "Cafe"]

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self.setFixedWidth(200)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        self.setLayout(layout)

        # ---- study music icon label ----
        s_icon = self.base_path / "Icons/icons8-rhythm-48.png"
        self.study_music_label = QLabel(
            f'<div style="text-align:center;">'
            f'<img src="{s_icon}" width="40" height="40"></div>'
        )
        self.study_music_label.setToolTip("study music")
        self.study_music_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.study_music_label.setStyleSheet(
            "QLabel { padding:8px; border-radius:10px; background-color:#D6EAF8; }"
        )

        # ---- sound selector ----
        self.sound_selector = QComboBox()
        self.sound_selector.addItems(self.SOUND_OPTIONS)
        self.sound_selector.setStyleSheet(self._combo_style())

        # ---- volume label ----
        v_icon = self.base_path / "Icons/icons8-volume-48.png"
        self.volume_label = QLabel(
            f'<div style="text-align:center;">'
            f'<img src="{v_icon}" width="40" height="40"></div>'
        )
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- volume slider ----
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet(self._slider_style())

        # ---- progress button ----
        self.progress_btn = QPushButton("")
        p_icon = self.base_path / "Icons/icons8-progress-64.png"
        self.progress_btn.setIcon(QIcon(str(p_icon)))
        self.progress_btn.setIconSize(QSize(30, 30))
        self.progress_btn.setStyleSheet(self._green_btn_style())

        # ---- theme toggle ----
        self.theme_btn = QPushButton("")
        self.theme_btn.setIconSize(QSize(30, 30))
        self.theme_btn.setStyleSheet("")

        # ---- exit button ----
        self.exit_btn = QPushButton("")
        exit_icon = self.base_path / "Icons/icons8-exit-sign-64.png"
        self.exit_btn.setIcon(QIcon(str(exit_icon)))
        self.exit_btn.setIconSize(QSize(30, 30))
        self.exit_btn.setStyleSheet(self._red_btn_style())

        # ---- assemble ----
        for w in (
            self.study_music_label,
            self.sound_selector,
            self.volume_label,
            self.volume_slider,
            self.progress_btn,
            self.theme_btn,
            self.exit_btn,
        ):
            layout.addWidget(w)
        layout.addStretch()

    # ------------------------------------------------------------------
    # Style helpers
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
    def _slider_style() -> str:
        return """
            QSlider::groove:horizontal {
                border: 1px solid #999; height: 8px; background: #444;
                margin: 2px 0; border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00c896; border: 1px solid #5c5c5c;
                width: 18px; margin: -2px 0; border-radius: 9px;
            }
        """

    @staticmethod
    def _green_btn_style() -> str:
        return """
            QPushButton {
                background-color: #1a4d14; color: white; padding: 10px 20px;
                border: 2px solid #3e8e41; border-radius: 20px; font-size: 14px;
            }
            QPushButton:hover { background-color: #45a049; border-color: #388e3c; }
            QPushButton:pressed { background-color: #3e8e41; }
        """

    @staticmethod
    def _red_btn_style() -> str:
        return """
            QPushButton {
                background-color: #380101; color: white; font-size: 16px;
                padding: 8px 16px; border-radius: 10px; border: 2px solid #d43f3a;
            }
            QPushButton:hover { background-color: #ad4e4b; }
            QPushButton:pressed { background-color: #a94442; }
        """
