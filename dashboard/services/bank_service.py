import json
import logging
from pathlib import Path
from typing import Optional

from autodidex_cache import DictionaryCache
from dash_board_db import Dashboard
from cp_tracker_db import Cp_tracker


class BankService:
    """
    Manages the player's XP, lumen wallet, and subject-level progression.

    Corresponds to the original AutodidexBank class, renamed for clarity
    and with all UI references removed.
    """

    XP_PER_CHECKBOX   = 20    # progress_conversion multiplier
    XP_PER_LEVEL      = 200   # subject XP needed per level
    LUMENS_PER_LEVEL  = 10    # lumen reward on subject level-up

    def __init__(self, user_service):
        self._dashboard  = Dashboard()
        self._cp_tracker = Cp_tracker()
        self._cache      = DictionaryCache()
        self.user        = user_service

        self._xp_total:    int = self._dashboard.get_total_xp()
        self._wallet:      int = self._dashboard.get_lumens_amount()
        self.badges: Optional[dict] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def xp(self) -> int:
        return self._xp_total

    @property
    def wallet(self) -> int:
        return self._wallet

    @wallet.setter
    def wallet(self, lumens: int):
        if not isinstance(lumens, int):
            raise TypeError("Lumens must be an integer.")
        if lumens < 0:
            raise ValueError("Cannot deposit negative lumens.")
        self._wallet += lumens
        self._dashboard.add_lumens(self._wallet)
        logging.info(f"Deposited {lumens} lumens. New balance: {self._wallet}")

    # ------------------------------------------------------------------
    # XP / progression
    # ------------------------------------------------------------------
    def earn_subject_xp(self):
        """
        Compare current check-mark streaks against the cached snapshot.
        Award XP for any subject that gained new check-marks since last call.
        """
        current_data = self._cp_tracker.get_cp_with_check_marks()
        logging.debug(f"BankService.earn_subject_xp: current={current_data}")
        self._update_progression(current_data)

    def _update_progression(self, current_data: dict):
        cached = self._cache.get("cp_streak")

        if cached is None:
            self._cache.set("cp_streak", current_data)
            return

        for subject, streak in current_data.items():
            cached_streak = cached.get(subject, 0)
            if cached_streak < streak:
                xp = streak * self.XP_PER_CHECKBOX
                self._dashboard.add_total_xp(xp)
                self._xp_total += xp
                self._cp_tracker.save_cp_xp(subject, xp)
                self._subject_level_up(subject)
                self.user.cp_level_badge_reward()
                self.user.overall_level_up()
                logging.debug(f"BankService: XP update applied for '{subject}'")

        self._cache.set("cp_streak", current_data)

    def _subject_level_up(self, subject: str):
        """Level up a subject if its XP crossed the next threshold; reward lumens."""
        subject_xp    = self._cp_tracker.get_cp_specific_xp(subject)
        current_level = self._cp_tracker.get_cp_specific_level(subject)
        new_level     = subject_xp // self.XP_PER_LEVEL

        if new_level > current_level:
            self._cp_tracker.increment_cp_level(subject, new_level)
            self.wallet = self.LUMENS_PER_LEVEL
            logging.debug(f"BankService: '{subject}' levelled up to {new_level}")

    # ------------------------------------------------------------------
    # Lumen spending
    # ------------------------------------------------------------------
    def spend_lumens(self, amount: int) -> dict:
        """Deduct *amount* from the wallet and persist. Returns DB message dict."""
        self._wallet -= amount
        return self._dashboard.decrement_lumens(self._wallet)

    # ------------------------------------------------------------------
    # Badge management
    # ------------------------------------------------------------------
    def remove_badge(self, subject: str, badge: str, index: int) -> bool:
        """Remove a traded badge from the subject's collection."""
        badges_file = Path(__file__).parent.parent / "dashboard files/subjects_badges.json"

        if self.badges and subject in self.badges:
            self.badges[subject].pop(index)
            logging.debug(f"BankService: removed '{badge}' from '{subject}'")
            badges_file.write_text(
                __import__("json").dumps(self.badges, indent=4), encoding="utf-8"
            )
            return True
        return False
