from sqlalchemy import select, delete, func
from db.engine import SessionLocal
from db.models import Reminder


class ReminderService:

    def add_reminder(self, text: str, remind_at_iso: str, note_id: int | None = None) -> int:
        with SessionLocal() as session:
            reminder = Reminder(text=text, remind_at=remind_at_iso, note_id=note_id)
            session.add(reminder)
            session.commit()
            session.refresh(reminder)  # populates reminder.id after insert
            return reminder.id

    def get_all(self) -> list[Reminder]:
        with SessionLocal() as session:
            return session.execute(
                select(Reminder).order_by(Reminder.remind_at.asc())
            ).scalars().all()

    def get_pending(self) -> list[Reminder]:
        with SessionLocal() as session:
            return session.execute(
                select(Reminder)
                .where(Reminder.fired == 0)
                .order_by(Reminder.remind_at.asc())
            ).scalars().all()

    def get_for_date(self, date_iso: str) -> list[Reminder]:
        """date_iso like 'yyyy-MM-dd' — used to highlight/populate a selected calendar day."""
        with SessionLocal() as session:
            return session.execute(
                select(Reminder)
                .where(Reminder.remind_at.like(f"{date_iso}%"))
                .order_by(Reminder.remind_at.asc())
            ).scalars().all()

    def get_dates_with_reminders(self) -> set[str]:
        """Distinct 'yyyy-MM-dd' dates with at least one pending reminder,
        used to bold/mark cells in QCalendarWidget."""
        with SessionLocal() as session:
            rows = session.execute(
                select(func.substr(Reminder.remind_at, 1, 10))
                .where(Reminder.fired == 0)
                .distinct()
            ).scalars().all()
            return set(rows)

    def mark_fired(self, reminder_id: int) -> None:
        with SessionLocal() as session:
            reminder = session.get(Reminder, reminder_id)
            if reminder is None:
                return
            reminder.fired = 1
            session.commit()

    def delete_reminder(self, reminder_id: int) -> None:
        with SessionLocal() as session:
            session.execute(delete(Reminder).where(Reminder.id == reminder_id))
            session.commit()

    def update_reminder(self, reminder_id: int, text: str, remind_at_iso: str) -> None:
        with SessionLocal() as session:
            reminder = session.get(Reminder, reminder_id)
            if reminder is None:
                return
            reminder.text = text
            reminder.remind_at = remind_at_iso
            session.commit()