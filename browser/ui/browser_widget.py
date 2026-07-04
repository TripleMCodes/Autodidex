"""
ui/browser_widget.py

The widget you actually drop into Autodidex. Wraps a QTabWidget of
BrowserTab instances sharing one BrowserProfileService (so cookies/
history persist across tabs and app restarts), plus a toolbar action
to save the current page as a PDF.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QToolButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from browser.services.browser_profile import BrowserProfileService
from browser.ui.browser_tab import BrowserTab

HOME_URL = "https://duckduckgo.com"


class BrowserWidget(QWidget):
    """Standalone, embeddable in-app browser. Usage:

        self.browser = BrowserWidget()
        layout.addWidget(self.browser)
    """

    def __init__(self, home_url: str = HOME_URL, parent: QWidget | None = None):
        super().__init__(parent)
        self._home_url = home_url

        self.profile_service = BrowserProfileService(parent=self)
        self.profile_service.set_dialog_parent(self)
        self.profile_service.download_finished.connect(self._on_download_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)

        new_tab_btn = QToolButton(text="+")
        new_tab_btn.setAutoRaise(True)
        new_tab_btn.clicked.connect(lambda: self.new_tab())
        self.tabs.setCornerWidget(new_tab_btn, Qt.TopRightCorner)

        layout.addWidget(self.tabs)

        self.new_tab()

    # --- public API -------------------------------------------------------

    def new_tab(self, url: str | None = None) -> BrowserTab:
        tab = BrowserTab(self.profile_service.profile, home_url=url or self._home_url)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)

        tab.title_changed.connect(lambda title, t=tab: self._update_tab_title(t, title))
        tab.icon_changed.connect(lambda icon, t=tab: self._update_tab_icon(t, icon))
        return tab

    def navigate_current(self, text_or_url: str) -> None:
        current = self._current_tab()
        if current:
            current.navigate(text_or_url)

    def save_current_as_pdf(self) -> None:
        current = self._current_tab()
        if not current:
            return
        default_name = "page.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Save Page as PDF", default_name, "PDF Files (*.pdf)")
        if path:
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            current.save_as_pdf(path)

    # --- internal -----------------------------------------------------

    def _current_tab(self) -> BrowserTab | None:
        return self.tabs.currentWidget()

    def _close_tab(self, index: int) -> None:
        if self.tabs.count() <= 1:
            return  # keep at least one tab open
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        widget.deleteLater()

    def _update_tab_title(self, tab: BrowserTab, title: str) -> None:
        index = self.tabs.indexOf(tab)
        if index != -1:
            shortened = (title[:20] + "…") if len(title) > 20 else title
            self.tabs.setTabText(index, shortened or "New Tab")

    def _update_tab_icon(self, tab: BrowserTab, icon) -> None:
        index = self.tabs.indexOf(tab)
        if index != -1 and icon is not None:
            self.tabs.setTabIcon(index, icon)

    def _on_download_finished(self, path: str, ok: bool) -> None:
        if ok:
            QMessageBox.information(self, "Download Complete", f"Saved to:\n{path}")
        else:
            QMessageBox.warning(self, "Download Failed", f"Could not save:\n{path}")