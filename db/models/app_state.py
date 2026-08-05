from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
from db.types import JSONEncoded, PickleEncoded

class AppState(Base):
    __tablename__ = "autodidex"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sessions: Mapped[dict | None] = mapped_column(JSONEncoded)
    bank_details: Mapped[dict | None] = mapped_column(JSONEncoded)
    game_badges: Mapped[dict | None] = mapped_column(JSONEncoded)
    game_update_state: Mapped[dict | None] = mapped_column(JSONEncoded)
    overall_level: Mapped[dict | None] = mapped_column(JSONEncoded)
    store_items: Mapped[list | None] = mapped_column(JSONEncoded)
    subject_badges: Mapped[dict | None] = mapped_column(JSONEncoded)
    subject_levels: Mapped[dict | None] = mapped_column(JSONEncoded)
    username: Mapped[dict | None] = mapped_column(JSONEncoded)
    end_date: Mapped[object | None] = mapped_column(PickleEncoded)
    last_saved_habits: Mapped[list | None] = mapped_column(JSONEncoded)
    last_saved_checkboxes: Mapped[list | None] = mapped_column(JSONEncoded)
    first_date: Mapped[object | None] = mapped_column(PickleEncoded)
    state: Mapped[dict | None] = mapped_column(JSONEncoded)
    subject_tracker: Mapped[dict | None] = mapped_column(JSONEncoded)
    weekly_progress: Mapped[dict | None] = mapped_column(JSONEncoded)
    config: Mapped[dict | None] = mapped_column(JSONEncoded)
    temp: Mapped[dict | None] = mapped_column(JSONEncoded)
    dashboard_config: Mapped[dict | None] = mapped_column(JSONEncoded)