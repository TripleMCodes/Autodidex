from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QThread, Signal
import threading
import space_invader

class SpaceInvaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Space Invader")
        layout = QVBoxLayout()
        self.start_btn = QPushButton("Start Space Invader")
        layout.addWidget(self.start_btn)
        self.setLayout(layout)
        self.start_btn.clicked.connect(self.run_game)

    def run_game(self):
        # Run the game in a separate thread to avoid blocking the UI
        threading.Thread(target=space_invader.main, daemon=True).start()
        self.start_btn.clicked.disconnect(self.run_game)