from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,QTableWidget, QTableWidgetItem,QLineEdit,QMessageBox, QCheckBox,QSizePolicy,QHeaderView
from PySide6.QtCore import Qt, QDate
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Optional
from collections import defaultdict
from style_sheet import StyleSheet
import pickle
import datetime
import json
import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SidebarMenu(QWidget):
    def __init__(self):
        super().__init__()

        #StlyeSheets
        self.base_style: Optional[str] = None
        self.dark_mode: Optional[str] = None

        # Main Layout
        self.load_themes()
        self.main_layout =  QHBoxLayout(self)
        # self.main_layout = QWidget()
        self.main_layout.setObjectName("mainframe")
        # self.load_themes()
        # qq = StyleSheet()
        
        # Sidebar Widget
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)  # Default width "background-color: #333;"
        self.sidebar.setStyleSheet(self.base_style)

        # Sidebar Layout (Vertical)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Toggle Button (Collapses Sidebar)
        self.toggle_btn = QPushButton("☰")  # Unicode for menu icon
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        #app theme state
        self.mode = "light mode"
        # Sidebar Buttons
        progress_btn = QPushButton("progress")
        progress_btn.clicked.connect(self.show_progress)
        self.thm_btn = QPushButton("🌙 Dark mode")
        self.thm_btn.clicked.connect(self.theme)
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self._exit)

        # # Style Buttons
        # for btn in [progress_btn, self.thm_btn, self.exit_btn]:
        #     btn.setStyleSheet("color: white; background: #444; border: none; padding: 10px;")
        self.sidebar_layout.addWidget(progress_btn)
        self.sidebar_layout.addWidget(self.thm_btn)
        self.sidebar_layout.addWidget(self.exit_btn)

        # Main Content Area
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = ["Habits","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sundday"]
        self.counter = -1

        self.habit_tracker = QTableWidget()
        self.habit_tracker.setRowCount(15)
        self.habit_tracker.setColumnCount(8)
        self.habit_tracker.horizontalHeader().setStretchLastSection(True)
        self.habit_tracker.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.habit_tracker.verticalHeader().setDefaultSectionSize(40)  # row heigh
        self.habit_tracker.setStyleSheet(self.base_style)
        self.habit_tracker.setHorizontalHeaderLabels(header)

        for col in range(1, 8):
            for row in range(0,15):
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:25px;")
                checkbox.stateChanged.connect(lambda state, r=row, c=col: self.checkbox_changed(r, c, state))
                self.habit_tracker.setCellWidget(row, col, checkbox)



        layout.addWidget(self.habit_tracker)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Horizontal layout
        h_layout = QHBoxLayout()

        #Creating an input box for habits
        self.input = QLineEdit()
        self.input.setStyleSheet(self.base_style)
        self.input.setPlaceholderText("Enter habit here or double click Habit column...")
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        h_layout.addWidget(self.input)

        self.enter_btn = QPushButton("Enter")
        self.enter_btn.setStyleSheet(self.base_style)
        self.enter_btn.clicked.connect(self.add_habit)
        h_layout.addWidget(self.enter_btn)

        #cell edit button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet(self.base_style)
        self.edit_btn.clicked.connect(self.edit_cell)
        h_layout.addWidget(self.edit_btn)

        layout.addLayout(h_layout)

        # Add Widgets to Main Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(layout)

        self.setLayout(self.main_layout)
        self.resize(600, 400)
        
        
        self.enable_check_box_change = False #checking checkboxes again when loading the app
        self.first_subject_checked = True #For taking the date when the first is logged
        self.date_of_first_checked = datetime.datetime.fromtimestamp(1682531274, datetime.timezone.utc) #stores the date when the first subject is checked
        self.init_wrapper()

    def load_last_entered_habits(self):
        file = Path(__file__).parent / "last saved.txt"
        try:
            with open(file, 'r') as f:
                habits = f.readlines()
            logging.debug(habits)
            for habit in habits:
                if habit != "\n":
                    self.counter += 1
                    logging.debug(habit)
                    item = QTableWidgetItem(habit.strip())
                    self.habit_tracker.setItem(self.counter, 0, item)
                    logging.debug(f"done! added {habit}")
        except FileNotFoundError:
            return
    
    def save_checkbox_states(self):
        """Save the state and position of checkboxes in the QTable."""
        self.enable_check_box_change = False
        logging.debug("checkbox_changed() disabled")
        file = Path(__file__).parent / "last_saved_checkboxes.json"  

        states = {}

        for col in range(1, 8):
            for row in range(0, 15):
                #creates reference to the checkbox inside the QTable cell
                checkbox = self.habit_tracker.cellWidget(row, col)
                 #safe net: checks for cells with checkboxes
                if isinstance(checkbox, QCheckBox):
                    # Save True/False for each position  
                    states[f"{row},{col}"] = checkbox.isChecked()

        with open(file, "w") as f:
            json.dump(states, f)

        logging.debug("✅ Checkbox states saved.")

    
    def load_checkbox_states(self):
        """Load and apply previously saved checkbox states."""
        
        file = Path(__file__).parent / "last_saved_checkboxes.json"
        
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
        file = Path(__file__).parent / "last saved.txt"
        open(file, "w").close()
        self.counter = 0
        while self.counter < 10:
            item = self.habit_tracker.item(self.counter, 0)
            if item != None:
                with open(file, "a") as f:
                    task = item.text()
                    f.write(task)
                    f.write("\n")
                    logging.debug(f"wrote {item.text()} to file")
                self.counter += 1
            else:
                break

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setText("☰")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("✖")

    def add_habit(self):
        self.counter += 1
        habit = self.input.text()
        if habit != "":
            item = QTableWidgetItem(habit)
            self.habit_tracker.setItem(self.counter, 0, item)
            logging.debug(f"done! added {habit}")
            self.input.clear()
        else:
            QMessageBox.information(self, "WARNING", "Enter a valid habit")

    def edit_cell(self):
        row = self.habit_tracker.currentRow()
        col = self.habit_tracker.currentColumn()
        
        text = self.input.text()
        self.habit_tracker.setItem(row, col, QTableWidgetItem(text))
        self.input.clear()


    def checkbox_changed(self, row, col, state):
        if self.enable_check_box_change:
            header_item = self.habit_tracker.horizontalHeaderItem(col)
            if header_item:
                column_header = header_item.text()
                logging.debug(f"Column header at column {col}: {column_header}")
            try:
                item = self.habit_tracker.item(row, 0)
                if item is not None:
                    cell_text = item.text()
                    logging.debug(cell_text)
                    dt = QDate(date.today()).toString('dddd, MMMM d, yyyy')
                    logging.debug(dt)
                logging.debug(f"Checkbox at ({row}, {col}) changed to {'checked' if state == 2 else 'unchecked'}")
                
                if state == 2:
                    state = "checked"
                    file = Path(__file__).parent / "subject_tracker.json"
                    
                    # Try to load existing data
                    if file.exists():
                        with open(file, 'r') as f:
                            try:
                                data = json.load(f)
                            except json.JSONDecodeError:
                                data = {}
                    else:
                        data = {}

                    key = cell_text     
                    logging.debug(key)
                        
                    if key not in data or not data[key]:
                        if self.first_subject_checked :
                            self.date_of_first_checked = datetime.date.today()

                        data[key] = [{
                            "row": row,
                            "col": col,
                            "state": state,
                            "date": dt,
                            "streak": [True]
                        }]
                        with open("save_state.pkl", "wb") as f:
                            pickle.dump(self.date_of_first_checked, f)
                        logging.debug(f"first ✔️ for {key}")
                    else:
                        data[key][0]["streak"].append(True)
                        logging.debug(f"added ✔️ to {key}")
                            
                    # Save back to file
                    with open(file, 'w') as f:
                            json.dump(data, f, indent=4)

            except UnboundLocalError:
                QMessageBox.warning(self, "Warning", "Can not check checkbox not associated with a subject.")
            logging.debug("done") 
            return 
    
    def reset_app_state(self):

        file = Path(__file__).parent / "subject_tracker.json"
        last_checked = Path(__file__).parent / "last_saved_checkboxes.json"
        file2 = Path(__file__).parent /"last saved.txt"

        try:
            with open(file, 'r') as f:
                data = json.load(f)

            with open("save_state.pkl", "rb") as f:
                self.date_of_first_checked = pickle.load(f)

            with open(last_checked, "r") as f:
                checkbox_states = json.load(f)
            
            with open(file2, "r") as f:
                subjects = f.readlines()
        except (FileNotFoundError,json.decoder.JSONDecodeError, EOFError) as e:
            logging.debug(f"An {e} occured while ressint")
        
        logging.debug(f'this is the date {self.date_of_first_checked}')
        
        if os.path.getsize(file) > 0:
            logging.debug(data)
            logging.debug(subjects)
            logging.debug(self.date_of_first_checked)
            logging.debug(checkbox_states)

            logging.debug(data[subjects[0].strip()][0]["streak"])
            
            if self.save_weekly_progress(data, subjects):
                open(last_checked, "w").close()
                logging.debug("last checked file cleared.")
                open(file,"w").close()
                logging.debug("subject tracker file cleared.")
                open("save_state.pkl", "wb").close()
                logging.debug("date of first checked file cleared.")
              
    def init_wrapper(self):
        try:
            with open("save_state.pkl", "rb") as f:
                self.date_of_first_checked = pickle.load(f)
        except (FileNotFoundError, EOFError):
            logging.debug("start date in not found")
        end_date = self.date_of_first_checked #+ datetime.timedelta(days=6)

        if self.date_of_first_checked == end_date:
            if self.load_reset_state():
                self.reset_app_state()
                self.load_last_entered_habits()
                self.enable_check_box_change = True
                logging.debug("app reset")
                self.save_reset_state("0")
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

    def save_weekly_progress(self,data, subjects):
        file = Path(__file__).parent / "weekly_progress.json"
        if file.exists():
            open(file).close()
            try:
                with open(file, "r") as f:
                    weekly_progress = json.load(f)
            except json.decoder.JSONDecodeError:
                logging.debug(f"{f} is empty")     
        else:
            weekly_progress = {}
        
        i = 0
        while i < len(subjects):
            try:
                progress = data[subjects[i].strip()][0]["streak"]
                logging.debug(f"{subjects[i]} is {data[subjects[i].strip()][0]["streak"]}")
                weekly_progress[subjects[i]] = progress
            except KeyError:
                logging.debug(f"{subjects[i]} has no streak")
            i += 1
        with open(file, "w") as f:
            json.dump(weekly_progress, f)
            logging.debug("Weekly progress saved")
        return True
    
    def load_reset_state(self):
        file = Path(__file__).parent / "state.txt"
        with open(file, 'r') as f:
            self.reset_state = f.read()
            logging.debug(f'The reset state is: {self.reset_state}')
            self.reset_state = bool(int(self.reset_state))
            logging.debug(f'The reset state is: {self.reset_state}')
            return self.reset_state
    
    def save_reset_state(self, state):
        file = Path(__file__).parent / "state.txt"
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

        # Add count labels on top of bars
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
        light_mode_file = Path(__file__).parent / "light_mode.txt"
        dark_mode_file = Path(__file__).parent / "dark_mode.txt"

        #load light mode
        with open(light_mode_file, "r") as f:
            light_mode = f.read()
        self.base_style = light_mode

        #load dark mode
        with open(dark_mode_file, "r") as f:
            dark_mode = f.read()
        self.dark_mode = dark_mode

    def theme(self):
        #to dark mode
        if self.mode == "light mode":
            self.sidebar.setStyleSheet(self.dark_mode)
            self.habit_tracker.setStyleSheet(self.dark_mode)
            self.input.setStyleSheet(self.dark_mode)
            self.enter_btn.setStyleSheet(self.dark_mode)
            self.edit_btn.setStyleSheet(self.dark_mode)
            self.thm_btn.setText("☀️ Light mode")
            self.mode = "dark mode"
        else:
            #to light mode
            self.sidebar.setStyleSheet(self.base_style)
            self.habit_tracker.setStyleSheet(self.base_style)
            self.input.setStyleSheet(self.base_style)
            self.enter_btn.setStyleSheet(self.base_style)
            self.edit_btn.setStyleSheet(self.base_style)
            self.thm_btn.setText("🌙 Dark mode")
            self.mode = "light mode"

    
    def show_progress(self):
        file = Path(__file__).parent / "subject_tracker.json"

        data = self._load_habit_data(file)
        count = self.count_checkmarks(data)
        self.plot_habit_barchart(count)

    def _exit(self):
        self.save_last_entered_habits()
        self.save_checkbox_states()
        sys.exit()

# Run Application
if __name__ == "__main__":
    app = QApplication([])
    window = SidebarMenu()
    window.show()
    app.exec()