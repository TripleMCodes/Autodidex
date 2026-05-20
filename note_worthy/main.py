import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import NoteWorthy


def main():
    app = QApplication([])
    window = NoteWorthy()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
