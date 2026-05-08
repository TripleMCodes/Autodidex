import sys
from PySide6.QtWidgets import QApplication
from cirillo.ui.main_window import PomodoroGUI


def main():
    app = QApplication(sys.argv)
    window = PomodoroGUI()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
