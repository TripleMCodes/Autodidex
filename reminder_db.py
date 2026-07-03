"""
db/reminders_db.py

Raw SQLite access for reminders. No Qt imports here — this layer only
knows about sqlite3, mirroring how the rest of Autodidex keeps DB code
separate from services and UI.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class RemindersDB:
    def __init__(self):
        self.db_path = Path(__file__).parent / "autodidex.db"
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    text        TEXT NOT NULL,
                    remind_at   TEXT NOT NULL,   -- ISO 8601 "yyyy-MM-ddTHH:mm:ss"
                    fired       INTEGER NOT NULL DEFAULT 0,
                    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                    note_id     INTEGER,          -- optional FK -> notes.id, for linking a reminder to a note
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders(remind_at)"
            )

    # --- CRUD -----------------------------------------------------------

    def add_reminder(self, text: str, remind_at_iso: str, note_id: Optional[int] = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO reminders (text, remind_at, note_id) VALUES (?, ?, ?)",
                (text, remind_at_iso, note_id),
            )
            return cur.lastrowid

    def get_all(self) -> list[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM reminders ORDER BY remind_at ASC"
            ).fetchall()

    def get_pending(self) -> list[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM reminders WHERE fired = 0 ORDER BY remind_at ASC"
            ).fetchall()

    def get_for_date(self, date_iso: str) -> list[sqlite3.Row]:
        """date_iso like 'yyyy-MM-dd' — used to highlight/populate a selected calendar day."""
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM reminders WHERE remind_at LIKE ? ORDER BY remind_at ASC",
                (f"{date_iso}%",),
            ).fetchall()

    def get_dates_with_reminders(self) -> set[str]:
        """Returns the distinct 'yyyy-MM-dd' dates that have at least one pending reminder,
        used to bold/mark cells in QCalendarWidget."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT substr(remind_at, 1, 10) AS d FROM reminders WHERE fired = 0"
            ).fetchall()
            return {row["d"] for row in rows}

    def mark_fired(self, reminder_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE reminders SET fired = 1 WHERE id = ?", (reminder_id,))

    def delete_reminder(self, reminder_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

    def update_reminder(self, reminder_id: int, text: str, remind_at_iso: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE reminders SET text = ?, remind_at = ? WHERE id = ?",
                (text, remind_at_iso, reminder_id),
            )