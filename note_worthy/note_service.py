import logging
from pathlib import Path


class NoteService:
    """
    Handles all file I/O for note content:
      - autosave to a temp buffer
      - restore last session text
      - explicit save-to-file (any supported format)
      - open-from-file
    """

    def __init__(self, temp_path: Path):
        self._temp = temp_path
        self._last_saved: str = ""

    # ------------------------------------------------------------------
    # Autosave
    # ------------------------------------------------------------------
    def autosave(self, text: str):
        """Write text to the temp buffer only when it has actually changed."""
        if text == self._last_saved:
            return
        try:
            self._temp.parent.mkdir(parents=True, exist_ok=True)
            self._temp.write_text(text, encoding="utf-8")
            self._last_saved = text
            logging.debug("NoteService: autosaved.")
        except OSError as e:
            logging.warning(f"NoteService: autosave failed: {e}")

    def load_last(self) -> str | None:
        """Return the last autosaved text, or None if no buffer exists."""
        try:
            return self._temp.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    # ------------------------------------------------------------------
    # Explicit file operations (return text on read; raise on error)
    # ------------------------------------------------------------------
    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write_file(path: str, text: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
