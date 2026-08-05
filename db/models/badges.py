from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from db.models.cerebral_pursuits import UserInfo, CerebralPursuit

class BadgeAndTitle(Base):
    __tablename__ = "badges_and_titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge: Mapped[str | None] = mapped_column(String)
    titles: Mapped[str | None] = mapped_column(String)
    uid: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user_info.uid", ondelete="CASCADE", onupdate="CASCADE")
    )
    subject_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cerebral_pursuits.id", ondelete="CASCADE", onupdate="CASCADE")
    )

    user: Mapped["UserInfo"] = relationship()
    subject: Mapped["CerebralPursuit"] = relationship()