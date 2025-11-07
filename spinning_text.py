from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QFont, QLinearGradient, QRadialGradient, QBrush, QColor, QTransform

import sys
import math

class SpinningLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 80, QFont.Bold))
        self.angle = 0

        # Timer to simulate 3D spin
        self.timer = QTimer()
        self.timer.timeout.connect(self.spin)
        self.timer.start(30)  # Spin speed

    def spin(self):
        self.angle += 2
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create radial gradient (white to purple)
        gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()/1.5)
        gradient.setColorAt(0, QColor("white"))
        gradient.setColorAt(1, QColor(128, 0, 128))  # Purple
        painter.fillRect(self.rect(), QBrush(gradient))

        # Simulate 3D spin using scaling on the x-axis
        transform = QTransform()
        scale = math.cos(math.radians(self.angle))
        transform.translate(self.width()/2, self.height()/2)
        transform.scale(scale, 1)
        transform.translate(-self.width()/2, -self.height()/2)
        painter.setTransform(transform)

        # Draw the text
        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex Spin Magic 🌌")
        # self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        label = SpinningLabel("Autodidext")
        layout.addWidget(label)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
