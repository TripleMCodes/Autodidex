from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,  QLabel,
    QFileDialog, QComboBox, QLineEdit
)
from PySide6.QtCore import QSize

class FlashCardsApp(QWidget):
    
    def __init__(self):
        super().__init__()

        self.main_layout = QHBoxLayout()
        self.setWindowTitle("Flash")
        self.setFixedSize(QSize(500, 50))

        
        

if __name__ == "__main__":
    app = QApplication([])
    window = FlashCardsApp()
    window.show()
    app.exec()