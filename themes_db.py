import sqlite3
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG)

class Themes():

    def __init__(self):
        self.db_path = Path(__file__).parent / "autodidex.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn_cursor = self.conn.cursor()
        self.themes_table_name = 'themes'

    def _commit_data(self):
        """Commits data to the data base (does not close connection)"""
        self.conn.commit()

    def get_theme_mode(self, theme:str) -> str:
        """Get theme"""

        query = f"""SELECT {theme} from {self.themes_table_name} 
                    WHERE id = 1;"""
        try:
            self.conn_cursor.execute(query)
            light_mode = self.conn_cursor.fetchone()
            logging.debug(light_mode)
        except Exception as e:
            logging.debug(f"An error occurred {e}")
    
    def insert_chosen_theme(self, theme:str):
        """Save chosen theme"""

        query = f"""UPDATE {self.themes_table_name}
                    SET "chosen theme" = ? WHERE id = 1;"""
        try:
            self.conn_cursor.execute(query, (theme,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
    


if __name__ == "__main__":
    themes = Themes()
    # themes.get_theme_mode("neutral")
    themes.insert_chosen_theme("neutral")
