import sys
from PySide6.QtWidgets import QApplication
from calender.ui.main_window import CalendarHeatmap


def main():
    app = QApplication([])
    window = CalendarHeatmap()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
