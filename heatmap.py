#=========================================================Imports==================================
#**************************************************************************************************
import csv
import logging
import random
import sys
from datetime import date, datetime, timedelta
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
        return "#ebedf0"  # light gray
    elif count == 1:
        return "#c6e48b"  # light green
    elif count == 2:
        return "#7bc96f"  # medium green
    elif count == 3:
        return "#239a3b"  # dark green
    else:
        return "#196127"  # deepest green
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

        layout = QVBoxLayout(self)
        self.study_data = {}

        file = Path(__file__).parent / "cirillo files/sessions.csv"

        try:
            with open(file, mode="r", newline="", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                
                if len(reader) < 2:
                    logging.warning("CSV does not contain enough data (missing rows after header).")
                    start_date = end_date = datetime.today().date()
                else:
                    try:
                        start_date = datetime.strptime(reader[1][1], '%d %B %Y').date()
                        end_date = datetime.strptime(reader[-1][1], '%d %B %Y').date()
                        logging.debug(f"Start date: {start_date}")
                        logging.debug(f"End date: {end_date}")
                    except (IndexError, ValueError) as e:
                        logging.error(f"Error parsing dates from CSV: {e}")
                        start_date = end_date = datetime.today().date()

        except FileNotFoundError:
            logging.error(f"File not found: {file}")
            start_date = end_date = datetime.today().date()
        except Exception as e:
            logging.error(f"Unexpected error loading session file: {e}")
            start_date = end_date = datetime.today().date()

        # Now load the session data safely
        try:
            with open(file, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        dt = datetime.strptime(row["date"], '%d %B %Y').date()
                        sessions = int(row["sessions"])
                        self.study_data[dt] = sessions
                        logging.debug(f"Loaded: {dt} -> {sessions}")
                    except (ValueError, KeyError) as e:
                        logging.warning(f"Skipping invalid row: {row} | Error: {e}")

        except FileNotFoundError:
            logging.error("Session file not found during data load.")
        except Exception as e:
            logging.error(f"Unexpected error while reading session data: {e}")

        # Proceed even if data is empty or partial
        heatmap = HeatmapWidget(self.study_data, start_date, end_date)
        layout.addWidget(heatmap)

# # ---------- Run the App ----------
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     tracker = StreakTracker()
#     tracker.show()
#     sys.exit(app.exec())