import json
import logging
from pathlib import Path


class PreferencesService:
    """
    Persists and retrieves user preferences (font size, theme mode)
    from a JSON config file.
    """

    DEFAULT_FONT_SIZE = 14

    def __init__(self, config_path: Path):
        self._path = config_path

    def load_font_size(self) -> int:
        """Return saved font size, or the default (14) if none is stored."""
        try:
            with open(self._path, "r") as f:
                data = json.load(f)
            return int(data.get("font_size", self.DEFAULT_FONT_SIZE))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return self.DEFAULT_FONT_SIZE

    def save(self, theme_mode: str, font_size: str):
        """Persist current theme mode and font size selection."""
        try:
            with open(self._path, "w") as f:
                json.dump({"dark_mode": theme_mode, "font_size": font_size}, f)
        except OSError as e:
            logging.warning(f"PreferencesService: could not save config: {e}")
