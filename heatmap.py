#=========================================================Imports==================================
#**************************************************************************************************
import csv
import logging
import random
import sys
from datetime import date, datetime, timedelta
from PySide6.QtCore import QSize, Qt, QTime, QTimer
from PySide6.QtCore import QFileSystemWatcher
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QScrollArea,
                               QVBoxLayout, QWidget)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
#==================================================================================================
#---------------------------------------------Color Gradient Function -----------------------------
def get_color(count):
    if count == 0:
        return "#ebedf0"  
    elif count == 1:
        return "#c6e48b"  
    elif count == 2:
        return "#7bc96f"  
    elif count == 3:
        return "#239a3b"  
    elif count > 3 and count < 6:
        return "#1f7c32"  
    elif count >= 6 and count < 9:
        return "#134D1F"  
    elif count >= 9:
        return "#03300C"  
    elif count >= 15:
        return "#011405"  
#=================================================================================================
#------------------------------------------------Heatmap Widget------------------------------------
class HeatmapWidget(QWidget):
    def __init__(self, study_data, start_date, end_date):
        super().__init__()

        self.study_data = study_data
        self.start_date = start_date
        self.end_date = end_date

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setStyleSheet("""
                    QWidget {
                        background-color:#ba9dcab0;
                    }
                """)
        self.grid = QGridLayout(container)
        self.grid.setSpacing(4)

        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.create_heatmap()

    def create_heatmap(self):
        current_date = self.start_date
        column = 0

#================================Shift start day to Sunday (to align like GitHub)==================
        while current_date.weekday() != 6:
            current_date -= timedelta(days=1)

        while current_date <= self.end_date:
            for row in range(7):  # Sunday to Saturday
                day = current_date + timedelta(days=row)
                if day > self.end_date:
                    break

                count = self.study_data.get(day, 0)
                color = get_color(count)

                cell = QLabel()
                cell.setFixedSize(20, 20)
                cell.setStyleSheet(
                    f"background-color: {color}; border-radius: 3px; color:black;"
                )
                cell.setToolTip(f"{day.isoformat()}\nSessions: {count}")
                self.grid.addWidget(cell, row, column)

            current_date += timedelta(days=7)
            column += 1
#==================================================================================================
#------------------------------------------------- Main Window ------------------------------------

class StreakTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub-Style Streak Tracker")
        self.resize(800, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.study_data = {}
        self.heatmap = None

        self.session_file = Path(__file__).parent / "cirillo files/sessions.csv"

        # Watch the CSV file for changes
        self.watcher = QFileSystemWatcher()
        if self.session_file.exists():
            self.watcher.addPath(str(self.session_file))
        self.watcher.fileChanged.connect(self.on_file_changed)

        # Initial data load
        self.read_sessions()

    def on_file_changed(self, path):
        """
        Gets called automatically when the file is changed.
        """
        logging.debug(f"Detected change in: {path}")

        # QFileSystemWatcher can drop the file if it gets overwritten
        if not self.watcher.files():
            self.watcher.addPath(path)

        self.read_sessions()

    def read_sessions(self):
        file = self.session_file
        start_date = end_date = datetime.today().date()
        new_data = {}

        try:
            with open(file, mode="r", newline="", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                if len(reader) >= 2:
                    try:
                        start_date = datetime.strptime(reader[1][1], '%d %B %Y').date()
                        end_date = datetime.strptime(reader[-1][1], '%d %B %Y').date()
                    except Exception as e:
                        logging.error(f"Date parsing error: {e}")
        except Exception as e:
            logging.error(f"File read error: {e}")
            return

        try:
            with open(file, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        dt = datetime.strptime(row["date"], '%d %B %Y').date()
                        sessions = int(row["sessions"])
                        new_data[dt] = sessions
                    except:
                        continue
        except:
            pass

        if new_data != self.study_data:
            self.study_data = new_data
            self.update_heatmap(start_date, end_date)

    def update_heatmap(self, start_date, end_date):
        if self.heatmap:
            self.layout.removeWidget(self.heatmap)
            self.heatmap.setParent(None)

        self.heatmap = HeatmapWidget(self.study_data, start_date, end_date)
        self.layout.addWidget(self.heatmap)

# # ---------- Run the App ----------
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     tracker = StreakTracker()
#     tracker.show()
#     sys.exit(app.exec())