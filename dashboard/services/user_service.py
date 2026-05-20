import logging

from autodidex_cache import DictionaryCache
from dash_board_db import Dashboard
from cp_tracker_db import Cp_tracker


class UserService:
    """
    Manages user identity, overall level, and badge reward logic.

    Corresponds to the original UserIfo class, renamed for clarity
    and stripped of direct UI dependencies.
    """

    def __init__(self):
        self._dashboard  = Dashboard()
        self._cp_tracker = Cp_tracker()
        self._cache      = DictionaryCache()

        self._name          = self._dashboard.get_user_name()
        self._overall_level = self._load_overall_level()
        self.subjects: list = self._cp_tracker.get_cerebral_pursuits() or []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value[0].isupper():
            raise ValueError("Please capitalize the first letter of your name.")
        self._name = value

    @property
    def level(self) -> int:
        return self._overall_level

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def initialize_subjects(self) -> list:
        """Return the current list of cerebral-pursuit subjects."""
        return self.subjects

    def refresh_subjects(self):
        """Re-fetch subjects from the DB (called after new CP is added)."""
        self.subjects = self._cp_tracker.get_cerebral_pursuits() or []

    def overall_level_up(self):
        """
        Recalculate overall level from total XP (every 500 XP = 1 level).
        Awards a badge and updates the cache if the level increased.
        """
        xp_amount       = self._dashboard.get_total_xp()
        new_level       = xp_amount // 500
        cached_level    = self._cache.get("overall_level") or 0

        if new_level > cached_level:
            self._overall_level = new_level
            self._dashboard.increment_overall_level(new_level)
            self._cache.set("overall_level", new_level)
            self._award_overall_badge(new_level)

    def cp_level_badge_reward(self):
        """Award per-subject badges when level or XP milestones are hit."""
        BADGES = ["🎯 Every Ten Counts", "🏆 1K Subject XP Master"]

        cp_with_levels = self._cp_tracker.get_cp_with_level()
        cp_with_xp     = self._cp_tracker.get_cp_with_xp()

        for subject, level in cp_with_levels.items():
            if level % 10 == 0 and level != 0:
                msg = self._dashboard.add_cp_badge(BADGES[0], subject)
                if msg:
                    logging.debug(msg.get("message"))

        for subject, xp in cp_with_xp.items():
            if xp % 10 == 0 and xp != 0:
                msg = self._dashboard.add_cp_badge(BADGES[1], subject)
                if msg:
                    logging.debug(msg.get("message"))

        self._refresh_badge_cache()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_overall_level(self) -> int:
        level = self._cache.get("overall_level")
        if level is None:
            level = self._dashboard.get_overall_level()
            self._cache.set("overall_level", level)
        return level

    def _award_overall_badge(self, level: int):
        if level == 5:
            self._dashboard.add_new_badge("🎖️ Level 5 Unlocked")
        if level % 10 == 0:
            self._dashboard.add_new_badge("💎 Every Tenth Tier counts")
        self._refresh_badge_cache()

    def _refresh_badge_cache(self):
        self._cache.set("cp_badges",  self._dashboard.get_cp_with_badges())
        self._cache.set("badges",     self._dashboard.get_all_badges())
