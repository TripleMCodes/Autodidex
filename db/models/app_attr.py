from sqlalchemy import Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class AppAttr(Base):
    __tablename__ = "app_attr"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_active: Mapped[int] = mapped_column(Integer, default=0)
    reset_date: Mapped[str | None] = mapped_column(Date)