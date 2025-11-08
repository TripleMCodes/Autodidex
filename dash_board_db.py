import sqlite3
from pathlib import Path
import logging
from datetime import datetime
logging.basicConfig(level=logging.DEBUG)

class Dashboard():

    def __init__(self):
        self.db_path = Path(__file__).parent / "autodidex.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn_cursor = self.conn.cursor()
        self.app_attr_table = "app_attr"
        self.badges_table = "badges_and_titles"
        self.user_table = "user_info"
    
    def _commit_data(self):
        """Commits data to data base (does not close connection)"""

        self.conn.commit()

    def create_new_user(self, name:str) -> bool:
        """Create a new user"""

        query = f"""INSERT INTO {self.user_table} (name, overall_level) VALUES (?, 0);"""
        try:
            self.conn_cursor.execute(query, (name,))
            self._commit_data()
            # self.starter_badge()
            return True
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return False

    def _get_user_id(self) -> int | None:
        """Get the id of current user"""
        query = f"SELECT uid FROM {self.user_table};"
        try:
            self.conn_cursor.execute(query)
            uid = int(self.conn_cursor.fetchone()[0])
            return uid
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
        
    def get_overall_level(self) -> int:
        """Get the overall xp level of active user"""

        query = f"""SELECT overall_level FROM {self.user_table};"""
        try:
            self.conn_cursor.execute(query)
            level = self.conn_cursor.fetchone()[0]
            return level
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return 0 #default

    def get_user_state(self) -> bool:
        """Checks if there is a user active"""

        query = f"SELECT is_active FROM {self.app_attr_table};"
        try:
            self.conn_cursor.execute(query)
            state = self.conn_cursor.fetchone()[0]
            state = bool(state)
            return state
        except Exception as e:
            logging.debug(f'An error as occurred: {e}')
            return False #return default
        
    def update_is_active_state(self, val:int) -> None:
        """Change based on whether there is a user logged in"""
        val = bool(val)
        query = f"""UPDATE {self.app_attr_table} 
                    SET is_active = ?;"""
        try:
            self.conn_cursor.execute(query,(val,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f'An error occurred: {e}')
            return
    
    def starter_badge(self) -> None:
        """Give a badge to new user"""

        query = f"""INSERT INTO {self.badges_table} (badge, id) VALUES(?,?);"""
        badge = "🔰Genesis"
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (badge, id,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
    
    def _delete_active_user(self) -> None:
        """Deletes active user"""

        query = f"""DELETE FROM user_info
                    WHERE uid = ?;"""
        id = self._get_user_id()

        if id == None:
            return
        try:
            self.conn_cursor.execute(query, (id,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f'An error occurred: {e}')
            return
    
    def _reset_active_state(self) -> None:
        """logs out all user"""
        
        self.update_is_active_state(0)
        return

    
if __name__ == "__main__":
    db = Dashboard()
    # db.update_is_active_state(0)
    # print(db.get_user_state())
    # db._delete_active_user()
    # db._reset_active_state()
    # print(db.get_overall_level())