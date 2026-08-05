from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dark: Mapped[str | None] = mapped_column(String)
    light: Mapped[str | None] = mapped_column(String)
    neutral: Mapped[str | None] = mapped_column(String)
    chosen_theme: Mapped[str | None] = mapped_column("chosen theme", String)