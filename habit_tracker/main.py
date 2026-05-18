import sys
from PySide6.QtWidgets import QApplication
from habit_tracker.ui.main_window import CPTracker


def main():
    app = QApplication([])
    window = CPTracker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
