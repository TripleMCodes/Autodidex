from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class UserInfo(Base):
    __tablename__ = "user_info"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    overall_level: Mapped[int | None] = mapped_column(Integer)


class Bank(Base):
    __tablename__ = "bank"

    uid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_info.uid", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        autoincrement=True,
    )
    lumens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class CerebralPursuit(Base):
    __tablename__ = "cerebral_pursuits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String, unique=True)
    uid: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user_info.uid", ondelete="CASCADE", onupdate="CASCADE"),
    )
    subject_xp: Mapped[int] = mapped_column(Integer, default=0)
    subject_level: Mapped[int] = mapped_column(Integer, default=0)

    check_marks: Mapped[list["CheckMark"]] = relationship(
        back_populates="subject_ref", cascade="all, delete-orphan"
    )


class CheckMark(Base):
    __tablename__ = "check_marks"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cerebral_pursuits.id", ondelete="CASCADE")
    )
    reset_date: Mapped[str | None] = mapped_column(String)
    Monday: Mapped[str | None] = mapped_column(String)
    Tuesday: Mapped[str | None] = mapped_column(String)
    Wednesday: Mapped[str | None] = mapped_column(String)
    Thursday: Mapped[str | None] = mapped_column(String)
    Friday: Mapped[str | None] = mapped_column(String)
    Saturday: Mapped[str | None] = mapped_column(String)
    Sunday: Mapped[str | None] = mapped_column(String)

    subject_ref: Mapped["CerebralPursuit"] = relationship(back_populates="check_marks")