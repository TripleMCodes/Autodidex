import sqlite3
import json
import pickle
from pathlib import Path
import datetime
import logging
import pyinputplus as pyip
from typing import Any
from typing import Optional
logging.basicConfig(level=logging.DEBUG)


class AutodidexDB:

    def __init__(self, db_path: Optional[Path] = None):
        self.base_path = db_path or Path(__file__).parent
        self.conn = sqlite3.connect(self.base_path / "autodidex.db")
        self.conn_cursor = self.conn.cursor()
        self.db_state: Optional[bool] = None
        self.state_file = self.base_path / "db_state.json"

        self.columns = {
            "sessions": "TEXT",
            "bank_details": "TEXT",
            "game_badges": "TEXT",
            "game_update_state": "TEXT",
            "overall_level": "TEXT",
            "store_items": "TEXT",
            "subject_badges": "TEXT",
            "subject_levels": "TEXT",
            "username": "TEXT",
            "end_date": "BLOB",
            "last_saved_habits": "TEXT",
            "last_saved_checkboxes": "TEXT",
            "first_date": "BLOB",
            "state": "TEXT",
            "subject_tracker": "TEXT",
            "weekly_progress": "TEXT",
            "config": "TEXT",
            "temp": "TEXT",
            "dashboard_config": "TEXT"
        }

        self.json_columns = [    
                        "username", "bank_details", 
                        "game_badges", "game_update_state", 
                        "overall_level", "store_items", "subject_badges", "subject_levels", 
                        "sessions", "last_saved_habits", "last_saved_checkboxes", 
                        "subject_tracker", "weekly_progress", "config", "dashboard_config"
                        ]

        self.pickle_columns = ["end_date", "first_date"]

        self.table_name = "autodidex"

        # Initialize DB state
        self.db_created()
        if not self.db_state:
            self.create_table()

    def save_db_state(self):
        """Marks the DB as created in a JSON state file."""
        self.db_state = True
        with open(self.state_file, "w") as f:
            json.dump({"db_state": True}, f, indent=4)

    def db_created(self):
        """Loads the state of db creation."""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.db_state = data.get("db_state", False)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.warning("Failed to load db_state.json, assuming DB not created.")
            self.db_state = False


    def commit_data(self):
        """Commits data to the database (does NOT close connection)."""
        self.conn.commit()

    def create_table(self):
        """Creates the autodidex table if it doesn't exist."""
        if not self.db_state:
            column_definitions = ",\n    ".join(
                [f"{column} {datatype}" for column, datatype in self.columns.items()]
            )
            self.conn_cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {column_definitions}
                )
                """
            )
            self.conn.commit()
            self.save_db_state()
            logging.info("Database initialized.")

    def insert_default_values(self, force=False):
        """Inserts default values into the {self.table_name} table."""
        if self.table_exists() and not force:
            logging.info("Table already exists, skipping default values insertion.")
            return  # Skip insertion if table already exists not forcing it
        self.create_table()  # Ensure the table is created before inserting default values
       
        if not self.db_state or force:
            logging.info("Inserting default values into the database.")
            default_values = {
                "sessions": json.dumps({"csv": "sessions,date,time studied"}),
                "bank_details": json.dumps({"total_xp": 0, "lumens": 0}),
                "game_badges": json.dumps({
                    "badges": [
                        "🎯 Every Ten Counts", 
                        "🖤 Every Ten K Counts"
                        ]
                }),
                "game_update_state": json.dumps({"state": True}),
                "overall_level": json.dumps({"overall_level": 0}),
                "store_items": json.dumps([
                    {
                        "Day-off": 1000,
                        "half Day-off": 500,
                        "fifteen min off from any subject": 250,
                        "one song/vid while studying": 100
                    },
                    {
                        "🎯 Every Ten Counts": 50,
                        "🖤 Every Ten K Counts": 100
                    }
                ]),
                "subject_badges": json.dumps({}),
                "subject_levels": json.dumps({}),
                "username": json.dumps({"username": None, "userstate": False}),
                "end_date": pickle.dumps(None),
                "last_saved_habits": json.dumps([]),
                "last_saved_checkboxes": json.dumps([]),
                "first_date": pickle.dumps(None),
                "state": json.dumps({"state": 0}),
                "subject_tracker": json.dumps({}),
                "weekly_progress": json.dumps({}),
                "config": json.dumps({"dark_mode": False, "font_size": "10"}),
                "temp": json.dumps({"temp": ""}),
                "dashboard_config": json.dumps({"mode": "light"})
            }
            placeholders = ", ".join(["?"] * len(default_values))
            columns = ", ".join(default_values.keys())
            self.conn_cursor.execute(
                f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                tuple(default_values.values())
            )
            self.commit_data()
            logging.info("Default values inserted into the database.")

    def update_column_by_id(self, record_id: int, column: str, value: Any):
        """Updates a specific column for a given record ID, auto-handling JSON and pickle types."""

        if column not in self.columns:
            raise ValueError(f"Invalid column: {column}")

        if column in self.json_columns:
                value = json.dumps(value)

        elif column in self.pickle_columns:
            value = pickle.dumps(value)

        self.conn_cursor.execute(
            f"UPDATE {self.table_name} SET {column} = ? WHERE id = ?",
            (value, record_id)
        )
        self.commit_data()
        logging.debug("Column updated")

    def update_multiple_columns_by_id(self, record_id:int, data: dict):
        """
            updates multiple columns for a given ID.
            Auto-converts  values based on column type (JSON/pickle.)
            Example:
                db.update_multiple_columns_by_id(1, {
                    "username": {"username": "new_user", "userstate": True},
                    "overall_level": {"overall_level": 5},
                    "sessions": {"csv": "sessions,date,time studied"}
                })
        """
        
        fields = []
        values = []
        for columns, value in data.items():
            if columns in self.json_columns:
                value = json.dumps(value)
            elif columns in self.pickle_columns:
                value = pickle.dumps(value)

            fields.append(f"{columns} = ?")
            values.append(value)

        values.append(record_id)
        query = f"UPDATE {self.table_name} SET {', '.join(fields)} WHERE id = ?"
        self.conn_cursor.execute(query, values)
        self.commit_data()
        logging.debug("Multiple columns updated")

    def get_column_value_by_rowid(self, column: str, record_id: int):
        """Get the value of a specific column in a row identified by record_id."""

        if column not in self.columns:
            raise ValueError(f"Invalid column: {column}")
        
        query = f"SELECT {column} FROM {self.table_name} WHERE rowid = ?"
        self.conn_cursor.execute(query, (record_id,))
        result = self.conn_cursor.fetchone()
        logging.debug("Data retrieved")
        return result[0] if result else None

    def get_all_data_in_row(self, record_id:int):
        """Fetches all the data in a row"""

        query = f"SELECT * FROM {self.table_name} WHERE rowid = ?"
        self.conn_cursor.execute(query, (record_id,))
        results = self.conn_cursor.fetchall()
        logging.debug("Data from specified row retrieved")
        return results if results else None


    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def _del_table(self, confirm=False):
        """Deletes the table from the database."""
        if self.table_exists():
            if not confirm:
                response = pyip.inputYesNo("Are you sure you want to delete the table? (yes/no) ")
                if response != "yes":
                    print("Table deletion cancelled.")
                    return
            query = f"DROP TABLE {self.table_name}"
            self.conn_cursor.execute(query)
            self.commit_data()
            logging.info("Table deleted.")


    def table_exists(self):
        self.conn_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
        return bool(self.conn_cursor.fetchone())


          
if __name__ == "__main__":
    db = AutodidexDB()
    db.insert_default_values(force=True)
    logging.debug(db.get_all_data_in_row(1))
    logging.debug("\n")
    logging.debug(db.update_column_by_id(1, "username", {"username": "Karina", "userstate": True}))
    logging.debug("\n")
    logging.debug(db.get_column_value_by_rowid("username", 1))
    db.close_connection()