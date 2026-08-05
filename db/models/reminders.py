from sqlalchemy import Integer, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index
from db.base import Base

class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (Index("idx_reminders_remind_at", "remind_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    remind_at: Mapped[str] = mapped_column(String, nullable=False)  # ISO 8601
    fired: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String, nullable=False, server_default=func.now())
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("notes.id", ondelete="SET NULL")
    )

    note: Mapped["Note"] = relationship()