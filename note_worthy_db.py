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
        if name_check:
            query = f"INSERT INTO {self.notebooks_table_name} (name) VALUES (?);"
            try:
                self.conn_cursor.execute(query, (name,))
                self._commit_data()
                return {"message": "Notebook created successfully"}
            except sqlite3.Error as e:
                logging.debug("Couldn't create notebook, error: {e}")
        else:
            return {'message': "Notebook name already exists"}

    def _check_note_book(self, name:str):
        """check for the note book name in database"""
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
        
if __name__ == "__main__":
    notes = Notes()
    print(notes._check_note_book("Test Notebook"))