"""
main.py

Standalone runner to sanity-check the browser widget in isolation
before wiring it into the Autodidex shell.

Run with:  python main_demo.py
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
from PySide6.QtGui import QAction

from browser.ui.browser_widget import BrowserWidget


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex — Browser")
        self.resize(1100, 750)

        self.browser = BrowserWidget()
        self.setCentralWidget(self.browser)

        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        save_pdf_action = QAction("Save Page as PDF", self)
        save_pdf_action.triggered.connect(self.browser.save_current_as_pdf)
        toolbar.addAction(save_pdf_action)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.browser.new_tab())
        toolbar.addAction(new_tab_action)


def main():
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()