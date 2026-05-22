import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import Autodidex


def main():
    app = QApplication(sys.argv)
    window = Autodidex()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
