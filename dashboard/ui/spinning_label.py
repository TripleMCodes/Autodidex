import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QRadialGradient, QTransform,
)
from PySide6.QtWidgets import QLabel


class SpinningLabel(QLabel):
    """
    A QLabel that renders its text with a simulated 3D x-axis spin
    over a white-to-purple radial gradient background.

    Fully self-contained — no external dependencies.
    """

    SPIN_SPEED_MS = 30   # timer interval
    SPIN_STEP_DEG = 2    # degrees per tick

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 80, QFont.Bold))
        self._angle = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.SPIN_SPEED_MS)

    # ------------------------------------------------------------------
    def _tick(self):
        self._angle = (self._angle + self.SPIN_STEP_DEG) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Radial gradient: white centre → purple edge
        gradient = QRadialGradient(self.width() / 2, self.height() / 2, self.width() / 1.5)
        gradient.setColorAt(0, QColor("white"))
        gradient.setColorAt(1, QColor(128, 0, 128))
        painter.fillRect(self.rect(), QBrush(gradient))

        # Simulate 3D spin by scaling x-axis with cosine
        scale = math.cos(math.radians(self._angle))
        transform = QTransform()
        transform.translate(self.width() / 2, self.height() / 2)
        transform.scale(scale, 1)
        transform.translate(-self.width() / 2, -self.height() / 2)
        painter.setTransform(transform)

        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
