"""
ui/browser_tab.py

One tab = one NavBar + one QWebEngineView, wired together. Handles the
"is this a URL or a search query" resolution and forwards title/icon/
progress changes up via signals so BrowserWidget can update tab labels.
"""

from __future__ import annotations

from urllib.parse import quote

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile

from browser.ui.nav_bar import NavBar

SEARCH_URL_TEMPLATE = "https://duckduckgo.com/?q={query}"


def resolve_input(text: str) -> QUrl:
    """Turn whatever the user typed into a navigable QUrl — a real URL,
    a bare domain, or a search query."""
    text = text.strip()
    if not text:
        return QUrl("about:blank")

    candidate = QUrl.fromUserInput(text)
    looks_like_url = (
        candidate.isValid()
        and ("." in text or text.startswith("localhost"))
        and " " not in text
    )
    if looks_like_url:
        return candidate

    return QUrl(SEARCH_URL_TEMPLATE.format(query=quote(text)))


class BrowserTab(QWidget):
    title_changed = Signal(str)
    icon_changed = Signal(object)   # QIcon
    load_progress = Signal(int)

    def __init__(self, profile: QWebEngineProfile, home_url: str = "https://duckduckgo.com", parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.nav_bar = NavBar()
        layout.addWidget(self.nav_bar)

        self.view = QWebEngineView()
        self._apply_profile(profile)
        layout.addWidget(self.view, stretch=1)
        layout.addWidget(self.nav_bar.progress)

        self._wire_signals()
        self.navigate(home_url)

    # --- setup -----------------------------------------------------

    def _apply_profile(self, profile: QWebEngineProfile) -> None:
        # QWebEnginePage must be constructed with the profile to actually use it.
        from PySide6.QtWebEngineCore import QWebEnginePage
        page = QWebEnginePage(profile, self.view)
        self.view.setPage(page)

    def _wire_signals(self) -> None:
        self.nav_bar.back_clicked.connect(self.view.back)
        self.nav_bar.forward_clicked.connect(self.view.forward)
        self.nav_bar.reload_clicked.connect(self.view.reload)
        self.nav_bar.stop_clicked.connect(self.view.stop)
        self.nav_bar.url_submitted.connect(lambda text: self.navigate(text))

        self.view.urlChanged.connect(lambda url: self.nav_bar.set_url_text(url.toString()))
        self.view.loadProgress.connect(self._on_load_progress)
        self.view.loadFinished.connect(lambda _ok: self._update_nav_buttons())
        self.view.titleChanged.connect(lambda title: self.title_changed.emit(title))
        self.view.iconChanged.connect(lambda icon: self.icon_changed.emit(icon))

    # --- public API -------------------------------------------------------

    def navigate(self, text_or_url: str) -> None:
        url = text_or_url if isinstance(text_or_url, QUrl) else resolve_input(text_or_url)
        self.view.load(url)

    def save_as_pdf(self, file_path: str) -> None:
        self.view.page().printToPdf(file_path)

    def current_html(self, callback) -> None:
        """callback(html: str) — QWebEnginePage.toHtml() is async."""
        self.view.page().toHtml(callback)

    # --- internal -----------------------------------------------------

    def _on_load_progress(self, percent: int) -> None:
        self.nav_bar.set_progress(percent)
        self.load_progress.emit(percent)

    def _update_nav_buttons(self) -> None:
        history = self.view.history()
        self.nav_bar.set_nav_enabled(history.canGoBack(), history.canGoForward())