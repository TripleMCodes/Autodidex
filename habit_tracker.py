#==================================================================Imports=======================================================
#******************************************************************************************************************************** 
import datetime
import json
import logging
import os
import pickle
import sys
from collections import defaultdict
from PySide6.QtCore import Qt,QTimer
from datetime import date
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from PySide6.QtCore import QDate, QSize, Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (QApplication, QCheckBox,
                               QGraphicsDropShadowEffect, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QSizePolicy, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
#================================================================================================================================
#********************************************************************************************************************************
#==============================================================Cerebral Pursuit Tracker==========================================
class CPTracker(QWidget):
#----------------------------------------------------------------------Data fields-----------------------------------------------
    def __init__(self):
        super().__init__()
        win_icon = Path(__file__).parent / "Icons/icons8-to-do-list-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))
        self.setWindowTitle("Cerebral Pursuit Tracker")

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(180, 150, 255, 120))

        self.thm_pref = Path(__file__).parent / "v tab files/dashboard_config.json"

        # self.cpt_timer = QTimer(self)
        # self.cpt_timer.setInterval(2000)  # 2000 ms = 2 seconds
        # self.cpt_timer.timeout.connect(self.save_last_entered_habits)
        # self.cpt_timer.start()

        
#-----------------------------------------------------------------------StlyeSheets----------------------------------------------
        self.light_mode: Optional[str] = None
        self.dark_mode: Optional[str] = None

#-----------------------------------------------------------------------Main Layout-----------------------------------------------
        self.main_layout =  QHBoxLayout(self)
        self.main_layout.setObjectName("mainframe")
        
#-----------------------------------------------------------------Sidebar Widget-------------------------------------------------
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)  # Default width "background-color: #333;"
        self.sidebar.setStyleSheet(self.light_mode)

#---------------------------------------------------------------Sidebar Layout (Vertical)----------------------------------------
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

#------------------------------------------------------------Toggle Button (Collapses Sidebar)-----------------------------------
        self.menu_icon = Path(__file__).parent / "Icons/icons8-menu-48.png"
        self.x_icon = Path(__file__).parent / "Icons/icons8-close-64.png"
        self.toggle_btn = QPushButton("")  
        self.toggle_btn.setIcon(QIcon(str(self.x_icon)))
        self.toggle_btn.setIconSize(QSize(40, 40))
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

#-----------------------------------------------------------------app theme state------------------------------------------------
        self.mode: Optional[str] = None

#-------------------------------------------------------------------Sidebar Buttons----------------------------------------------
        p_icon = Path(__file__).parent / "Icons/icons8-progress-64.png"
        progress_btn = QPushButton("")
        progress_btn.setIcon(QIcon(str(p_icon)))
        progress_btn.setToolTip("progress")
        progress_btn.setIconSize(QSize(30, 30))
        progress_btn.clicked.connect(self.show_progress)

        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.thm_btn = QPushButton("")
        self.thm_btn.setIcon(QIcon(str(self.d_mode)))
        self.thm_btn.setIconSize(QSize(30, 30))
        self.thm_btn.clicked.connect(self.theme)

        exit_icon = Path(__file__).parent / "Icons/icons8-exit-sign-64.png"
        self.exit_btn = QPushButton("")
        self.exit_btn.setIcon(QIcon(str(exit_icon)))
        self.exit_btn.setIconSize(QSize(30, 30))
        self.exit_btn.setToolTip("exit")
        self.exit_btn.clicked.connect(self.exit_app)

        self.sidebar_layout.addWidget(progress_btn)
        self.sidebar_layout.addWidget(self.thm_btn)
        self.sidebar_layout.addWidget(self.exit_btn)

#------------------------------------------------------------Main Content Area---------------------------------------------------
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = ["Habits","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sundday"]
        self.counter = -1

        self.habit_tracker = QTableWidget()
        self.habit_tracker.setGraphicsEffect(self.shadow)
        self.habit_tracker.setAlternatingRowColors(True)
        self.habit_tracker.setRowCount(15)
        self.habit_tracker.setColumnCount(8)
        self.habit_tracker.horizontalHeader().setStretchLastSection(True)
        self.habit_tracker.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.habit_tracker.verticalHeader().setDefaultSectionSize(40)  # row heigh
        self.habit_tracker.setStyleSheet(self.light_mode)
        self.habit_tracker.setHorizontalHeaderLabels(header)

        for col in range(1, 8):
            for row in range(0,15):
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:25px;")
                checkbox.stateChanged.connect(lambda state, r=row, c=col: self.checkbox_changed(r, c, state))
                self.habit_tracker.setCellWidget(row, col, checkbox)



        layout.addWidget(self.habit_tracker)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

