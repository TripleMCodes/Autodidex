from db.engine import SessionLocal
from db.models import Theme

_VALID_MODES = {"dark", "light", "neutral"}


class ThemeService:

    def get_theme_mode(self, mode: str) -> str | None:
        """Get the stylesheet for a given mode ('dark', 'light', or 'neutral')."""
        if mode not in _VALID_MODES:
            raise ValueError(f"Unknown theme mode: {mode!r}")
        with SessionLocal() as session:
            row = session.get(Theme, 1)
            return getattr(row, mode) if row else None

    def insert_chosen_theme(self, theme: str) -> None:
        with SessionLocal() as session:
            row = session.get(Theme, 1)
            if row is None:
                return
            row.chosen_theme = theme
            session.commit()

    def get_chosen_theme(self) -> str | None:
        with SessionLocal() as session:
            row = session.get(Theme, 1)
            return row.chosen_theme if row else None