import sys
from pathlib import Path

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QWidget,
)

from lyric_n_summarization_ui import LyricsSummarizationUi

from services.definition_service  import DefinitionService
from services.note_service        import NoteService
from services.preferences_service import PreferencesService
from services.theme_service       import ThemeService

from ui.editor_area import EditorArea
from ui.sidebar     import Sidebar


CONFIG_FILE = Path(__file__).parent / "noteworthy files/config.json"
TEMP_FILE   = Path(__file__).parent / "noteworthy files/temp.txt"

AUTOSAVE_DELAY_MS = 1000


class NoteWorthy(QWidget):
    """
    Thin orchestration shell.

    Responsibilities:
      - Instantiate services and UI sub-widgets.
      - Connect widget signals → service calls.
      - Push service results back into the UI.
    """

    def __init__(self):
        super().__init__()
        self._path = Path(__file__).parent

        # ---- services ----
        self._notes       = NoteService(TEMP_FILE)
        self._definitions = DefinitionService()
        self._prefs       = PreferencesService(CONFIG_FILE)
        self._themes      = ThemeService(self._path)

        # ---- autosave timer ----
        self._autosave_timer = QTimer()
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(
            lambda: self._notes.autosave(self._editor.get_text())
        )

        # ---- window chrome ----
        self.setWindowTitle("Note Worthy")
        self.setGeometry(100, 100, 600, 400)
        win_icon = self._path / "Icons/icons8-notebook-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))

        # ---- build layout ----
        root = QHBoxLayout(self)

        self._sidebar      = Sidebar(self._path)
        self._toggle_btn   = self._make_toggle_btn()
        self._editor       = EditorArea(self._path)

        root.addWidget(self._sidebar)
        root.addWidget(self._toggle_btn)
        root.addLayout(self._editor.layout() or self._editor_vbox())
        # EditorArea is a QWidget — add it directly
        root.addWidget(self._editor)
        self.setLayout(root)

        # ---- wire signals ----
        self._connect_signals()

        # ---- initialise state ----
        self._init_wrapper()

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------
    def _connect_signals(self):
        # editor → services
        self._editor.text_changed.connect(self._on_text_changed)
        self._editor.definition_requested.connect(self._on_definition_requested)

        # sidebar buttons → handlers
        self._sidebar.file_btn.clicked.connect(self._open_file)
        self._sidebar.theme_btn.clicked.connect(self._toggle_theme)
        self._sidebar.font_size_box.currentIndexChanged.connect(self._change_font_size)
        self._sidebar.copy_btn.clicked.connect(self._editor.text_edit.copy)
        self._sidebar.cut_btn.clicked.connect(self._editor.text_edit.cut)
        self._sidebar.paste_btn.clicked.connect(self._editor.text_edit.paste)
        self._sidebar.lyrical_btn.clicked.connect(self._launch_lyrical_lab)
        self._sidebar.undo_btn.clicked.connect(self._editor.text_edit.undo)
        self._sidebar.clear_btn.clicked.connect(self._editor.text_edit.clear)
        self._sidebar.save_btn.clicked.connect(self._save_file)
        self._sidebar.md_btn.clicked.connect(self._toggle_markdown)
        self._sidebar.exit_btn.clicked.connect(self._exit)

        # toggle button
        self._toggle_btn.clicked.connect(self._toggle_sidebar)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def _init_wrapper(self):
        font_size = self._prefs.load_font_size()
        self._editor.set_font_size(font_size)
        self._sidebar.font_size_box.setCurrentText(str(font_size))
        self._apply_current_theme()
        last_text = self._notes.load_last()
        if last_text is not None:
            self._editor.set_text(last_text)

    # ------------------------------------------------------------------
    # Text / autosave
    # ------------------------------------------------------------------
    def _on_text_changed(self):
        self._editor.update_word_count()
        self._editor.refresh_markdown()
        self._autosave_timer.start(AUTOSAVE_DELAY_MS)

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------
    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", "",
            "Text Files (*.txt);;HTML (*.html);;CSV (*.csv);;Python (*.py);;Markdown (*.md)"
        )
        if path:
            try:
                self._notes.write_file(path, self._editor.get_text())
            except OSError as e:
                QMessageBox.critical(self, "Save error", str(e))

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "",
            "Text Files (*.txt);;HTML (*.html);;CSV (*.csv);;Python (*.py);;Markdown (*.md)"
        )
        if path:
            try:
                self._editor.set_text(self._notes.read_file(path))
            except OSError as e:
                QMessageBox.critical(self, "Open error", str(e))

    # ------------------------------------------------------------------
    # Dictionary
    # ------------------------------------------------------------------
    def _on_definition_requested(self, word: str):
        result = self._definitions.lookup(word)
        self._editor.show_definition(result)

    # ------------------------------------------------------------------
    # Font size
    # ------------------------------------------------------------------
    def _change_font_size(self):
        size = int(self._sidebar.font_size_box.currentText())
        self._editor.set_font_size(size)
        self._prefs.save(self._themes.current_mode, str(size))

    # ------------------------------------------------------------------
    # Markdown preview
    # ------------------------------------------------------------------
    def _toggle_markdown(self):
        self._editor.toggle_markdown_preview()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self._themes.toggle()
        self._apply_current_theme()
        self._prefs.save(
            self._themes.current_mode,
            self._sidebar.font_size_box.currentText(),
        )

    def _apply_current_theme(self):
        sheet = self._themes.stylesheet()
        self.setStyleSheet(sheet)
        self._sidebar.setStyleSheet(sheet)
        self._sidebar.theme_btn.setIcon(QIcon(self._themes.icon_path()))

    # ------------------------------------------------------------------
    # Sidebar toggle
    # ------------------------------------------------------------------
    def _toggle_sidebar(self):
        menu_icon = self._path / "Icons/icons8-menu-48.png"
        x_icon    = self._path / "Icons/icons8-close-64.png"
        if self._sidebar.isVisible():
            self._sidebar.hide()
            self._toggle_btn.setIcon(QIcon(str(menu_icon)))
        else:
            self._sidebar.show()
            self._toggle_btn.setIcon(QIcon(str(x_icon)))

    # ------------------------------------------------------------------
    # Lyrical Lab
    # ------------------------------------------------------------------
    def _launch_lyrical_lab(self):
        self._lyrical_window = LyricsSummarizationUi()
        self._lyrical_window.show()

    # ------------------------------------------------------------------
    # Exit
    # ------------------------------------------------------------------
    def _exit(self):
        self.destroy()
        sys.exit()

    # ------------------------------------------------------------------
    # Toggle button factory
    # ------------------------------------------------------------------
    def _make_toggle_btn(self) -> QPushButton:
        x_icon = self._path / "Icons/icons8-close-64.png"
        btn = QPushButton("")
        btn.setIcon(QIcon(str(x_icon)))
        btn.setIconSize(QSize(30, 30))
        return btn

    def _editor_vbox(self):
        """Fallback — should never be needed; EditorArea manages its own layout."""
        from PySide6.QtWidgets import QVBoxLayout
        return QVBoxLayout()


# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication([])
    window = NoteWorthy()
    window.show()
    sys.exit(app.exec())