#------------------------------------------------------------------------Horizontal layout---------------------------------------
        h_layout = QHBoxLayout()

#---------------------------------------------------------------Creating an input box for habits---------------------------------
        self.input = QLineEdit()
        self.input.setStyleSheet(self.light_mode)
        self.input.setPlaceholderText("Enter habit here or double click Habit column...")
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input.returnPressed.connect(self.add_habit) 
        h_layout.addWidget(self.input)

        enter_icon = Path(__file__).parent / "Icons/icons8-enter-64.png"
        self.enter_btn = QPushButton("")
        self.enter_btn.setIcon(QIcon(str(enter_icon)))
        self.enter_btn.setIconSize(QSize(30, 30))
        self.enter_btn.setToolTip("enter")
        self.enter_btn.setStyleSheet(self.light_mode)
        self.enter_btn.clicked.connect(self.add_habit)
        h_layout.addWidget(self.enter_btn)

#----------------------------------------------------------------cell edit button------------------------------------------------
        edit_icon = Path(__file__).parent / "Icons/icons8-edit-64.png"
        self.edit_btn = QPushButton("")
        self.edit_btn.setIcon(QIcon(str(edit_icon)))
        self.edit_btn.setIconSize(QSize(30, 30))
        self.edit_btn.setToolTip("edit cell")
        self.edit_btn.setStyleSheet(self.light_mode)
        self.edit_btn.clicked.connect(self.edit_cell)
        h_layout.addWidget(self.edit_btn)

        layout.addLayout(h_layout)

#--------------------------------------------------------------Add Widgets to Main Layout----------------------------------------
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(layout)

        self.setLayout(self.main_layout)
        self.resize(600, 400)
        
        
        self.enable_check_box_change = False #checking checkboxes again when loading the app
        self.first_subject_checked = True #For taking the date when the first is logged
        self.date_of_first_checked = datetime.datetime.fromtimestamp(1682531274, datetime.timezone.utc) #stores the date when the first subject is checked
        self.end_date: Optional[int] = None
       
        # self.init_wrapper()

    def load_last_entered_habits(self):
        file = Path(__file__).parent / "habit tracker files/last saved.txt"
        try:
            with open(file, 'r') as f:
                habits = f.readlines()

                habits = [habit.strip() for habit in habits]
                for habit in habits:
                    logging.debug(habit)
                logging.debug('Done removing new line')

                habits = set(habits)

            logging.debug(f"Subjects in the list - {habits}")

            for habit in habits:
                if habit.strip():
                    self.counter += 1
                    logging.debug(habit)
                    item = QTableWidgetItem(habit.strip())
                    self.habit_tracker.setItem(self.counter, 0, item)
                    logging.debug(f"done! added {habit}")
        except FileNotFoundError:
            logging.deg("last saved.txt file not found")
            return
    
    def save_checkbox_states(self):
        """Save the state and position of checkboxes in the QTable."""
        self.enable_check_box_change = False
        logging.debug("checkbox_changed() disabled")
        file = Path(__file__).parent / "habit tracker files/last_saved_checkboxes.json"  

        states = {}

        for col in range(1, 8):
            for row in range(0, 15):
#--------------------------------------------------creates reference to the checkbox inside the QTable cell-----------------------
                checkbox = self.habit_tracker.cellWidget(row, col)
#---------------------------------------------------safe net: checks for cells with checkboxes------------------------------------
                if isinstance(checkbox, QCheckBox):
