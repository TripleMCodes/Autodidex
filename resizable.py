from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QSplitter
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class ResizableCollapsibleEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VS Code Style Terminal Panel")
        self.resize(600, 400)

        main_layout = QVBoxLayout(self)

        # --- Splitter (like VS Code resizable panel) ---
        self.splitter = QSplitter(Qt.Vertical)  # Vertical split: top/bottom
        main_layout.addWidget(self.splitter)

        # --- Main Content (Top) ---
        self.top_area = QTextEdit("Main Editor Area\nImagine your code here...")
        self.splitter.addWidget(self.top_area)

        # --- Resizable Bottom Panel (QTextEdit as terminal/log) ---
        self.bottom_panel = QTextEdit("Your 'terminal' or lyric ideas appear here...")
        self.splitter.addWidget(self.bottom_panel)

        # Initial panel sizes
        self.splitter.setSizes([300, 100])  # Top bigger than bottom

        # --- Toggle Button ---
        self.toggle_btn = QPushButton("Collapse / Expand Bottom Panel")
        self.toggle_btn.clicked.connect(self.toggle_bottom_panel)
        main_layout.addWidget(self.toggle_btn)

        # --- Animation for smooth collapse ---
        self.anim = QPropertyAnimation(self.bottom_panel, b"maximumHeight")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.collapsed = False

    def toggle_bottom_panel(self):
        if self.collapsed:
            # Expand
            self.anim.setStartValue(self.bottom_panel.maximumHeight())
            self.anim.setEndValue(150)  # Expanded height
            self.anim.start()
        else:
            # Collapse
            self.anim.setStartValue(self.bottom_panel.height())
            self.anim.setEndValue(0)  # Fully collapsed
            self.anim.start()
        self.collapsed = not self.collapsed


if __name__ == "__main__":
    app = QApplication([])
    window = ResizableCollapsibleEditor()
    window.show()
    app.exec()
