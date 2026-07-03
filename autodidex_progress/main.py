import sys
from PySide6.QtWidgets import QApplication
from autodidex_progress.ui.main_window import ProgressWindow

def main():
    app = QApplication([])
    window = ProgressWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()