#----------------------------------------------------Save True/False for each position--------------------------------------------  
                    states[f"{row},{col}"] = checkbox.isChecked()

        with open(file, "w") as f:
            json.dump(states, f)

        logging.debug("✅ Checkbox states saved.")

    
    def load_checkbox_states(self):
        """Load and apply previously saved checkbox states."""
        
        file = Path(__file__).parent / "habit tracker files/last_saved_checkboxes.json"
        
        try:
            with open(file, "r") as f:
                states = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logging.debug("📂 No saved checkbox states found.")
            self.enable_check_box_change = True
            logging.debug("checkbox_changed() enabled")
            return

        for col in range(1, 8):
            for row in range(0, 15):
                checkbox = self.habit_tracker.cellWidget(row, col)
                if isinstance(checkbox, QCheckBox):  
                    key = f"{row},{col}"
                    if key in states:
                        checkbox.setChecked(states[key])
        self.enable_check_box_change = True
        logging.debug("checkbox_changed() enabled")
        logging.debug("✅ Checkbox states loaded.")


    def save_last_entered_habits(self):
        file = Path(__file__).parent / "habit tracker files/last saved.txt"
        
        file.open("w").close()
        self.counter = 0
        while self.counter < 15:
            item = self.habit_tracker.item(self.counter, 0)
            if item is not None:
                task = item.text().strip()
                if task:  # Only save non-empty, non-whitespace habits
                    with open(file, "a") as f:
                        logging.debug(f'subject is {task}')
                        f.write(task + "\n")
                        logging.debug(f"wrote {task} to file")
                self.counter += 1  # Always increment to avoid infinite loop
            else:
                break
        

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setIcon(QIcon(str(self.menu_icon)))
        else:
            self.sidebar.show()
            self.toggle_btn.setIcon(QIcon(str(self.x_icon)))

    def add_habit(self):
        
        habit = self.input.text()
        if habit.strip():
            item = QTableWidgetItem(habit)
            self.habit_tracker.setItem(self.counter, 0, item)
            logging.debug(f"done! added {habit}")
            self.input.clear()
            self.counter += 1
        else:
                QMessageBox.information(self, "WARNING", "Enter a valid habit")
        self.save_last_entered_habits()
       
        

    def edit_cell(self):
        row = self.habit_tracker.currentRow()
        col = self.habit_tracker.currentColumn()
        
        text = self.input.text()
        self.habit_tracker.setItem(row, col, QTableWidgetItem(text))
        self.input.clear()


    def checkbox_changed(self, row, col, state):
        if not self.enable_check_box_change:
            logging.debug(f"checkbox save state not enabled, {self.enable_check_box_change}")
            return

        header_item = self.habit_tracker.horizontalHeaderItem(col)
        if not header_item:
            return

        column_header = header_item.text()
        logging.debug(f"Column header at column {col}: {column_header}")

        item = self.habit_tracker.item(row, 0)
        if item is None:
            return

        cell_text = item.text()
        logging.debug(cell_text)

        dt = QDate(date.today()).toString('dddd, MMMM d, yyyy')
        logging.debug(f"Checkbox at ({row}, {col}) changed to {'checked' if state == 2 else 'unchecked'}")

        if state != 2:
            return  # Only proceed if checked

        state = "checked"
        file = Path(__file__).parent / "habit tracker files/subject_tracker.json"
        save_state_path = Path(__file__).parent / "habit tracker files/save_state.pkl"
        end_date_file = Path(__file__).parent / "habit tracker files/end_date.pkl"

#-----------------------------------------------------Load or initialize data----------------------------------------------------
        if file.exists():
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        key = cell_text
        logging.debug(f"Subject key: {key}")

        if key not in data or not data[key]:
            if self.first_subject_checked:
                self.date_of_first_checked = datetime.datetime.today()
                self.end_date = self.date_of_first_checked + datetime.timedelta(days=6)
            data[key] = [{
                "row": row,
                "col": col,
                "state": state,
                "date": dt,
                "streak": [True]
            }]
            with open(save_state_path, "wb") as f:
                pickle.dump(self.date_of_first_checked, f)
            logging.debug(f"First ✔️ for {key} — date saved.")

            with open(end_date_file, "wb") as f:
                pickle.dump(self.end_date, f)
                logging.debug(f"First check on {self.date_of_first_checked}App reset date is {self.end_date}")
        else:
            if isinstance(data[key], list) and data[key]:
                data[key][0]["streak"].append(True)
                logging.debug(f"Added ✔️ to {key}, streak length now {len(data[key][0]['streak'])}")
            else:
                logging.warning(f"Unexpected structure for {key} in subject_tracker.json")

