#********************************************************************************************************************
#===========================================================Modules==================================================
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)

from calander import Calendar_Heatmap
from game_ui import MainWindow, SpinningLabel
from habit_tracker import CPTracker
from note_worthy import NoteWorthy
from pomodoro_gui import PomodoroGUI
from space_invader_widget import SpaceInvaderWidget

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
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
#========================================================tab-container===============================================
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
        self.dark = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.light = Path(__file__).parent / "Icons/icons8-light-64.png"
#====================================================================================================================
#===========================================================layout content===========================================
        settings_label = SpinningLabel("⚙️Settings")
        settings_label.setObjectName("onloadlabel")
        self.thm_btn = QPushButton("Dark mode")
        self.thm_btn.setIcon(QIcon(str(self.dark)))
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
        self.space_invader = SpaceInvaderWidget()
        
#====================================================================================================================
#==============================================================tab icons=============================================
        dashboard = Path(__file__).parent / "Icons/icons8-dashboard-64.png"
        habit_tracker = Path(__file__).parent / "Icons/icons8-to-do-list-64.png"
        pomodoro = Path(__file__).parent / "Icons/icons8-pomodoro-50.png"
        noteworthy = Path(__file__).parent / "Icons/icons8-notebook-64.png"
        calendar = Path(__file__).parent / "Icons/icons8-calendar-64.png"
        settings = Path(__file__).parent / "Icons/icons8-settings-64.png"
        space_invader_icon = Path(__file__).parent / "spaceinvader" / "img"/ "ufo.png"
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

        self.tab_widget.addTab(self.space_invader, QIcon(str(space_invader_icon)), "")
        self.tab_widget.setTabToolTip(6, "Space Invader")
#====================================================================================================================
#=========================================================set layout=================================================
        self.exit_button = QPushButton("")
        self.exit_button.setIcon(QIcon(str(Path(__file__).parent / "Icons/icons8-exit-sign-64.png")))
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
#====================================================================================================================
#===========================================================load saved theme=========================================
        self.init_wrapper()
#====================================================================================================================
#=========================================================class methods==============================================
    def exit_app(self):
        self.cirillo.log_sessions()
        self.cpt_tracker.save_last_entered_habits()
        self.cpt_tracker.save_checkbox_states()
        self.close()
        self.destroy()

    def save_preference(self):
        """Save theme mode chosen"""
        config_file = Path(__file__).parent / "v tab files/dashboard_config.json"

        data = {
            "mode": self.thm_mode  # This is an Enum 
        }

        with open(config_file, "w") as f:
            json.dump(data, f, cls=EnumEncoder)

        logging.debug(f"saving preferred theme as {self.thm_mode}")
        return
    
    def load_saved_pref(self):
        """Loads the saved theme preference and applies the enum properly"""
        config_file = Path(__file__).parent / "v tab files/dashboard_config.json"

        try:
            with open(config_file, "r") as f:
                data = json.load(f)

#---------------------------------------------------Convert the string back to ThemeMode Enum------------------------
            self.thm_mode = Theme(data.get("mode", Theme.DARK.value))
            logging.debug(f'save theme {self.thm_mode}')

        except (json.decoder.JSONDecodeError, FileNotFoundError, ValueError, KeyError):
#----------------------------------------------If file is corrupt or missing, fallback to default--------------------
            self.thm_mode = Theme.DARK
            data = {"mode": self.thm_mode.value}
            
            with open(config_file, "w") as f:
                json.dump(data, f, cls=EnumEncoder)

        return
    
    def load_thms(self):
        """Loads the styling data for the app"""
        
        light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"
        with open(light_mode_file, "r") as f:
            light_mode = f.read()
        
        dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"
        with open(dark_mode_file, "r") as f:
            dark_mode = f.read()

        return light_mode, dark_mode

    def thm_toggle(self):
        light_mode, dark_mode = self.load_thms()

        if self.thm_mode == Theme.DARK:
            self.setStyleSheet(light_mode)
            self.thm_btn.setText("Dark mode")
            self.thm_btn.setIcon(QIcon(str(self.dark)))
            self.thm_mode = Theme.LIGHT
            self.cirillo.toggle_theme()
            self.cpt_tracker.theme()
            self.dash_board.toggle_theme()
            self.cal_ht.toggle_theme()
            self.noteworthy.apply_theme()
        else:
            self.setStyleSheet(dark_mode)
            self.thm_btn.setText("Light mode")
            self.thm_btn.setIcon(QIcon(str(self.light)))
            self.thm_mode = Theme.DARK
            self.cirillo.toggle_theme()
            self.cpt_tracker.theme()
            self.dash_board.toggle_theme()
            self.cal_ht.toggle_theme()
            self.noteworthy.apply_theme()
            
        self.save_preference()
        return
    
    def about_autodidex(self):
        QMessageBox.information(
            self,
            "About Autodidex",
            self.about_text
        )

    def init_wrapper(self):
        self.load_saved_pref()
        light_mode, dark_mode = self.load_thms()
        if self.thm_mode == Theme.DARK:
            self.setStyleSheet(dark_mode)
            logging.debug("New user present")
        else:
            self.setStyleSheet(light_mode)
        self.cpt_tracker.init_wrapper()
        self.dash_board.init_wrapper()
        self.cal_ht.init_wrapper()
        self.noteworthy.init_wrapper()
        self.cirillo.init()
        logging.debug("Saved user logged in")

#--------------------------------------------------------------------------------------------------------------------
#================================================================run app=============================================
if __name__ == "__main__":
    app = QApplication([])
    window = Autodidex ()
    window.show()
    app.exec()
