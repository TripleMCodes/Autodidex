import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging
# import date
logging.basicConfig(level=logging.DEBUG)


class Cp_tracker():

    def __init__(self):
        self.db_path = Path(__file__).parent / "autodidex.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn_cursor = self.conn.cursor()
        self.table_name_one = "cerebral_pursuits"
        self.table_name_two = "check_marks"

    def _commit_data(self):
        """Commits data to the data (does not close connection)"""
        self.conn.commit()

    def _get_user_id(self) -> int | None:
        """Get the id of current user"""
        query = f"SELECT uid FROM user_info;"
        try:
            self.conn_cursor.execute(query)
            uid = int(self.conn_cursor.fetchone()[0])
            return uid
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return

    def insert_cp(self, cp:str) -> dict:
        """Add a new cerebral pursuit"""

        query = f"""INSERT INTO cerebral_pursuits (subject, uid) 
                VALUES (?,?);"""
        uid = self._get_user_id()
        try:
            self.conn_cursor.execute(query, (cp, uid))
            self._commit_data()
            return {"message": f"{cp} successfully add!", "status": True}
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"message": "Subject already added", "status": False}
        except Exception as e:
            logging.debug(f"An error occured: {e}")
            return {"status": False}
        
    def get_cerebral_pursuits(self) -> list:
        """Gets all the cerebral pursuits previous saved"""
        query = f"SElECT * FROM {self.table_name_one};"
        cp_list = []

        try:
            self.conn_cursor.execute(query)
            cp_data = self.conn_cursor.fetchall()
            for i in range(len(cp_data)):
                cp_list.append(cp_data[i][1])
            return cp_list
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return None
    
    def get_cp_id(self, cp:str) -> int:
        """Get the id of a given cp"""

        query = f"""SELECT id FROM {self.table_name_one}
                    WHERE subject = ?;"""    
        try:
            self.conn_cursor.execute(query, (cp,))
            id = self.conn_cursor.fetchone()[0]
            return id
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
    
    def save_cp(self, row:int, state:dict, cp:str, day:str) -> dict | None:
        """Saves the position of check mark  on the table"""

        id = self.get_cp_id(cp)
        state = json.dumps(state)
        query = f"""INSERT INTO {self.table_name_two} (row_id, subject_id, {day}) VALUES 
                    (?, ?, ?);"""
        try:
            self.conn_cursor.execute(query, (row, id, state,))
            self._commit_data()
            return {"message": "Done"}
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
    
    def get_check_marks(self) -> dict | None:
        """Get all the check marks for saved cerebral pursuits"""
        cp_dict = dict()
        query = f"SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday FROM {self.table_name_two};"
        try:
            self.conn_cursor.execute(query)
            cp_data = self.conn_cursor.fetchall()
            for tup in cp_data:
                for dct in tup:
                    if dct != None:
                        for k, v in json.loads(dct).items():
                            cp_dict[k] = v
            return cp_dict
        except Exception as e:
            logging.debug(f'An error occured: {e}')
            return
    
    def get_reset_date(self) -> datetime | None:
        """Gets the date to reset the app"""

        query = f"""SELECT reset_date FROM {self.table_name_two};"""
        try:
            self.conn_cursor.execute(query)
            dates = self.conn_cursor.fetchall()
            reset_date = dates[0][0]
            reset_date = datetime.strptime(reset_date, "%Y-%m-%d")
            return reset_date
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return
    
    def clear_cp_data(self) -> dict:
        """Clear all the check marks of the all cerebral pursuit saved along with dates"""
        query = f"DELETE FROM {self.table_name_two};"
        try:
            self.conn_cursor.execute(query)
            self._commit_data()
            return {"message": "cp data clearred, app reset", "status": True}
        except sqlite3.DatabaseError as e :
            logging.debug(f"An error occurred: {e}")
            return {"message": "Couldn't retrieve data", "status": False}
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return {"message": "An error occurred", "status": False}
     
    def update_cp(self, old_cp: str, new_cp: str) -> dict:
        """Rename a cerebral pursuit (subject)."""
        try:
            id = self.get_cp_id(old_cp)
        except Exception as e:
            logging.debug(f"Failed to find id for {old_cp}: {e}")
            return {"message": "Subject not found", "status": False}

        query = f"UPDATE {self.table_name_one} SET subject = ? WHERE id = ?;"
        try:
            self.conn_cursor.execute(query, (new_cp, id))
            self._commit_data()
            return {"message": f"{old_cp} renamed to {new_cp}", "status": True}
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"message": "A subject with that name already exists", "status": False}
            logging.debug(f"IntegrityError: {e}")
            return {"message": "Failed to rename subject", "status": False}
        except Exception as e:
            logging.debug(f"An error occurred while renaming: {e}")
            return {"message": "An error occurred", "status": False}

    def delete_cp(self, cp: str) -> dict:
        """Delete a cerebral pursuit and its related check marks."""
        try:
            id = self.get_cp_id(cp)
        except Exception as e:
            logging.debug(f"Failed to find id for {cp}: {e}")
            return {"message": "Subject not found", "status": False}

        try:
            # Remove related check_marks rows
            q1 = f"DELETE FROM {self.table_name_two} WHERE subject_id = ?;"
            self.conn_cursor.execute(q1, (id,))
            # Remove the subject
            q2 = f"DELETE FROM {self.table_name_one} WHERE id = ?;"
            self.conn_cursor.execute(q2, (id,))
            self._commit_data()
            return {"message": f"{cp} deleted", "status": True}
        except Exception as e:
            logging.debug(f"An error occurred while deleting {cp}: {e}")
            return {"message": "An error occurred", "status": False}

if __name__ == "__main__":

    cp_table = Cp_tracker()
    dt = cp_table.get_reset_date()
    today = str(datetime.now().date())
    today = datetime.strptime(today, "%Y-%m-%d")
    print(isinstance(today, datetime))
    print(isinstance(dt, datetime))
    print(dt)
    print(today)
    if today >= dt:
        print("the are the same")
    else:
        print('you know what this means')
    # print(datetime.now())

