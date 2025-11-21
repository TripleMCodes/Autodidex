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
        self.bank_table = "bank"
    
    def _commit_data(self):
        """Commits data to data base (does not close connection)"""

        self.conn.commit()
#=========================================================User related=================================================

    def create_new_user(self, name:str) -> bool:
        """Create a new user"""

        query = f"""INSERT INTO {self.user_table} (name, overall_level) VALUES (?, 0);"""
        try:
            self.conn_cursor.execute(query, (name,))
            self._commit_data()
            self.starter_badge()
            self._create_bank()
            return True
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return False
        
    def get_user_name(self) -> str | None:
        """Gets the name of the user from db in the user in logged in."""

        query = f"SELECT name FROM {self.user_table};"

        try:
            self.conn_cursor.execute(query)
            name = self.conn_cursor.fetchone()[0]
            return name
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return None

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
        
    def _get_cp_id(self, cp:str) -> int:
        """Get the id of a given cp"""

        query = f"""SELECT id FROM cerebral_pursuits
                    WHERE subject = ?;"""    
        try:
            self.conn_cursor.execute(query, (cp,))
            id = self.conn_cursor.fetchone()[0]
            return id
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
        
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
#=====================================================================================================================
#========================================================bank related functions========================================        
    def _create_bank(self) -> None:
        "Creates bank 'account' for new user"

        query = f"INSERT INTO {self.bank_table} (uid, lumens, total_xp) VALUES (?, 0, 0);"
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (id,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f"An error occured: {e}")
            return

    def get_lumens_amount(self) -> int:
        """Get the amount of lumens"""

        query = f"SELECT lumens FROM {self.bank_table};"
        try:
            self.conn_cursor.execute(query)
            lumens = self.conn_cursor.fetchone()[0]
            return lumens
        except Exception as e:
            logging.debug(f'An error occurred: {e}')
            return 0
        
    def get_total_xp(self) -> int:
        """Get total xp amout"""
        
        query = f"SELECT total_xp FROM {self.bank_table};"
        try:
            self.conn_cursor.execute(query)
            total_xp = self.conn_cursor.fetchone()[0]
            return total_xp
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return 0
        
    def add_total_xp(self, new_amount: int) -> dict | None:
        """Increment total xp"""

        query = f"""UPDATE {self.bank_table}
                    SET total_xp = ?
                    WHERE uid = ?;"""
        id = self._get_user_id()
        current_amount = self.get_total_xp()
        new_amount = new_amount + current_amount

        try:
            self.conn_cursor.execute(query, (new_amount, id))
            self._commit_data()
            return {"msg": "total xp incremented"}
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
        
    def add_lumens(self, amount):
        """Increment total lumens"""

        query = f"""UPDATE bank
                    SET lumens = ?
                    WHERE uid = ?;"""
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (amount, id,))
            self._commit_data()
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
        finally:
            return 
#=========================================================overlevel related============================================
    def increment_overall_level(self, new_level:int):
        """Increases the overall level"""

        query = f"""UPDATE user_info
                    SET overall_level = ?
                    WHERE uid = ?;"""
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (new_level, id,))
            self._commit_data()
        except Exception as e:
            logging.debug(f"An error occurred: {e}")

    def add_new_badge(self, badge_name:str) -> dict | None:
        """Add a new overall level badge"""

        query = f"""INSERT INTO badges_and_titles (badge, uid)
                        VALUES (?,?);"""
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (badge_name, id,))
            self._commit_data()
            return {"message": "new badge added"}
        except Exception as e:
            logging.debug(f"An error occurred: {e}")

    def add_cp_badge(self, badge_name: str, cp:str) -> dict | None:
        """Add badge for a particular cp"""

        query = f"""INSERT INTO badges_and_titles (badge, uid, subject_id) 
                    VALUES (?,?,?);"""
        cp_id = self._get_cp_id(cp)
        uid = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (badge_name, uid, cp_id,))
            self._commit_data()
            return {"message": f"new badge added: {badge_name}"}
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
        
    def _delete_all_badges(self):
        """Deletes all badges of user"""

        query = f"DELETE FROM badges_and_titles WHERE ?;"
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (id,))
            self._commit_data()
            return
        except Exception as e:
            logging.debug(f'An error occurred: {e}')
            return
        
    def _delete_bank(self):
        """Clear bank details of user"""

        query = f"DELETE FROM bank WHERE uid = ?"
        id = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (id,))
            self._commit_data()
        except Exception as e:
            logging.debug(f'An error occurred: {e}')

    def _reset_active_state(self) -> None:
        """logs out all user"""
        
        self.update_is_active_state(0)
        return

    
if __name__ == "__main__":
    db = Dashboard()
    print(db.get_lumens_amount())
    print(db.get_total_xp())
    # print(db.)
    # print(db.get_user_state())
    # db._delete_active_user()
    # db._reset_active_state()
    # print(db.get_overall_level())