import datetime
import logging
from typing import Optional

from cp_tracker_db import Cp_tracker


class HabitService:
    """
    All database interactions for the Cerebral Pursuit Tracker.
    The UI never touches cp_table directly — it goes through here.
    """

    def __init__(self):
        self._db = Cp_tracker()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get_habits(self) -> list[str]:
        """Return the current list of cerebral pursuit subjects."""
        return self._db.get_cerebral_pursuits() or []

    def get_checkbox_states(self) -> dict:
        """Return saved checkbox states keyed by 'row,col'."""
        return self._db.get_check_marks()

    def get_cp_with_check_marks(self) -> dict:
        """Return {habit: check_count} for the progress chart."""
        return self._db.get_cp_with_check_marks()

    def get_reset_date(self) -> Optional[datetime.datetime]:
        """Return the weekly reset date (or None if not set)."""
        return self._db.get_reset_date()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def add_habit(self, habit: str) -> dict:
        """Insert a new habit. Returns {status: bool, message: str}."""
        return self._db.insert_cp(habit)

    def save_checkbox(self, row: int, col: int, subject: str, day: str) -> dict:
        """Persist a single checkbox check. Returns {status, message}."""
        state = {f"{row},{col}": True}
        return self._db.save_cp(row, state, subject, day)

    def edit_habit(self, old_name: str, new_name: str) -> dict:
        """Rename a habit. Returns {status, message}."""
        return self._db.update_cp(old_name, new_name)

    def delete_habit(self, subject: str) -> dict:
        """Delete a habit and its checkmarks. Returns {status, message}."""
        return self._db.delete_cp(subject)

    def clear_all_data(self) -> dict:
        """Wipe all check-mark data (weekly reset). Returns {status, message}."""
        return self._db.clear_cp_data()

    # ------------------------------------------------------------------
    # Reset logic
    # ------------------------------------------------------------------
    def needs_reset(self) -> bool:
        """Return True if today >= the stored reset date."""
        try:
            reset_date = self.get_reset_date()
            if reset_date is None:
                return False
            today = datetime.datetime.strptime(str(datetime.datetime.now().date()), "%Y-%m-%d")
            return today >= reset_date
        except TypeError:
            logging.debug("Reset date not available yet.")
            return False