#------------------------------------------------------------------Save data----------------------------------------------------
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def reset_app_state(self):

#-----------------------------------------------------------------Define file paths----------------------------------------------
        base_path = Path(__file__).parent / "habit tracker files"
        subject_tracker_file = base_path / "subject_tracker.json"
        last_checked_file = base_path / "last_saved_checkboxes.json"
        save_state_file = base_path / "save_state.pkl"
        subjects_file = base_path / "last saved.txt"
        end_date_file = base_path /"end_date.pkl"

#-----------------------------------------------------Initialize variables in case of early exception----------------------------
        data = {}
        checkbox_states = {}
        subjects = []

        try:
            if subject_tracker_file.exists():
                with subject_tracker_file.open('r') as f:
                    data = json.load(f)

            if save_state_file.exists() and os.path.getsize(save_state_file) > 0:
                with save_state_file.open("rb") as f:
                    self.date_of_first_checked = pickle.load(f)

            if last_checked_file.exists():
                with last_checked_file.open("r") as f:
                    checkbox_states = json.load(f)

            if subjects_file.exists():
                with subjects_file.open("r") as f:
                    subjects = f.readlines()
                    
            if end_date_file.exists():
                with open(end_date_file, "rb") as f:
                    self.end_date = pickle.load(f)

        except (FileNotFoundError, json.decoder.JSONDecodeError, EOFError, pickle.PickleError) as e:
            logging.debug(f"An error occurred while resetting: {e}")
            return  # Exit early if critical data is missing or corrupted

        logging.debug(f'Date of first checked: {self.date_of_first_checked}')

        if subject_tracker_file.exists() and os.path.getsize(subject_tracker_file) > 0:
            logging.debug(f"Subject tracker data: {data}")
            logging.debug(f"Subjects: {subjects}")
            logging.debug(f"Checkbox states: {checkbox_states}")

            if subjects:
                subject = subjects[0].strip()
                if subject in data and isinstance(data[subject], list) and data[subject]:
                    logging.debug(f"Streak for first subject '{subject}': {data[subject][0].get('streak')}")

            if self.save_weekly_progress(data, subjects):
                try:
                    last_checked_file.write_text("")
                    logging.debug("Cleared last checked file.")

                    subject_tracker_file.write_text("")
                    logging.debug("Cleared subject tracker file.")

                    save_state_file.write_bytes(b"")
                    logging.debug("Cleared save state file.")

                except Exception as e:
                    logging.error(f"Failed to clear files during reset: {e}")
        return
                        
    def init_wrapper(self):
        base_path = Path(__file__).parent / "habit tracker files"
        start_date_file = base_path / "save_state.pkl"
        end_date_file = base_path / "end_date.pkl"

        try:
            with open(start_date_file, "rb") as f:
                self.date_of_first_checked = pickle.load(f)

            with open(end_date_file, "rb") as f:
                self.end_date = pickle.load(f)

        except (FileNotFoundError, EOFError):
            logging.debug("start date in not found")
            
        self.end_date = self.date_of_first_checked #for testing

        if self.date_of_first_checked <= self.end_date:
            if self.load_reset_state():
                self.reset_app_state()
                self.load_last_entered_habits()
                self.enable_check_box_change = True
                logging.debug("app reset")
                self.save_reset_state("0")
                logging.debug("App has been reset")
            else:
                self.load_last_entered_habits()
                self.load_checkbox_states()
                self.enable_check_box_change = True
                logging.debug("App already reset")
        else:
            self.load_last_entered_habits()
            self.load_checkbox_states()
            self.save_reset_state("1")
            logging.debug("App not reset")
        self.load_themes()
        self.load_thm_pref()

    def save_weekly_progress(self, data, subjects):
        file = Path(__file__).parent / "habit tracker files/weekly_progress.json"
        weekly_progress = {}
        if file.exists():
            logging.debug(f"weekly_progress.json file exists.")
        else:
            file.parent.mkdir(parents=True, exist_ok=True)  # ensure directory exists
            with file.open("w") as f:
                json.dump({}, f)
            logging.debug("weekly_progress.json file created with empty dict.")
            
        i = 0
        while i < len(subjects):
            try:
                progress = data[subjects[i].strip()][0]["streak"]
                logging.debug(f"{subjects[i]} is {data[subjects[i].strip()][0]["streak"]}")
                weekly_progress[subjects[i]] = progress
            except KeyError:
                logging.debug(f"{subjects[i]} has no streak")
            i += 1

        # Save new data
        with file.open("w") as f:
            json.dump(weekly_progress, f, indent=4)
            logging.debug("Weekly progress saved")

        return True
    
    def load_reset_state(self):
        file = Path(__file__).parent / "habit tracker files/state.txt"
        with open(file, 'r') as f:
            self.reset_state = f.read()
            logging.debug(f'The reset state is: {self.reset_state}')
            self.reset_state = bool(int(self.reset_state))
            logging.debug(f'The reset state is: {self.reset_state}')
            return self.reset_state
    
    def save_reset_state(self, state):
        file = Path(__file__).parent / "habit tracker files/state.txt"
        with open(file, 'w') as f:
            f.write(state)

    def _load_habit_data(self, filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data

    def count_checkmarks(self, habit_data):
        counts = defaultdict(int)
        for habit, entries in habit_data.items():
            for entry in entries:
                if entry["state"] == "checked":
                    counts[habit] += 1
        return counts

    def plot_habit_barchart(self, counts):
        habits = list(counts.keys())
        frequencies = list(counts.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(habits, frequencies, color="mediumpurple", edgecolor="black")

#----------------------------------------------------------------Add count labels on top of bars---------------------------------
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 0.1, f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)

        plt.title("Habit Completion Frequency", fontsize=16)
        plt.xlabel("Habits", fontsize=12)
        plt.ylabel("Check-ins", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def load_themes(self):
        """loads the themes, and sets them to their data fields"""
        light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"
        dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"

#------------------------------------------------------------------------load light mode-----------------------------------------
        with open(light_mode_file, "r") as f:
            light_mode = f.read()
        self.light_mode = light_mode

#------------------------------------------------------------------load dark mode------------------------------------------------
        with open(dark_mode_file, "r") as f:
            dark_mode = f.read()
        self.dark_mode = dark_mode

    def theme(self):
#---------------------------------------------------------------------to dark mode-----------------------------------------------
        if self.mode == "light":
            self.sidebar.setStyleSheet(self.dark_mode)
            self.habit_tracker.setStyleSheet(self.dark_mode)
            self.input.setStyleSheet(self.dark_mode)
            self.enter_btn.setStyleSheet(self.dark_mode)
            self.edit_btn.setStyleSheet(self.dark_mode)
            self.thm_btn.setIcon(QIcon(str(self.l_mode)))
            self.setStyleSheet(self.dark_mode)
            self.mode = "dark"
        else:
#----------------------------------------------------------------------to light mode---------------------------------------------
            self.sidebar.setStyleSheet(self.light_mode)
            self.habit_tracker.setStyleSheet(self.light_mode)
            self.input.setStyleSheet(self.light_mode)
            self.enter_btn.setStyleSheet(self.light_mode)
            self.edit_btn.setStyleSheet(self.light_mode)
            self.setStyleSheet(self.light_mode)
            self.mode = "light"

    def load_thm_pref(self):
        """load saved theme preferrence"""
        try:
            with open(self.thm_pref, "r") as f:
                data = json.load(f)
                thm = data["mode"]
            self.mode = thm
        except (FileNotFoundError, json.decoder.JSONDecodeError):
#------------------------------------------------------------------set theme to default------------------------------------------
            self.mode = "dark"

        if self.mode == "dark":
            self.setStyleSheet(self.dark_mode)
        elif self.mode == "light":
            self.setStyleSheet(self.light_mode)

    def show_progress(self):
        file = Path(__file__).parent / "habit tracker files/subject_tracker.json"

        data = self._load_habit_data(file)
        count = self.count_checkmarks(data)
        self.plot_habit_barchart(count)

    def exit_app(self):
        self.save_checkbox_states()
        self.save_last_entered_habits()
        sys.exit()

# ======================================================================Run Application===========================================
# if __name__ == "__main__":
#     app = QApplication([])
#     window = CPTracker()
#     window.show()
#     app.exec()