import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
