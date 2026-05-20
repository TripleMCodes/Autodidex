import csv
import logging
from datetime import date, datetime
from pathlib import Path


DATE_FMT = "%d %B %Y"


class SessionReader:
    """
    Reads and parses the Cirillo sessions CSV.

    Provides:
      - load_study_data()  → {date: session_count}
      - load_date_range()  → (start_date, end_date)
      - load_first_date()  → str | None  (human-readable first date)
    """

    def __init__(self, sessions_file: Path):
        self._file = sessions_file

    # ------------------------------------------------------------------
    def load_study_data(self) -> dict[date, int]:
        """Return {date: session_count} from the full CSV."""
        data: dict[date, int] = {}
        try:
            with open(self._file, mode="r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        dt       = datetime.strptime(row["date"], DATE_FMT).date()
                        sessions = int(row["sessions"])
                        data[dt] = sessions
                    except (KeyError, ValueError):
                        continue
        except FileNotFoundError:
            logging.warning(f"SessionReader: file not found: {self._file}")
        except Exception as e:
            logging.error(f"SessionReader: unexpected error reading data: {e}")
        return data

    def load_date_range(self) -> tuple[date, date]:
        """
        Return (start_date, end_date) parsed from the first and last
        data rows.  Falls back to today on any error.
        """
        today = datetime.today().date()
        try:
            with open(self._file, mode="r", newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            if len(rows) >= 2:
                start = datetime.strptime(rows[1][1], DATE_FMT).date()
                end   = datetime.strptime(rows[-1][1], DATE_FMT).date()
                return start, end
        except FileNotFoundError:
            logging.warning(f"SessionReader: file not found: {self._file}")
        except Exception as e:
            logging.error(f"SessionReader: date range error: {e}")
        return today, today

    def load_first_date(self) -> str | None:
        """
        Return the raw date string from the first data row, or None.
        Used by the calendar label to show the streak start date.
        """
        try:
            with open(self._file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)                       # skip header
                first_row = next(reader, None)
                if first_row and len(first_row) > 1:
                    return first_row[1]
            logging.warning("SessionReader: no data rows found in sessions.csv.")
        except FileNotFoundError:
            logging.error(f"SessionReader: file not found: {self._file}")
        except UnicodeDecodeError:
            logging.error("SessionReader: encoding error — file must be UTF-8.")
        except Exception as e:
            logging.error(f"SessionReader: unexpected error: {e}")
        return None
