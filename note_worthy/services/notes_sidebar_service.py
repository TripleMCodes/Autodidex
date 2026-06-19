from note_worthy_db import Notes
from pydantic import BaseModel, Field, field_validator
import logging
logging.basicConfig(level=logging.DEBUG)

class Note(BaseModel):
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")

class NoteBook(BaseModel):
    name: str = Field(..., description="Name of the notebook")
    notes: list[Note] = Field(default_factory=list, description="List of notes in the notebook")

class NewNoteBook(BaseModel):
    name: str = Field(..., description="Name of the notebook")

class NewNote(BaseModel):
    notebook_name: str = Field(..., description="Name of the notebook to add the note to")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")

class RenameNoteBook(BaseModel):
    old_name: str = Field(..., description="Current name of the notebook")
    new_name: str = Field(..., description="New name for the notebook")

class RenameNote(BaseModel):
    notebook_name: str = Field(..., description="Name of the notebook containing the note")
    old_title: str = Field(..., description="Current title of the note")
    new_title: str = Field(..., description="New title for the note")   


class NotesService:

    def __init__(self):
        self._notes_db_class = Notes()

    def create_notebook(self, notebook_name) -> dict:
        """create a new notebook"""
        new_notebook = NewNoteBook(name=notebook_name)
        res = self._notes_db_class.Insert_a_new_notebook(new_notebook)
        return res
    
    def create_note(self, notebook_name:str, title:str, content:str) -> dict:
        """Create a new note in a notebook"""
        new_note = NewNote(notebook_name=notebook_name, title=title, content=content)
        res = self._notes_db_class.Insert_a_new_note(new_note)
        return res
    
    def rename_notebook(self, old_name:str, new_name:str) -> dict:
        """Rename notebook name"""
        res = self._notes_db_class.rename_notebook(old_name, new_name)
        return res

    def rename_note(self, notebook_name:str, old_title:str, new_title:str) -> dict:
        """Rename a note in a notebook"""
        res = self._notes_db_class.rename_note(notebook_name, old_title, new_title)
        return res

    def get_notebooks_and_notes(self) -> dict:
        """Gets notebooks and their respective notes"""
        res = self._notes_db_class.get_notebooks_with_notes()
        return res

    def get_notebooks(self) -> dict:
        """Get all notebooks with or without notes"""
        res = self._notes_db_class.get_notebooks_with_and_without_notes()
        return res
    
    def get_all_notes(self) -> dict:
        """Get all notes regardless of notebook"""
        res = self._notes_db_class.get_all_notes()
        return res
    
    def get_all_notebooks(self) -> dict:
        """Get all notebooks with notes (Notes have content)"""
        res = self._notes_db_class.get_all_notebooks()
        return res
    
    def get_notebook_with_notes(self, notebook_name:str) -> dict:
        """Get single notebook with notes"""
        res = self._notes_db_class.get_single_notebook_with_notes(notebook_name)
        return res
    
    def get_a_note(self, notebook_name:str, note:str) -> dict:
        """Get a single note from a notebook"""
        res = self._notes_db_class.get_single_note(notebook_name, note)
        return res
    
    def delete_notebook(self, notebook_name:str) -> dict:
        """Delete a notebook and all its notes"""
        res = self._notes_db_class.delete_notebook(notebook_name)
        return res  
    
    def delete_note(self, notebook_name:str, note:str) -> dict:
        """Delete a single note from a notebook"""
        res = self._notes_db_class.delete_note(notebook_name, note)
        return res

if __name__ == "__main__":
    n = NotesService()
    # res = n.get_notebooks()
    # print(res)
    # print(n.get_all_notes())
    print(n.get_notebook_with_notes("Updated Test Notebook"))