from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget,
)


class TimerDisplay(QWidget):
    """Large countdown label plus work / break duration spinboxes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # ---- big clock ----
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 150px; font-weight: bold; color: white;
                background-color: #FF5555; border-radius: 100px;
                border: 4px solid #AA0000;
                qproperty-alignment: 'AlignCenter';
            }
        """)
        layout.addWidget(self.timer_label)

        # ---- time inputs row ----
        row = QHBoxLayout()

        work_label = QLabel("Work Duration:")
        work_label.setStyleSheet(self._input_label_style())

        self.work_input = QSpinBox()
        self.work_input.setSuffix(" min")
        self.work_input.setRange(1, 180)
        self.work_input.setValue(25)
        self.work_input.setStyleSheet(self._spinbox_style())

        break_label = QLabel("Break Duration:")
        break_label.setStyleSheet(self._input_label_style())

        self.break_input = QSpinBox()
        self.break_input.setSuffix(" min")
        self.break_input.setRange(1, 60)
        self.break_input.setValue(5)
        self.break_input.setStyleSheet(self._spinbox_style())

        for w in (work_label, self.work_input, break_label, self.break_input):
            row.addWidget(w)
        layout.addLayout(row)

    # ------------------------------------------------------------------
    def set_time(self, mins: int, secs: int):
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

    def reset(self):
        self.timer_label.setText("00:00")

    @property
    def work_duration(self) -> int:
        return self.work_input.value()

    @property
    def break_duration(self) -> int:
        return self.break_input.value()

    # ------------------------------------------------------------------
    @staticmethod
    def _input_label_style() -> str:
        return """
            QLabel {
                color: #00ffcc; font-size: 18px; font-weight: bold;
                padding: 4px 10px; border-left: 3px solid #00ffcc;
                background-color: rgba(0,255,204,0.05);
                border-radius: 6px; margin-bottom: 5px;
            }
        """

    @staticmethod
    def _spinbox_style() -> str:
        return """
            QSpinBox {
                background-color: #222; color: #fff; border: 2px solid #555;
                border-radius: 10px; padding: 5px 10px; font-size: 16px;
            }
            QSpinBox::up-button {
                subcontrol-origin: border; subcontrol-position: top right;
                width: 20px; background-color: #444;
                border-left: 1px solid #555; border-bottom: 1px solid #555;
                border-top-right-radius: 8px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border; subcontrol-position: bottom right;
                width: 20px; background-color: #444;
                border-left: 1px solid #555; border-top: 1px solid #555;
                border-bottom-right-radius: 8px;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow { image: none; }
            QSpinBox:hover { border: 2px solid #777; }
            QSpinBox:focus { border: 2px solid #00bfff; outline: none; }
        """
