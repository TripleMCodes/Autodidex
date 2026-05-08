#********************************************************************************************************************
#===========================================================Modules==================================================
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)
from calander import Calendar_Heatmap
from game_ui import MainWindow, SpinningLabel, AutodidexBank, UserIfo
from habit_tracker import CPTracker
from note_worthy import NoteWorthy
from pomodoro_gui import PomodoroGUI
import csv
# from space_invader_widget import SpaceInvaderWidget
from autodidex_cache import DictionaryCache
from themes_db import Themes

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable(logging.DEBUG)
#====================================================================================================================
#========================================================enums=======================================================
class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
#====================================================================================================================
#======================================================enum-encoder==================================================
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
#====================================================================================================================
#========================================================Autodidex-class=============================================
class Autodidex (QWidget):
    
    def __init__(self):
        super().__init__()
#====================================================================================================================
#========================================================window-title================================================
        self.setWindowTitle("Autodidex")
        self.layout = QVBoxLayout()
#====================================================================================================================
#========================================================window-icon=================================================
        win_icon = Path(__file__).parent / "Icons/icons8-brain-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))
#====================================================================================================================
#=========================================================Tabwidget==================================================
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)  #This makes them vertical on the left
        self.tab_widget.tabBar().setIconSize(QSize(36, 36))
        self.thm_mode: Optional[str] = None
#====================================================================================================================
#=================================================tab-container======================================================
        tab1_widget = QWidget()
#====================================================================================================================
#=======================================================create settings tab==========================================
        self.settings_tab = QWidget()
#====================================================================================================================
#=======================================================creating layout for the tab==================================
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
#====================================================================================================================
#==========================================================header-layout=============================================
        h_layout = QHBoxLayout()
        settings_layout.addLayout(h_layout)
#====================================================================================================================
#=========================================================setting content layout=====================================
        s_layout = QHBoxLayout()
        settings_layout.addLayout(s_layout)
#====================================================================================================================
#==============================================================button icons==========================================
        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.n_mode = Path(__file__).parent / "Icons/icons8-day-and-night-50.png"
#===================================================================================================================
        self.light_mode: Optional[str] = None
        self.dark_mode: Optional[str] = None
        self.neutral_mode: Optional[str] = None
        self.cache = DictionaryCache() #lazy loading
        self.themes = Themes() #lazy loading
        self.mode = self.cache.get("theme") or self.themes.get_chosen_theme()
#====================================================================================================================
#===========================================================layout content===========================================
        settings_label = SpinningLabel("⚙️Settings")
        settings_label.setObjectName("onloadlabel")
        self.thm_btn = QPushButton("")
        self.thm_btn.setIcon(QIcon(str(self.d_mode)))
        self.about = QPushButton("About Autodidex")
        self.about.setIcon(QIcon(str(win_icon)))
        settings_list = [self.thm_btn, self.about]
#====================================================================================================================
#============================================================adding slots============================================
        self.thm_btn.clicked.connect(self.thm_toggle)
        self.about.clicked.connect(self.about_autodidex)
#====================================================================================================================
#==========================================================adding content to layout==================================
        h_layout.addWidget(settings_label, alignment=Qt.AlignmentFlag.AlignCenter)
        for item in settings_list:
            item.setIconSize(QSize(30, 30))
            s_layout.addWidget(item)
#====================================================================================================================
#===================================================adding layout to the tab=========================================
        self.settings_tab.setLayout(settings_layout)
#====================================================================================================================
#=============================================================tabs===================================================
        self.noteworthy = NoteWorthy()
        self.cirillo = PomodoroGUI()
        
        self.cpt_tracker = CPTracker()
        self.cal_ht = Calendar_Heatmap()
        self.dash_board = MainWindow()
        # self.space_invader = SpaceInvaderWidget()
        
