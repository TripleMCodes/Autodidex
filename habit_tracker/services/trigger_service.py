import random
import string
from pathlib import Path


class TriggerService:
    """
    Signals other parts of the Autodidex ecosystem by writing a random
    string to a watched text file.  QFileSystemWatcher elsewhere picks
    this up and refreshes accordingly.
    """

    def __init__(self, base_path: Path):
        self._dashboard_trigger = base_path / "update.txt"
        self._db_ui_trigger     = base_path / "update_db_ui.txt"

    # ------------------------------------------------------------------
    def notify_dashboard(self):
        """Tell the dashboard a habit was added / edited / deleted."""
        self._write(self._dashboard_trigger)

    def notify_db_ui(self):
        """Tell the DB UI widget a checkbox state has changed."""
        self._write(self._db_ui_trigger)

    # ------------------------------------------------------------------
    @staticmethod
    def _write(path: Path):
        random_string = "".join(random.choices(string.ascii_letters, k=26))
        with open(path, "w") as f:
            f.write(random_string)
