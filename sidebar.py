from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,QTableWidget, QTableWidgetItem,QLineEdit,QMessageBox, QCheckBox,QSizePolicy
from PySide6.QtCore import Qt, QDate
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict
import sys
import json
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SidebarMenu(QWidget):
    def __init__(self):
        super().__init__()

        
        # Main Layout
        self.main_layout = QHBoxLayout(self)
        
        # Sidebar Widget
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)  # Default width
        self.sidebar.setStyleSheet("background-color: #333;")

        # Sidebar Layout (Vertical)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Toggle Button (Collapses Sidebar)
        self.toggle_btn = QPushButton("☰")  # Unicode for menu icon
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        # Sidebar Buttons
        progress_btn = QPushButton("progress")
        progress_btn.clicked.connect(self.show_progress)
        self.btn_settings = QPushButton("Settings")
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self._exit)

        # Style Buttons
        for btn in [progress_btn, self.btn_settings, self.exit_btn]:
            btn.setStyleSheet("color: white; background: #444; border: none; padding: 10px;")
            self.sidebar_layout.addWidget(btn)

        # Main Content Area
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = ["Habits","Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sundday"]
        self.counter = -1

        self.habit_tracker = QTableWidget()
        self.habit_tracker.setRowCount(10)
        self.habit_tracker.setColumnCount(8)
        self.habit_tracker.setHorizontalHeaderLabels(header)

        for col in range(1, 8):
            for row in range(col + 9):
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
        self.input.setPlaceholderText("Enter habit here...")
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        h_layout.addWidget(self.input)

        self.enter_btn = QPushButton("Enter")
        self.enter_btn.clicked.connect(self.add_habit)
        h_layout.addWidget(self.enter_btn)

        #cell edit button
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_cell)
        h_layout.addWidget(edit_btn)

        layout.addLayout(h_layout)

        # Add Widgets to Main Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("PySide6 Sidebar Menu")
        self.resize(600, 400)

        self.load_last_entered_habits()
        

    def load_last_entered_habits(self):
        file = Path(__file__).parent / "last saved.txt"
        with open(file, 'r') as f:
            habits = f.readlines()
        logging.debug(habits)
        for habit in habits:
            if habit != "\n":
                self.counter += 1
                logging.debug(habit)
                item = QTableWidgetItem(habit)
                self.habit_tracker.setItem(self.counter, 0, item)
                logging.debug(f"done! added {habit}")
    
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
        header_item = self.habit_tracker.horizontalHeaderItem(col)
        if header_item:
            column_header = header_item.text()
            logging.debug(f"Column header at column {col}: {column_header}")

        item = self.habit_tracker.item(row, 0)
        if item is not None:
            cell_text = item.text()
            logging.debug(cell_text)
            dt = QDate(date.today()).toString('dddd, MMMM d, yyyy')
            logging.debug(dt)
        logging.debug(f"Checkbox at ({row}, {col}) changed to {'checked' if state == 2 else 'unchecked'}")
        
        if state == 2:
            state = "checked"
            file = Path(__file__).parent / "habit_tracker.json"
            
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

            if key not in data:
                data[key] = []
                
            data[key].append({
                    "row": row,
                    "col": col,
                    "state": state,
                    "date": dt
                })
            # Save back to file
            with open(file, 'w') as f:
                json.dump(data, f, indent=4)
        
        logging.debug("done") 

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

    def show_progress(self):
        file = Path(__file__).parent / "habit_tracker.json"

        data = self._load_habit_data(file)
        count = self.count_checkmarks(data)
        self.plot_habit_barchart(count)

    def _exit(self):
        self.save_last_entered_habits()
        sys.exit()

# Run Application
if __name__ == "__main__":
    app = QApplication([])
    window = SidebarMenu()
    window.show()
    app.exec()