#====================================================================================================================
#==============================================================tab icons=============================================
        dashboard = Path(__file__).parent / "Icons/icons8-dashboard-64.png"
        habit_tracker = Path(__file__).parent / "Icons/icons8-to-do-list-64.png"
        pomodoro = Path(__file__).parent / "Icons/icons8-pomodoro-50.png"
        noteworthy = Path(__file__).parent / "Icons/icons8-notebook-64.png"
        calendar = Path(__file__).parent / "Icons/icons8-calendar-64.png"
        settings = Path(__file__).parent / "Icons/icons8-settings-64.png"
        # space_invader_icon = Path(__file__).parent / "spaceinvader" / "img"/ "ufo.png"
#====================================================================================================================
#=================================================addings tabs to layout=============================================
        self.tab_widget.addTab(self.dash_board, QIcon(str(dashboard)), "")
        self.tab_widget.setTabToolTip(0, "Dashboard")

        self.tab_widget.addTab(self.cpt_tracker, QIcon(str(habit_tracker)), "")
        self.tab_widget.setTabToolTip(1, "Habit Tracker")

        self.tab_widget.addTab(self.cirillo, QIcon(str(pomodoro)), "")
        self.tab_widget.setTabToolTip(2, "Pomodoro")

        self.tab_widget.addTab(self.noteworthy, QIcon(str(noteworthy)), "")
        self.tab_widget.setTabToolTip(3, "NoteWorthy")

        self.tab_widget.addTab(self.cal_ht, QIcon(str(calendar)), "")
        self.tab_widget.setTabToolTip(4, "Calendar")

        self.tab_widget.addTab(self.settings_tab, QIcon(str(settings)), "")
        self.tab_widget.setTabToolTip(5, "Settings")

        # self.tab_widget.addTab(self.space_invader, QIcon(str(space_invader_icon)), "")
        # self.tab_widget.setTabToolTip(6, "Space Invader")
