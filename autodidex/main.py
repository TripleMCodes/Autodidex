import sys
from PySide6.QtWidgets import QApplication
from autodidex.ui.main_window import Autodidex


def main():
    app = QApplication(sys.argv)
    window = Autodidex()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
