from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout,
    QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
import sys


class CollapsibleSidebar(QWidget):
    def __init__(self):
        super().__init__()

        # --- main layout ---
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- sidebar frame ---
        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #CFC4EF;
                border-right: 1px solid #A89AD8;
            }
            QPushButton {
                background-color: #BBA9F2;
                border: none;
                padding: 6px;
                margin: 4px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #C9BBFF;
            }
        """)

        # sidebar content layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)

        sidebar_layout.addWidget(QPushButton("Home"))
        sidebar_layout.addWidget(QPushButton("Library"))
        sidebar_layout.addWidget(QPushButton("Settings"))
        sidebar_layout.addWidget(QPushButton("About"))
        sidebar_layout.addStretch()

        # --- toggle button ---
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        # --- main content ---
        self.content = QFrame()
        self.content.setStyleSheet("""
            QFrame {
                background-color: #F5F1FF;
            }
        """)
        content_layout = QVBoxLayout(self.content)
        content_layout.addWidget(QLabel("Main Content Area", alignment=Qt.AlignCenter))

        # --- place widgets ---
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content)

        # floating toggle button (optional)
        self.toggle_btn.setParent(self.content)
        self.toggle_btn.move(10, 10)

        # animation
        self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.sidebar_expanded = True

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            # collapse
            self.animation.setStartValue(self.sidebar.width())
            self.animation.setEndValue(0)
            self.animation.start()
            self.sidebar_expanded = False
        else:
            # expand
            self.animation.setStartValue(self.sidebar.width())
            self.animation.setEndValue(200)
            self.animation.start()
            self.sidebar_expanded = True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Collapsible Sidebar Example")
        layout = QVBoxLayout(self)
        layout.addWidget(CollapsibleSidebar())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.resize(960, 600)
    window.show()
    sys.exit(app.exec())