#====================================================================================================================
#=========================================================set layout=================================================
        self.exit_button = QPushButton("")
        self.exit_button.setIcon(QIcon(str(Path(__file__).parent / "Icons/icons8-power-button-50.png")))
        self.exit_button.setIconSize(QSize(50, 50))
        self.exit_button.setToolTip("Exit Autodidex")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #D5C8FF,
                stop:1 #BBA9F2
            );
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0D4FF;
                border: 1px solid #967BE3;
            }
            QPushButton:pressed {
                background-color: #BFA9FF;
                border: 1px solid #6F54D8;
            }
        """)

        self.exit_button.clicked.connect(self.exit_app) 
        self.layout.addWidget(self.tab_widget)
        self.layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)    
#====================================================================================================================
#========================================================about autodidex=============================================
        self.about_text = (
            "📘 **Autodidex** — A Toolkit for the Self-Taught Mind\n\n"
            "Crafted with passion and purpose by Connor Connorson, Autodidex is an all-in-one productivity suite designed "
            "for autodidacts, creatives, and knowledge-hunters who believe learning never stops.\n\n"
            
            "📌 **What's Inside:**\n"
            "• 🧠 Habit Tracker — Build better routines\n"
            "• ⏳ Pomodoro Timer — Stay sharp, stay focused\n"
            "• 📝 NoteWorthy — Take notes that matter\n"
            "• 📆 Calendar Heatmap — Visualize your grind\n"
            "• 🎮 Dashboard + Minigames — Because learning should be fun\n\n"
            
            "💡 Whether you're mastering code, philosophy, languages, or just life itself, Autodidex is your digital companion "
            "on the quest for personal mastery.\n\n"
            
            "🛠️ Made with PySide6 and relentless curiosity.\n\n"
            "📬 Contact: khona6047@gmail.com\n"
            "🚀 Keep learning. Keep creating. Stay worthy."
        )
#===================================================================================================================================
#===========================================================load special values and methods=========================================
        self.session_file = Path(__file__).parent / "cirillo files/sessions.csv"
        self.watcher = QFileSystemWatcher()
        if self.session_file.exists():
            self.watcher.addPath(str(self.session_file))
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.intial_sessions_val = self.load_last_saved_session()
        self.init_wrapper()
#====================================================================================================================
#=========================================================class methods==============================================
    def exit_app(self):
        self.cirillo.log_sessions()
        self.close()
        self.destroy()

    def load_thm_pref(self):
        """load saved theme preferrence"""
        self.mode = self.cache.get('theme') or self.themes.get_chosen_theme()

    
    def load_themes(self):
        """loads the themes, and sets them to their data fields"""
        
        if self.cache.get("light"):
            self.light_mode = self.cache.get("light")
        self.light_mode = self.themes.get_theme_mode("light")
        self.cache.set("light", self.light_mode)

        if self.cache.get("dark"):
            self.dark_mode = self.cache.get("dark")
        self.dark_mode = self.themes.get_theme_mode("dark")
        self.cache.set("dark", self.dark_mode)

        if self.cache.get("neutral"):
            self.neutral_mode = self.cache.get("neutral")
        self.neutral_mode = self.themes.get_theme_mode("neutral")
        self.cache.set("neutral", self.neutral_mode)

    def thm_toggle(self):
        if self.mode == "light":
            self.setStyleSheet(self.dark_mode)
            self.thm_btn.setText("")
            self.thm_btn.setIcon(QIcon(str(self.d_mode)))
            self.cirillo.toggle_theme()
            self.cpt_tracker.theme()
            self.dash_board.toggle_theme()
            self.cal_ht.toggle_theme()
            self.noteworthy.theme()
            self.mode = "dark"
            self.cache.set("theme", "dark")
        elif self.mode == "dark":
            self.setStyleSheet(self.neutral_mode)
            self.thm_btn.setText("")
            self.thm_btn.setIcon(QIcon(str(self.n_mode)))
            self.cirillo.toggle_theme()
            self.cpt_tracker.theme()
            self.dash_board.toggle_theme()
            self.cal_ht.toggle_theme()
            self.noteworthy.theme()
            self.mode = "neutral"
            self.cache.set("theme", "neutral")
        elif self.mode == "neutral":
            self.setStyleSheet(self.light_mode)
            self.thm_btn.setText("")
            self.thm_btn.setIcon(QIcon(str(self.l_mode)))
            self.cirillo.toggle_theme()
            self.cpt_tracker.theme()
            self.dash_board.toggle_theme()
            self.cal_ht.toggle_theme()
            self.noteworthy.theme()
            self.mode = "light"
            self.cache.set("theme", "light")
        
    def about_autodidex(self):
        QMessageBox.information(
            self,
            "About Autodidex",
            self.about_text
        )

    def on_file_changed(self):
        #This function is called twice when file session is called
        #Since I want to add 6 lumens with each new session
        #I will add lumens with each call of this function
        self.bank =  AutodidexBank(UserIfo)
        new_sessions_val = self.load_last_saved_session() 
        if new_sessions_val > self.intial_sessions_val:
            self.bank.wallet = 3
            self.dash_board.update()
        
    def load_last_saved_session(self):
        """Loads the number of last saved sessions in a day"""
        with open(self.session_file, "r") as f:
            sessions_data = list(csv.DictReader(f))
            last_row = sessions_data[-1]
            return int(last_row["sessions"])
    
    def set_init_thm(self):
        """Set initial theme upon opening app"""

        if self.mode == "light":
            self.thm_btn.setIcon(QIcon(str(self.l_mode)))
            self.setStyleSheet(self.light_mode)
        elif self.mode == "dark":
            self.thm_btn.setIcon(QIcon(str(self.d_mode)))
            self.setStyleSheet(self.dark_mode)
        elif self.mode == "neutral":
            self.thm_btn.setIcon(QIcon(str(self.n_mode)))
            self.setStyleSheet(self.neutral_mode)
        print(f"The theme is {self.mode}")

    def init_wrapper(self):
        self.load_thm_pref()
        self.load_themes()
        self.set_init_thm()
        self.cpt_tracker.init_wrapper() 
        self.dash_board.init_wrapper()
        self.cal_ht.init_wrapper()
        self.noteworthy.init_wrapper()
        self.cirillo.init()
#--------------------------------------------------------------------------------------------------------------------
#================================================================run app=============================================
if __name__ == "__main__":
    app = QApplication([])
    window = Autodidex ()
    window.show()
    app.exec()
