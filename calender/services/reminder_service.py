"""
services/reminder_service.py

Sits between the DB layer and the UI. Owns the QTimer that polls for due
reminders and emits Qt signals so any widget (calendar panel, tray icon,
dashboard) can react without knowing about SQLite.
"""

from PySide6.QtCore import QObject, Signal, QTimer, QDateTime

from reminder_db import RemindersDB


class ReminderService(QObject):
    # Emitted whenever a reminder fires — UI decides how to notify (tray, dialog, sound...)
    reminder_due = Signal(int, str)          # (reminder_id, text)
    # Emitted whenever reminders are added/edited/deleted — UI refreshes lists/calendar marks
    reminders_changed = Signal()

    def __init__(self, poll_interval_ms: int = 30_000, parent=None):
        super().__init__(parent)
        self.db = RemindersDB()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_due_reminders)
        self._timer.start(poll_interval_ms)

    # --- public API -------------------------------------------------

    def add_reminder(self, text: str, dt: QDateTime, note_id: int | None = None) -> int:
        text = text.strip()
        if not text:
            raise ValueError("Reminder text cannot be empty")
        reminder_id = self.db.add_reminder(text, dt.toString("yyyy-MM-ddTHH:mm:ss"), note_id)
        self.reminders_changed.emit()
        return reminder_id

    def delete_reminder(self, reminder_id: int) -> None:
        self.db.delete_reminder(reminder_id)
        self.reminders_changed.emit()

    def update_reminder(self, reminder_id: int, text: str, dt: QDateTime) -> None:
        self.db.update_reminder(reminder_id, text.strip(), dt.toString("yyyy-MM-ddTHH:mm:ss"))
        self.reminders_changed.emit()

    def reminders_for_date(self, date) -> list:
        """date: QDate — returns rows for that day, used when a calendar cell is clicked."""
        return self.db.get_for_date(date.toString("yyyy-MM-dd"))

    def dates_with_reminders(self) -> set[str]:
        return self.db.get_dates_with_reminders()

    def all_pending(self) -> list:
        return self.db.get_pending()

    # --- internal -----------------------------------------------------

    def _check_due_reminders(self) -> None:
        now = QDateTime.currentDateTime()
        for row in self.db.get_pending():
            remind_at = QDateTime.fromString(row["remind_at"], "yyyy-MM-ddTHH:mm:ss")
            if remind_at <= now:
                self.db.mark_fired(row["id"])
                self.reminder_due.emit(row["id"], row["text"])
        self.reminders_changed.emit()