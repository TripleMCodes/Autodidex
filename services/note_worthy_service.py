from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from db.engine import SessionLocal
from db.models import Notebook, Note, NoteLink


class NoteWorthyService:

    # ---------- notebooks ----------

    def add_notebook(self, name: str) -> dict:
        with SessionLocal() as session:
            exists = session.execute(
                select(Notebook).where(Notebook.name == name)
            ).scalar_one_or_none()
            if exists:
                return {"message": "Notebook name already exists"}
            notebook = Notebook(name=name)
            session.add(notebook)
            session.commit()
            session.refresh(notebook)
            return {"message": "Notebook created successfully", "notebook_id": notebook.id}

    def rename_notebook(self, notebook_id: int, new_name: str) -> dict:
        with SessionLocal() as session:
            name_taken = session.execute(
                select(Notebook).where(Notebook.name == new_name)
            ).scalar_one_or_none()
            if name_taken:
                return {"message": "New notebook name already exists"}
            notebook = session.get(Notebook, notebook_id)
            if notebook is None:
                return {"message": "Notebook not found"}
            notebook.name = new_name
            session.commit()
            return {"message": "Notebook name updated successfully", "notebook_id": notebook.id}

    def delete_notebook(self, notebook_id: int) -> dict:
        with SessionLocal() as session:
            notebook = session.get(Notebook, notebook_id)
            if notebook is None:
                return {"message": "Notebook not found"}
            session.delete(notebook)  # cascades to notes
            session.commit()
            return {"message": "Notebook and its notes deleted successfully"}

    def get_all_notebooks(self) -> dict:
        with SessionLocal() as session:
            names = session.execute(select(Notebook.name)).scalars().all()
            return {"notebooks": names, "notebook_number": len(names)}

    def get_notebooks_with_notes(self) -> dict:
        """Eager-loads notes per notebook in one query — replaces the raw
        json_group_array trick with SQLAlchemy's selectinload."""
        with SessionLocal() as session:
            notebooks = session.execute(
                select(Notebook).options(selectinload(Notebook.notes)).order_by(Notebook.name)
            ).scalars().all()
            return {
                "notebooks": [
                    {
                        "id": nb.id,
                        "name": nb.name,
                        "notes": [
                            {
                                "id": n.id,
                                "title": n.title,
                                "content": n.content,
                                "created_at": n.created_at,
                                "updated_at": n.updated_at,
                            }
                            for n in nb.notes
                        ],
                    }
                    for nb in notebooks
                ]
            }

    def get_single_notebook_with_notes(self, notebook_id: int) -> dict:
        with SessionLocal() as session:
            notebook = session.execute(
                select(Notebook)
                .options(selectinload(Notebook.notes))
                .where(Notebook.id == notebook_id)
            ).scalar_one_or_none()
            if notebook is None:
                return {"message": "Notebook not found"}
            return {
                "notebook_name": notebook.name,
                "notes": [
                    {"id": n.id, "title": n.title, "content": n.content,
                     "created_at": n.created_at, "updated_at": n.updated_at}
                    for n in notebook.notes
                ],
            }

    # ---------- notes ----------

    def add_note(self, notebook_id: int, title: str, content: str) -> dict:
        with SessionLocal() as session:
            notebook = session.get(Notebook, notebook_id)
            if notebook is None:
                return {"message": "Notebook not found"}
            note = Note(notebook_id=notebook_id, title=title, content=content)
            session.add(note)
            session.commit()
            session.refresh(note)
            return {"message": "Note added successfully", "note_id": note.id}

    def update_note_content(self, note_id: int, new_content: str) -> dict:
        with SessionLocal() as session:
            note = session.get(Note, note_id)
            if note is None:
                return {"message": "Note not found"}
            note.content = new_content
            session.commit()
            return {"message": "Note saved successfully", "note_id": note.id}

    def update_note_title(self, note_id: int, new_title: str) -> dict:
        with SessionLocal() as session:
            note = session.get(Note, note_id)
            if note is None:
                return {"message": "Note not found"}
            note.title = new_title
            session.commit()
            return {"message": "Note title updated successfully"}

    def get_single_note(self, note_id: int) -> dict:
        with SessionLocal() as session:
            note = session.get(Note, note_id)
            if note is None:
                return {"message": "Note not found"}
            return {
                "note": {
                    "id": note.id, "title": note.title, "content": note.content,
                    "created_at": note.created_at, "updated_at": note.updated_at,
                }
            }

    def delete_note(self, note_id: int) -> dict:
        with SessionLocal() as session:
            note = session.get(Note, note_id)
            if note is None:
                return {"message": "Note not found"}
            session.delete(note)
            session.commit()
            return {"message": "Note deleted successfully"}

    # ---------- note links ----------

    def link_notes(self, source_note_id: int, target_note_id: int) -> dict:
        """Bidirectional link: inserts both directions so a query on either
        note_id returns all its linked notes."""
        if source_note_id == target_note_id:
            return {"message": "Cannot link a note to itself"}
        with SessionLocal() as session:
            for a, b in ((source_note_id, target_note_id), (target_note_id, source_note_id)):
                existing = session.execute(
                    select(NoteLink).where(
                        NoteLink.source_note_id == a, NoteLink.target_note_id == b
                    )
                ).scalar_one_or_none()
                if existing is None:
                    session.add(NoteLink(source_note_id=a, target_note_id=b))
            session.commit()
            return {"message": "Notes linked successfully"}

    def unlink_notes(self, source_note_id: int, target_note_id: int) -> dict:
        with SessionLocal() as session:
            session.execute(
                delete(NoteLink).where(
                    ((NoteLink.source_note_id == source_note_id) & (NoteLink.target_note_id == target_note_id))
                    | ((NoteLink.source_note_id == target_note_id) & (NoteLink.target_note_id == source_note_id))
                )
            )
            session.commit()
            return {"message": "Notes unlinked successfully"}

    def get_links_for_note(self, note_id: int) -> dict:
        with SessionLocal() as session:
            rows = session.execute(
                select(Note, Notebook)
                .join(NoteLink, NoteLink.target_note_id == Note.id)
                .join(Notebook, Notebook.id == Note.notebook_id)
                .where(NoteLink.source_note_id == note_id)
                .order_by(Notebook.name, Note.title)
            ).all()
            return {
                "links": [
                    {
                        "note_id": note.id,
                        "note_title": note.title,
                        "note_content": note.content,
                        "notebook_id": notebook.id,
                        "notebook_name": notebook.name,
                    }
                    for note, notebook in rows
                ]
            }