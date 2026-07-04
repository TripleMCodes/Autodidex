"""
services/browser_profile.py

Owns the QWebEngineProfile — persistent cookies/cache location, the
settings that let Chromium render local PDFs, and download handling.
Kept separate from any widget so the UI layer never touches Chromium
configuration directly (same split as ReminderService owning the DB).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, QStandardPaths
from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineDownloadRequest


class BrowserProfileService(QObject):
    """Wraps a single QWebEngineProfile shared by every tab in the browser."""

    # Emitted when a download finishes (path, ok) so the UI can show a toast/notification.
    download_finished = Signal(str, bool)

    def __init__(self, storage_name: str = "autodidex_browser", parent: QObject | None = None):
        super().__init__(parent)

        data_root = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        storage_path = data_root / storage_name

        # Named, off-the-record=False profile -> persists cookies/cache/history
        # across app restarts, separate from Autodidex's other app data.
        self.profile = QWebEngineProfile(storage_name, self)
        self.profile.setPersistentStoragePath(str(storage_path))
        self.profile.setCachePath(str(storage_path / "cache"))
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)

        self.profile.downloadRequested.connect(self._handle_download_requested)

        self._download_parent_widget: QWidget | None = None

    def set_dialog_parent(self, widget: QWidget) -> None:
        """Widget used as the parent for the native save-file dialog on downloads."""
        self._download_parent_widget = widget

    # --- internal -----------------------------------------------------

    def _handle_download_requested(self, download: QWebEngineDownloadRequest) -> None:
        suggested = download.downloadFileName() or "download"
        default_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)

        path, _ = QFileDialog.getSaveFileName(
            self._download_parent_widget,
            "Save File",
            str(Path(default_dir) / suggested),
        )
        if not path:
            download.cancel()
            return

        target = Path(path)
        download.setDownloadDirectory(str(target.parent))
        download.setDownloadFileName(target.name)
        download.isFinishedChanged.connect(
            lambda: self.download_finished.emit(str(target), download.isFinished())
        )
        download.accept()