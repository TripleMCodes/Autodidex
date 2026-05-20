from pathlib import Path
from typing import Optional

from autodidex_cache import DictionaryCache
from themes_db import Themes


class ThemeService:
    """
    Manages light / dark / neutral theme cycling.
    Shared contract across all Autodidex apps — drop-in reusable.
    """

    ICONS = {
        "light":   "Icons/icons8-light-64.png",
        "dark":    "Icons/icons8-dark-mode-48.png",
        "neutral": "Icons/icons8-day-and-night-50.png",
    }
    CYCLE = ["light", "dark", "neutral"]

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._themes   = Themes()
        self._cache    = DictionaryCache()

        # Resolve stylesheets: cache-first, then DB
        self.stylesheets: dict[str, Optional[str]] = {}
        for mode in self.CYCLE:
            cached = self._cache.get(mode)
            if cached:
                self.stylesheets[mode] = cached
            else:
                sheet = self._themes.get_theme_mode(mode)
                self._cache.set(mode, sheet)
                self.stylesheets[mode] = sheet

        # Current mode: cache-first, then DB
        self.current_mode: str = self._cache.get("theme") or self._themes.get_chosen_theme()

    def stylesheet(self, mode: Optional[str] = None) -> str:
        return self.stylesheets.get(mode or self.current_mode, "")

    def icon_path(self, mode: Optional[str] = None) -> str:
        rel = self.ICONS.get(mode or self.current_mode, "")
        return str(self.base_path / rel)

    def toggle(self) -> str:
        """Advance to the next mode and return its name."""
        idx = self.CYCLE.index(self.current_mode)
        self.current_mode = self.CYCLE[(idx + 1) % len(self.CYCLE)]
        return self.current_mode
