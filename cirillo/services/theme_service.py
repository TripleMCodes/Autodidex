from pathlib import Path
from typing import Optional

from autodidex_services.autodidex_cache import DictionaryCache
from autodidex_services.themes_db import Themes


class ThemeService:
    """Manages light / dark / neutral theme cycling."""

    ICONS = {
        "light": "Icons/icons8-light-64.png",
        "dark": "Icons/icons8-dark-mode-48.png",
        "neutral": "Icons/icons8-day-and-night-50.png",
    }
    CYCLE = ["light", "dark", "neutral"]

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._themes = Themes()
        self._cache = DictionaryCache()
        self.stylesheets: dict[str, Optional[str]] = {}
        
    # ------------------------------------------------------------------
    def stylesheet(self, mode: Optional[str] = None) -> str:
        """Return the stylesheet for *mode* (defaults to current mode)."""
        return self.stylesheets.get(mode or self.current_mode, "")

    def toggle(self, mode:str = "dark") -> str:
        """Advance to the next mode and return its name."""
        idx = self.CYCLE.index(mode)
        self.current_mode = self.CYCLE[(idx + 1) % len(self.CYCLE)]
        return self.current_mode
