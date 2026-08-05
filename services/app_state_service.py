from db.engine import SessionLocal
from db.models import AppState

_VALID_COLUMNS = {
    "sessions", "bank_details", "game_badges", "game_update_state",
    "overall_level", "store_items", "subject_badges", "subject_levels",
    "username", "end_date", "last_saved_habits", "last_saved_checkboxes",
    "first_date", "state", "subject_tracker", "weekly_progress",
    "config", "temp", "dashboard_config",
}


class AppStateService:

    def insert_default_values(self, force: bool = False) -> None:
        with SessionLocal() as session:
            existing = session.get(AppState, 1)
            if existing and not force:
                return
            if existing and force:
                session.delete(existing)
                session.flush()

            row = AppState(
                id=1,
                sessions={"csv": "sessions,date,time studied"},
                bank_details={"total_xp": 0, "lumens": 0},
                game_badges={"badges": ["🎯 Every Ten Counts", "🖤 Every Ten K Counts"]},
                game_update_state={"state": True},
                overall_level={"overall_level": 0},
                store_items=[
                    {"Day-off": 1000, "half Day-off": 500,
                     "fifteen min off from any subject": 250,
                     "one song/vid while studying": 100},
                    {"🎯 Every Ten Counts": 50, "🖤 Every Ten K Counts": 100},
                ],
                subject_badges={},
                subject_levels={},
                username={"username": None, "userstate": False},
                end_date=None,
                last_saved_habits=[],
                last_saved_checkboxes=[],
                first_date=None,
                state={"state": 0},
                subject_tracker={},
                weekly_progress={},
                config={"dark_mode": False, "font_size": "10"},
                temp={"temp": ""},
                dashboard_config={"mode": "light"},
            )
            session.add(row)
            session.commit()

    def update_column_by_id(self, record_id: int, column: str, value) -> None:
        if column not in _VALID_COLUMNS:
            raise ValueError(f"Invalid column: {column}")
        with SessionLocal() as session:
            row = session.get(AppState, record_id)
            if row is None:
                return
            setattr(row, column, value)
            session.commit()

    def update_multiple_columns_by_id(self, record_id: int, data: dict) -> None:
        with SessionLocal() as session:
            row = session.get(AppState, record_id)
            if row is None:
                return
            for column, value in data.items():
                if column not in _VALID_COLUMNS:
                    raise ValueError(f"Invalid column: {column}")
                setattr(row, column, value)
            session.commit()

    def get_column_value_by_id(self, column: str, record_id: int):
        if column not in _VALID_COLUMNS:
            raise ValueError(f"Invalid column: {column}")
        with SessionLocal() as session:
            row = session.get(AppState, record_id)
            return getattr(row, column) if row else None

    def get_all_data_in_row(self, record_id: int) -> dict | None:
        with SessionLocal() as session:
            row = session.get(AppState, record_id)
            if row is None:
                return None
            return {col: getattr(row, col) for col in _VALID_COLUMNS}