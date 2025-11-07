#===============================================Imports============================================
#**************************************************************************************************
import csv
import datetime
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional 
from PySide6.QtCore import QDate, QSize, Qt, QFileSystemWatcher
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QCalendarWidget, QLabel,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

from heatmap import HeatmapWidget, StreakTracker

logging.basicConfig(level=logging.DEBUG) 
logging.disable(logging.DEBUG)
#==================================================================================================
#**************************************************************************************************
#================================================Calendar and Heat Map UI==========================
class Calendar_Heatmap(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex Streak Calendar")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        starting_date = QDate(date.today())

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selected)
        self.calendar.setSelectedDate(starting_date)  
        layout.addWidget(self.calendar)

#-----------------------------------------------------load first date------------------------------
        self.first_date = self.load_first_date()

#-----------------------------------------------------theme button---------------------------------
        self.light_mode: Optional[str] = None
        self.dark_mode: Optional[str] = None
        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.thm_pref = Path(__file__).parent / "v tab files/dashboard_config.json"
        self.theme_toggle_btn = QPushButton("")
        self.theme_toggle_btn.setIcon(QIcon(str(self.l_mode)))
        self.theme_toggle_btn.setIconSize(QSize(30, 30))
        self.thm_mode: Optional[str] = None
        self.setStyleSheet(self.dark_mode)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel(f"Shows streak from {self.first_date} to {date.today()}")
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        font-weight: 600;
                        color: #f5f5f5;
                        background-color: #19191b;
                        padding: 10px 15px;
                        border: 1px solid #C5D2E0;
                        border-radius: 8px;
                        margin: 10px 0;
                    }
                """)
        layout.addWidget(self.label)

        self.heatmap = StreakTracker()
        layout.addWidget(self.heatmap)

        # self.load_themes()
        # self.load_thm_pref()
        # self.init_wrapper()

    def load_themes(self):
        """Loads the themes for the apps"""
#-----------------------------------------------------------light mode----------------------------- 
        light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"
        with open(light_mode_file, "r") as f:
            self.light_mode = f.read()

#-------------------------------------------------------dark mode----------------------------------
        dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"
        with open(dark_mode_file, "r") as f:
            self.dark_mode = f.read()

        return
    
    def load_thm_pref(self):
        try:
            with open(self.thm_pref, "r") as f:
                data = json.load(f)
                self.thm_mode = data["mode"]
        except (json.decoder.JSONDecodeError, FileNotFoundError, ValueError, KeyError):
#------------------------------------------------------set to default------------------------------
            self.thm_mode = "dark"
        
        if self.thm_mode == "dark":
            self.setStyleSheet(self.dark_mode)
        elif self.thm_mode == "light":
            self.setStyleSheet(self.light_mode)
        return

    def toggle_theme(self):
        """toggle between dark and light mode"""
        if self.thm_mode == "light":
            self.setStyleSheet(self.dark_mode)
            self.theme_toggle_btn.setIcon(QIcon(str(self.l_mode)))
            self.thm_mode = "dark"
        else:
            self.setStyleSheet(self.light_mode)
            self.theme_toggle_btn.setIcon(QIcon(str(self.d_mode)))
            self.thm_mode = "light"
                                                            
    def date_selected(self, qdate: QDate):
        """Show the number of sessions on a particular day"""
        some_date = qdate.toPython()
#--------------------------------------Convert to datetime.datetime (with time 00:00:00)---------------------
        logging.debug(some_date)
        # print(some_date)
        try:  
            self.label.setText(f"""Shows streak from {self.first_date}
                                to {date.today()}a\nsessios on {qdate.toString('dddd, MMMM d, yyyy')}:
                                  {self.heatmap.study_data[some_date]} """)
        except KeyError:
            QMessageBox.information(self, "Streak not found", f"There is no streak on  {qdate.toString('dddd, MMMM d, yyyy')} ")

    def load_first_date(self):
        """Loads the date of the first day the sessions data was saved, with error handling."""
        sessions_start_date_file = Path(__file__).parent / "cirillo files/sessions.csv"

        try:
            with open(sessions_start_date_file, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header
                first_row = next(reader, None)  # Get first row data, safely

                if first_row and len(first_row) > 1:
                    first_date = first_row[1]
                    logging.debug(f"First date is {first_date}")
                    return first_date
                else:
                    logging.warning("No data found in sessions.csv after header.")
                    return None

        except FileNotFoundError:
            logging.error(f"File not found: {sessions_start_date_file}")
            return None

        except UnicodeDecodeError:
            logging.error("Encoding issue encountered. Make sure the file is UTF-8 encoded.")
            return None

        except Exception as e:
            logging.error(f"Unexpected error while loading first date: {e}")
            return None
    
    
    
    def init_wrapper(self):
        self.load_themes()
        self.load_thm_pref()
#==================================================================================================
#===================================================Run============================================
# if __name__ == "__main__":
#     app = QApplication([])
#     demo = Calendar_Heatmap()
#     demo.show()
#     app.exec()