import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)


class Notes():
    """A class that deal with user-note queries"""

    def __init__(self):
        self.db_path = Path(__file__).parent / "autodidex.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn_cursor = self.conn.cursor()
        self.notebooks_table_name = "notebooks"
        self.notes_table_name = "notes"

    def _commit_data(self):
        """Commits data to the data base (does not close connection)"""
        self.conn.commit()

    def Insert_a_new_notebook(self, name:str):
        """Add a new note book"""
        
        name_check = self._check_note_book(name)
        if not name_check:
            query = f"INSERT INTO {self.notebooks_table_name} (name) VALUES (?);"
            try:
                self.conn_cursor.execute(query, (name,))
                self._commit_data()
                return {"message": "Notebook created successfully"}
            except sqlite3.Error as e:
                logging.debug("Couldn't create notebook, error: {e}")
        else:
            return {'message': "Notebook name already exists"}
    
    def Insert_a_new_note(self, notebook_name:str, title:str, content:str):
        """Add a new note to a specific notebook"""
        notebook_id_query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(notebook_id_query, (notebook_name,))
            notebook_id = self.conn_cursor.fetchone()
            if notebook_id is None:
                return {"message": "Notebook not found"}
            notebook_id = notebook_id[0]
            insert_note_query = f"""INSERT INTO {self.notes_table_name} (notebook_id, title, content) VALUES (?, ?, ?);"""
            self.conn_cursor.execute(insert_note_query, (notebook_id, title, content))
            self._commit_data()
            return {"message": "Note added successfully"}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while adding note: {e}")
            return {"message": "Failed to add note"}

    
    def update_notebook_name(self, old_name:str, new_name:str):
        """updates the names of the notebook"""
        new_name_check = self._check_note_book(new_name)
        old_name_check = self._check_note_book(old_name)

        if not new_name_check and old_name_check:
            query = f"""UPDATE {self.notebooks_table_name} SET name = ? WHERE name = ?;"""
            try:
                self.conn_cursor.execute(query, (new_name, old_name))
                self._commit_data()
                return {"message": "Notebook name updated successfully"}
            except sqlite3.Error as e:
                logging.error(f"Error occurred while updating notebook name: {e}")
                return {"message": "Failed to update notebook name"}
        else:
            return {'message': "New notebook name already exists"}
        
    def update_note_content(self, notebook_name:str, note_title:str, new_content:str):
        """updates the content of a note"""
        notebook_id_query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(notebook_id_query, (notebook_name,))
            notebook_id = self.conn_cursor.fetchone()
            if notebook_id is None:
                return {"message": "Notebook not found"}
            notebook_id = notebook_id[0]
            update_note_query = f"""UPDATE {self.notes_table_name} SET content = ? WHERE notebook_id = ? AND title = ?;"""
            self.conn_cursor.execute(update_note_query, (new_content, notebook_id, note_title))
            self._commit_data()
            return {"message": "Note content updated successfully"}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while updating note content: {e}")
            return {"message": "Failed to update note content"}
    
    def update_note_title(self, notebook_name:str, old_title:str, new_title:str):
        """updates the title of a note"""
        notebook_id_query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(notebook_id_query, (notebook_name,))
            notebook_id = self.conn_cursor.fetchone()
            if notebook_id is None:
                return {"message": "Notebook not found"}
            notebook_id = notebook_id[0]
            update_note_query = f"""UPDATE {self.notes_table_name} SET title = ? WHERE notebook_id = ? AND title = ?;"""
            self.conn_cursor.execute(update_note_query, (new_title, notebook_id, old_title))
            self._commit_data()
            return {"message": "Note title updated successfully"}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while updating note title: {e}")
            return {"message": "Failed to update note title"}
    

    def get_all_notebooks(self):
        """retrieves all notebooks from the database"""
        query = f"""SELECT name FROM {self.notebooks_table_name};"""
        try:
            self.conn_cursor.execute(query)
            notebooks = self.conn_cursor.fetchall()
            notebook_list = [notebook[0] for notebook in notebooks]
            return {"notebooks": notebook_list, "notebook_number": len(notebook_list)}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while retrieving notebooks: {e}")
            return {"message": "Failed to retrieve notebooks"}
    
    def get_all_notes(self):
        """retrieves all notes from the database"""
        query = f"""SELECT title, content FROM {self.notes_table_name};"""
        try:
            self.conn_cursor.execute(query)
            notes = self.conn_cursor.fetchall()
            return {"notes": [{"title": note[0], "content": note[1]} for note in notes], "note_number": len(notes)}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while retrieving notes: {e}")
            return {"message": "Failed to retrieve notes"}
    
    def get_notebooks_with_notes(self):
        """retrieves notebooks with their notes from the database"""
        query = f"""SELECT
                notes.id,
                notes.title,
                notes.content,
                notes.created_at,
                notes.updated_at,
                notebooks.name AS notebook_name
            FROM notes
            JOIN notebooks ON notes.notebook_id = notebooks.id"""
        try:
            self.conn_cursor.execute(query)
            results = self.conn_cursor.fetchall()
            notebooks_with_notes = {}
            for note_id, title, content, created_at, updated_at, notebook_name in results:
                if notebook_name not in notebooks_with_notes:
                    notebooks_with_notes[notebook_name] = []
                notebooks_with_notes[notebook_name].append({
                    "id": note_id,
                    "title": title,
                    "content": content,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            return {"notebooks_with_notes": notebooks_with_notes}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while retrieving notebooks with notes: {e}")
            return {"message": "Failed to retrieve notebooks with notes"}

    def get_single_notebook_with_notes(self, notebook_name:str):
        """retrieves a single notebook with its notes from the database"""
        query = f"""SELECT
                notes.id,
                notes.title,
                notes.content,
                notes.created_at,
                notes.updated_at,
                notebooks.name AS notebook_name
            FROM notes
            JOIN notebooks ON notes.notebook_id = notebooks.id
            WHERE notebooks.name = ?;"""
        try:
            self.conn_cursor.execute(query, (notebook_name,))
            results = self.conn_cursor.fetchall()
            if not results:
                return {"message": "Notebook not found"}
            notebook_with_notes = {
                "notebook_name": notebook_name,
                "notes": []
            }
            for note_id, title, content, created_at, updated_at, _ in results:
                notebook_with_notes["notes"].append({
                    "id": note_id,
                    "title": title,
                    "content": content,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            return {"notebook_with_notes": notebook_with_notes}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while retrieving single notebook with notes: {e}")
            return {"message": "Failed to retrieve single notebook with notes"}
        
    def get_single_note(self, notebook_name:str, note_title:str):
        """retrieves a single note from a specific notebook"""
        query = f"""SELECT
                notes.id,
                notes.title,
                notes.content,
                notes.created_at,
                notes.updated_at,
                notebooks.name AS notebook_name
            FROM notes
            JOIN notebooks ON notes.notebook_id = notebooks.id
            WHERE notebooks.name = ? AND notes.title = ?;"""
        try:
            self.conn_cursor.execute(query, (notebook_name, note_title))
            result = self.conn_cursor.fetchone()
            if not result:
                return {"message": "Note not found"}
            note_id, title, content, created_at, updated_at, _ = result
            return {
                "note": {
                    "id": note_id,
                    "title": title,
                    "content": content,
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            }
        except sqlite3.Error as e:
            logging.error(f"Error occurred while retrieving single note: {e}")
            return {"message": "Failed to retrieve single note"}

    def delete_notebook(self, notebook_name:str):
        """deletes a notebook and its associated notes from the database"""
        notebook_id_query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(notebook_id_query, (notebook_name,))
            notebook_id = self.conn_cursor.fetchone()
            if notebook_id is None:
                return {"message": "Notebook not found"}
            notebook_id = notebook_id[0]
            delete_notes_query = f"""DELETE FROM {self.notes_table_name} WHERE notebook_id = ?;"""
            self.conn_cursor.execute(delete_notes_query, (notebook_id,))
            delete_notebook_query = f"""DELETE FROM {self.notebooks_table_name} WHERE id = ?;"""
            self.conn_cursor.execute(delete_notebook_query, (notebook_id,))
            self._commit_data()
            return {"message": "Notebook and its notes deleted successfully"}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while deleting notebook: {e}")
            return {"message": "Failed to delete notebook"}
    
    def delete_note(self, notebook_name:str, note_title:str):
        """deletes a specific note from a specific notebook"""
        notebook_id_query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(notebook_id_query, (notebook_name,))
            notebook_id = self.conn_cursor.fetchone()
            if notebook_id is None:
                return {"message": "Notebook not found"}
            notebook_id = notebook_id[0]
            delete_note_query = f"""DELETE FROM {self.notes_table_name} WHERE notebook_id = ? AND title = ?;"""
            self.conn_cursor.execute(delete_note_query, (notebook_id, note_title))
            self._commit_data()
            return {"message": "Note deleted successfully"}
        except sqlite3.Error as e:
            logging.error(f"Error occurred while deleting note: {e}")
            return {"message": "Failed to delete note"}

    
        
    def _check_note_book(self, name:str) -> bool | sqlite3.Error:
        """check for the note book name in database, returns True if notebook found"""
        query = f"""SELECT EXISTS(
                SELECT 1
                FROM {self.notebooks_table_name}
                WHERE name = ?
            );"""
    
        try:
            self.conn_cursor.execute(query, (name,))
            state = self.conn_cursor.fetchone()
            return bool(state[0])
        except sqlite3.Error as e:
            logging.error(f"Error occurred while checking note book: {e}")
            return False

    def _get_notebook_id(self, notebook_name:str) -> int | None:
        """Helper method to get notebook id from notebook name"""
        query = f"""SELECT id FROM {self.notebooks_table_name} WHERE name = ?;"""
        try:
            self.conn_cursor.execute(query, (notebook_name,))
            result = self.conn_cursor.fetchone()
            if result is None:
                return None
            return result[0]
        except sqlite3.Error as e:
            logging.error(f"Error occurred while getting notebook id: {e}")
            return None

    def _get_note_id(self, notebook_id:int, note_title:str) -> int | None:
        """Helper method to get note id from notebook id and note title"""
        query = f"""SELECT id FROM {self.notes_table_name} WHERE notebook_id = ? AND title = ?;"""
        try:
            self.conn_cursor.execute(query, (notebook_id, note_title))
            result = self.conn_cursor.fetchone()
            if result is None:
                return None
            return result[0]
        except sqlite3.Error as e:
            logging.error(f"Error occurred while getting note id: {e}")
            return None

class NotesService():
    def __init__(self):
        self._db = Notes()

    def add_notebook(self, name: str):
        return self._db.Insert_a_new_notebook(name)

    def add_note(self, notebook_id: int, title: str):
        return self._db.Insert_a_new_note(notebook_id, title)

    def rename_notebook(self, notebook_id: int, new_name: str):
        return self._db.update_notebook_name(notebook_id, new_name)

    def rename_note(self, note_id: int, new_name: str):
        return self._db.update_note_name(note_id, new_name)

    def delete_notebook(self, notebook_id: int):
        return self._db.delete_notebook_by_id(notebook_id)

    def delete_note(self, note_id: int):
        return self._db.delete_note_by_id(note_id)

if __name__ == "__main__":
    notes = Notes()
    print(notes._check_note_book("Test Notebook 2"))
    # created_notebook = notes.Insert_a_new_notebook("Test Notebook 2")
    # print(created_notebook)
    # added_note = notes.Insert_a_new_note("Test Notebook 2", "Test Note", "This is a test note.")
    # print(added_note)
    # updated_notebook = notes.update_notebook_name("Test Notebook 2", "Updated Test Notebook")  
    # print(updated_notebook)
