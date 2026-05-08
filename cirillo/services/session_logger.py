import csv
import datetime
import logging
from collections import defaultdict
from pathlib import Path


class SessionLogger:
    """Reads and writes study session data to a CSV file."""

    FIELDS = ["sessions", "date", "time studied"]
    DATE_FMT = "%d %B %Y"

    def __init__(self, file: Path):
        self.file = file

    # ------------------------------------------------------------------
    # Date helpers
    # ------------------------------------------------------------------
    @staticmethod
    def today_str() -> str:
        return datetime.datetime.today().strftime(SessionLogger.DATE_FMT)

    @staticmethod
    def format_date(dt: datetime.datetime) -> str:
        return dt.strftime(SessionLogger.DATE_FMT)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def load_current_sessions(self) -> int:
        """Return the session count already saved for today (0 if none)."""
        try:
            with open(self.file, "r") as f:
                rows = list(csv.DictReader(f))
            if not rows:
                return 0
            last = rows[-1]
            if last.get("date") == self.today_str():
                return int(last["sessions"])
        except FileNotFoundError:
            logging.warning("Sessions CSV not found; starting from 0.")
        return 0

    def load_all(self) -> dict:
        """Return {date_obj: session_count} for plotting."""
        date_map = defaultdict(int)
        try:
            with open(self.file, newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or "date" not in reader.fieldnames:
                    return date_map
                for row in reader:
                    try:
                        date_obj = datetime.datetime.strptime(row["date"], self.DATE_FMT)
                        date_map[date_obj] += int(row["sessions"])
                    except ValueError as e:
                        logging.debug(f"Skipping row: {e}")
        except FileNotFoundError:
            logging.warning("Sessions CSV not found.")
        return date_map

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def log(self, sessions: int, time_studied_mins: int):
        """Upsert today's row with updated session count and time studied."""
        if sessions <= 0:
            return

        hrs, mins = divmod(time_studied_mins, 60)
        today = self.today_str()

        with open(self.file) as f:
            all_rows = list(csv.DictReader(f))

        filtered = [r for r in all_rows if r.get("date") != today]

        with open(self.file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            writer.writerows(filtered)

        with open(self.file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            if self.file.stat().st_size == 0:
                writer.writeheader()
            writer.writerow({
                "sessions": str(sessions),
                "date": today,
                "time studied": f"{hrs:02d} hrs {mins:02d} mins",
            })
        logging.debug(f"Logged {sessions} sessions for {today}.")
