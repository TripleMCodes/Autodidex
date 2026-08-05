from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.engine import SessionLocal
from db.models import CerebralPursuit, CheckMark, UserInfo
import json
import logging

logging.basicConfig(level=logging.DEBUG)


class CpTrackerService:

    def _get_user_id(self, session) -> int | None:
        """Get the id of current user"""
        user = session.execute(select(UserInfo)).scalars().first()
        return user.uid if user else None

    def insert_cp(self, cp: str) -> dict:
        """Add a new cerebral pursuit"""
        with SessionLocal() as session:
            uid = self._get_user_id(session)
            new_cp = CerebralPursuit(subject=cp, uid=uid)
            session.add(new_cp)
            try:
                session.commit()
                return {"message": f"{cp} successfully added!", "status": True}
            except IntegrityError:
                session.rollback()
                return {"message": "Subject already added", "status": False}
            except Exception as e:
                session.rollback()
                logging.debug(f"An error occurred: {e}")
                return {"status": False}

    def get_cerebral_pursuits(self) -> list[str]:
        """Gets all the cerebral pursuits previously saved"""
        with SessionLocal() as session:
            rows = session.execute(select(CerebralPursuit)).scalars().all()
            return [row.subject for row in rows]

    def get_cp_specific_xp(self, cp: str) -> int | None:
        """Get xp of a specific cp"""
        with SessionLocal() as session:
            row = session.execute(
                select(CerebralPursuit).where(CerebralPursuit.subject == cp)
            ).scalar_one_or_none()
            return row.subject_xp if row else None

    def save_cp_xp(self, cp: str, xp: int) -> None:
        """Adds xp to the subject's running total"""
        with SessionLocal() as session:
            row = session.execute(
                select(CerebralPursuit).where(CerebralPursuit.subject == cp)
            ).scalar_one_or_none()
            if row is None:
                return
            row.subject_xp += xp
            session.commit()

    def delete_cp(self, cp: str) -> dict:
        """Delete a cerebral pursuit and its related check marks"""
        with SessionLocal() as session:
            row = session.execute(
                select(CerebralPursuit).where(CerebralPursuit.subject == cp)
            ).scalar_one_or_none()
            if row is None:
                return {"message": "Subject not found", "status": False}
            session.delete(row)  # cascade handles check_marks
            session.commit()
            return {"message": f"{cp} deleted", "status": True}