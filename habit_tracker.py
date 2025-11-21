#==================================================================Imports=======================================================
#******************************************************************************************************************************** 
import datetime
import json
import logging
import random
import string
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
                               QTableWidgetItem, QVBoxLayout, QWidget,
                               QMenu, QInputDialog)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from cp_tracker_db import Cp_tracker
cp_table = Cp_tracker()
# logging.disable(logging.DEBUG)
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
        self.trigger_file = Path(__file__).parent / "update.txt" 
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

        header = ["Habits","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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

        # enable custom context menu for subjects (column 0)
        self.habit_tracker.setContextMenuPolicy(Qt.CustomContextMenu)
        self.habit_tracker.customContextMenuRequested.connect(self.show_subject_context_menu)

        layout.addWidget(self.habit_tracker)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
#------------------------------------------------------------------------Horizontal layout---------------------------------------
        h_layout = QHBoxLayout()
#---------------------------------------------------------------Creating an input box for habits---------------------------------
        self.input = QLineEdit()
        self.input.setStyleSheet(self.light_mode)
        self.input.setPlaceholderText("Enter habit here ")
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
    
        layout.addLayout(h_layout)
#--------------------------------------------------------------Add Widgets to Main Layout----------------------------------------
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(layout)

        self.setLayout(self.main_layout)
        self.resize(600, 400)
        
        self.enable_check_box_change = False #checking checkboxes again when loading the app
        self.end_date = cp_table.get_reset_date()
#------------------------------------------------------------init wrapper------------------------------------------------------       
        # self.init_wrapper()
#==========================================================methods begin here==================================================
    def load_last_entered_habits(self):
        """load the previously cerebral pursuits"""
        try:
            habits = cp_table.get_cerebral_pursuits() or []
            logging.debug(f"Subjects in the list - {habits}")

            # populate from row 0 downward and track next free index in self.counter
            for idx, habit in enumerate(habits):
                if habit and habit.strip():
                    logging.debug(habit)
                    item = QTableWidgetItem(habit.strip())
                    self.habit_tracker.setItem(idx, 0, item)
                    logging.debug(f"done! added {habit}")
            self.counter = len(habits)
        except FileNotFoundError:
            logging.deg("last saved.txt file not found")
            return
        
    def load_checkbox_states(self):
        """Load and apply previously saved checkbox states."""

        states = cp_table.get_check_marks()
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

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setIcon(QIcon(str(self.menu_icon)))
        else:
            self.sidebar.show()
            self.toggle_btn.setIcon(QIcon(str(self.x_icon)))
    
    def update_dashboard(self):
        """When a cp is added or updated this 
        triggers the dashboard to update cp list"""
        letters = string.ascii_letters
        random_string = "".join(random.choice(letters) for _ in range(26))
        with open(self.trigger_file, "w") as f:
            f.write(random_string)

    def add_habit(self):
        
        habit = self.input.text()
        if habit.strip():
            msg = cp_table.insert_cp(habit)
            if msg["status"] == False:
                QMessageBox.warning(self, "WARNING", msg["message"])
                return
            item = QTableWidgetItem(habit)
            self.habit_tracker.setItem(self.counter, 0, item)
            QMessageBox.information(self, "Successful", msg["message"])
            logging.debug(f"done! added {habit}")
            self.input.clear()
            self.counter += 1 
            self.update_dashboard()

        else:
                QMessageBox.warning(self, "WARNING", "Enter a valid habit")

    def show_subject_context_menu(self, pos):
        """Show right-click menu for subjects in column 0."""
        idx = self.habit_tracker.indexAt(pos)
        if not idx.isValid():
            return
        row = idx.row()
        col = idx.column()
        if col != 0:
            return
        item = self.habit_tracker.item(row, 0)
        if item is None or not item.text().strip():
            return
        subject = item.text()

        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")

        action = menu.exec(self.habit_tracker.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_subject(row, subject)
        elif action == delete_action:
            self.delete_subject(row, subject)

    def edit_subject(self, row: int, old_subject: str):
        """Prompt for new subject name, update DB and local JSON state, and refresh UI."""
        new_subject, ok = QInputDialog.getText(self, "Edit Subject", "New subject name:", text=old_subject)
        if not ok:
            return
        new_subject = new_subject.strip()
        if not new_subject:
            QMessageBox.warning(self, "Warning", "Enter a valid subject name")
            return
        if new_subject == old_subject:
            return

        msg = cp_table.update_cp(old_subject, new_subject)
        if not msg.get("status"):
            QMessageBox.warning(self, "Warning", msg.get("message", "Failed to rename subject"))
            return

        QMessageBox.information(self, "Success", msg.get("message", "Subject renamed"))
        # refresh visible list
        self.refresh_subjects()
        self.update_dashboard()

    def delete_subject(self, row: int, subject: str):
        """Confirm deletion, remove from DB and JSON stores, then refresh UI."""
        reply = QMessageBox.question(self, "Delete Subject",
                                     f"Delete '{subject}'? This will remove its check marks.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        msg = cp_table.delete_cp(subject)
        if not msg.get("status"):
            QMessageBox.warning(self, "Warning", msg.get("message", "Failed to delete subject"))
            return
        QMessageBox.information(self, "Deleted", msg.get("message", "Subject deleted"))
        self.refresh_subjects()

    def refresh_subjects(self):
        """Reload subjects from DB into the first column and update self.counter."""
        try:
            subjects = cp_table.get_cerebral_pursuits() or []
        except Exception:
            subjects = []

        # clear column 0
        for r in range(self.habit_tracker.rowCount()):
            self.habit_tracker.setItem(r, 0, QTableWidgetItem(""))

        for idx, subj in enumerate(subjects):
            if subj and subj.strip():
                self.habit_tracker.setItem(idx, 0, QTableWidgetItem(subj.strip()))
        self.counter = len(subjects)

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

        if state != 2:
            return  # Only proceed if checked

        key = cell_text
        logging.debug(f"Subject key: {key}")
        cp = key
#------------------------------------------------------------------Save data----------------------------------------------------
        day = column_header
        state = {f'{row},{col}': True}
        msg = cp_table.save_cp(row, state, cp, day)
        logging.debug(msg)
        QMessageBox.information(self, "Message", msg["message"])
        letters = string.ascii_letters
        random_string = "".join(random.choice(letters) for _ in range(26))
        trigger_file_2 = Path(__file__).parent / "update_db_ui.txt"
        with open(trigger_file_2, "w") as f:
            f.write(random_string)        
                        
    def init_wrapper(self):
        """Initailze necessary methods and check if app needs reset"""
            
        today = str(datetime.datetime.now().date())
        today = datetime.datetime.strptime(today, "%Y-%m-%d")
        # today = self.end_date
        try:
            if today >= self.end_date:
                self.load_last_entered_habits()
                self.enable_check_box_change = True
                logging.debug("app reset")
                msg = cp_table.clear_cp_data()
                if msg["status"]:
                    logging.debug(msg["message"])
                logging.debug("App has been reset")
            else:
                self.load_last_entered_habits()
                self.load_checkbox_states()
                logging.debug("App not reset")
        except TypeError:
            logging.debug("reset date not available yet")
            self.load_last_entered_habits()
            self.enable_check_box_change = True
        self.load_themes()
        self.load_thm_pref()

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
        """Shows the check marks for each cp per week"""

        count = cp_table.get_cp_with_check_marks()
        self.plot_habit_barchart(count)

    def exit_app(self):
        sys.exit()
# ======================================================================Run Application===========================================
if __name__ == "__main__":
    app = QApplication([])
    window = CPTracker()
    window.show()
    app.exec()