#==========================================================================Imports==============================================================
#***********************************************************************************************************************************************
import datetime
import json
import logging
import math
import os
import pickle
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import (QBrush, QColor, QFont, QIcon, QLinearGradient,
                           QPainter, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                               QLabel, QLineEdit, QListWidget, QMainWindow,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

#=====================================================================logs enable/disable=======================================================
logging.basicConfig(level=logging.DEBUG) 
logging.disable(logging.DEBUG)
#===============================================================================================================================================
#***********************************************************************************************************************************************
#========================================================================User INfo Class========================================================
class UserIfo:

    def __init__(self):
        self._name = self.load_username()
        # self._title = ""
        self._overAll_level = 0
        self.subjects = {}
#===============================================================================================================================================        
#==================================================================================Getters======================================================
    @property
    def name(self):
        return self._name
    
    
    @property
    def level(self):
        return self._overAll_level
#===============================================================================================================================================
#===============================================================================Setters=========================================================
    @name.setter
    def name(self, name):
        if name and name[0].isupper():
            self._name = name
        else:
            raise ValueError("Please capitalize the first letter of your name")
        
    @level.setter
    def level(self, total):
        pass
#===============================================================================================================================================
#===========================================================================Class Methods=======================================================
    def initialize_subjects(self):
        """Load subjects saved in Habit Tracker"""
        file = Path(__file__).parent / "habit tracker files/last saved.txt"
        subjects_level = Path(__file__).parent / "dashboard files/subjects_level.json"

        try:
            with open(file, "r") as f:
                subjects = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            logging.error("Subjects text file does not exist")
            return

        self.subjects = {}  # Reset or initialize class-level dictionary

#-----------------------------------------------------------------If the JSON is empty, initialize it fresh-------------------------------------
        if os.path.getsize(subjects_level) == 0:
            for subject in subjects:
                self.subjects[subject] = {"level": 0, "xp": 0}
            with open(subjects_level, "w") as f:
                json.dump(self.subjects, f, indent=4)
            logging.debug("Initialized subjects from scratch.")
            return self.subjects

#---------------------------------------------------------------------Otherwise, load the existing JSON data------------------------------------
        with open(subjects_level, "r") as f:
            subjects_level_data = json.load(f)

#---------------------------------------------------------------------Update existing dict with any new subjects--------------------------------
        for subject in subjects:
            if subject not in subjects_level_data:
                logging.debug(f"Adding new subject: {subject}")
                subjects_level_data[subject] = {"level": 0, "xp": 0}

#----------------------------------------------------------------------Save updated data back---------------------------------------------------
        with open(subjects_level, "w") as f:
            json.dump(subjects_level_data, f, indent=4)

        self.subjects = subjects_level_data  # Update internal state
        return self.subjects         
    
    def load_update_state(self):
        """loads the variable responsible for updating bank and subjects information"""
        file = Path(__file__).parent / "dashboard files/game_update_state.json"
         
        with open(file, 'r') as f:
            state = f.read()
            state = bool(int(state))
            self.update_state = state
            logging.debug(f"The state is {state}")
            return self.update_state
    
    def save_update_state(self, state):
        file = Path(__file__).parent / "dashboard files/game_update_state.json"
        state_to_save = {}

        open(file).close()
        with open(file, 'w')  as f:
            state_to_save["state"] = state
            json.dump(state_to_save, f)

    def overall_level_up(self):
        """Sum all subject XP points, each new gain of 500 XP points gives 1 overall level up."""

        file = Path(__file__).parent / "dashboard files/overall_level.json"
        bank_detail_file = Path(__file__).parent / "dashboard files/bank_details.json"

        with open(bank_detail_file, "r") as f:
            bank_details = json.load(f)
        xp_amount = bank_details["total_xp"]
        new_overall_level = xp_amount // 500

        logging.debug(f"New level is {new_overall_level}")

        with open(file, "r") as f:
            level = json.load(f)
        
        if new_overall_level > self._overAll_level:

            level["overall_level"] = new_overall_level
            logging.debug(f"new over lever is {level["overall_level"]}")
            open(file).close()
            with open(file, "w") as f:
                json.dump(level, f, indent=4)
            self._overAll_level = new_overall_level
        else:
            logging.debug(f"No new lever achieved")

    def subjects_badges_state(self):
        """Check if user qualifies for a badge and award it."""
        subjects_level_file = Path(__file__).parent / "dashboard files/subjects_level.json"
        badges_file = Path(__file__).parent / "dashboard files/subjects_badges.json"
        temp = {}
        
#------------------------------------------------------------------------IF FILE IS EMPTY-------------------------------------------------------
        if os.path.getsize(badges_file) == 0:
            with open(subjects_level_file, "r") as f:
                data = json.load(f)
                
                for key in data.keys():
                    temp[key] = []
                temp["Overall level"] = []

            with open(badges_file, "w") as f:
                json.dump(temp, f, indent=4)
        
#------------------------------------------------------------------------For new subjects-------------------------------------------------------
        logging.debug("checking for new subjects")
        try:
            with open(subjects_level_file, "r") as f:
                data = json.load(f)
            
            with open(badges_file, "r") as f:
                subject_badges = json.load(f)
        except json.decoder.JSONDecodeError as e:
            logging.warning("⚠️ JSON is malformed!")
            logging.warning(e)
            return
        
        except FileExistsError:
            # Create the file
            badges_file.touch(exist_ok=True)
            return
        
        for key in data.keys():
            if key not in subject_badges:
                logging.debug(f"{key} has not badges list")
                subject_badges[key] = []
        
        open(badges_file).close()
        with open(badges_file, "w") as f:
            json.dump(subject_badges, f, indent=4)
            logging.debug("added new subject")
        
        logging.debug("All good, append badges.")
        return True
    
    def badge_appending_method(self, dict_key, badge_name):
        """Adds badges to badges file"""
        badges_file = Path(__file__).parent / "dashboard files/subjects_badges.json"

        with open(badges_file, "r") as f:
            subject_badges = json.load(f)

        if badge_name not in subject_badges[dict_key]:
            subject_badges[dict_key].append(badge_name)
        else:
            return

        with open(badges_file, "w") as f:
            json.dump(subject_badges, f, indent=4)
        logging.debug(f"Added {badge_name} badge for {dict_key}")

    def append_badges(self):
        """Add badges for a particular subject"""
        total_xp_file = Path(__file__).parent / "dashboard files/bank_details.json"
        subjects_level_file = Path(__file__).parent / "dashboard files/subjects_level.json"

        try:
            with open(subjects_level_file, "r") as f:
                subjects_data = json.load(f)

            with open(total_xp_file, "r") as f:
                data = json.load(f)
                total_xp = data["total_xp"]
        except json.decoder.JSONDecodeError as e:
            logging.warning("⚠️ JSON is malformed!")
            logging.warning(e)
            return
        
#------------------------------------------------------------------checking if process ready----------------------------------------------------
        self.subjects_badges_state()

#--------------------------------------------------------------------badge for over level 5----------------------------------------------------
        if self._overAll_level == 5:
            self.badge_appending_method("Overall level", "🎖️ Level 5 Unlocked")

#----------------------------------------------------------badge for every tenth level achieved.------------------------------------------------
        if self._overAll_level % 10 == 0:
            self.badge_appending_method("Overall level", "💎 Every Tenth Tier counts")
        
#----------------------------------------------------------------badge for every thousand xps earned--------------------------------------------
        for key in subjects_data:
                xp = subjects_data[key].get("xp", 0)
                if xp % 1000 == 0 and xp != 0: 
                    self.badge_appending_method(key, "🏆 1K Subject XP Master")

#-------------------------------------------------------------badge for every tenth level for a  subject----------------------------------------
        for key in subjects_data:
            subject = subjects_data[key].get("level", 0)
            if subject % 10 == 0 and subject !=0:
                self.badge_appending_method(key, "🎯 Every Ten Counts")

#----------------------------------------------------------------------badge for every 10000 xp earned------------------------------------------
        if total_xp % 10000 == 0:
            self.badge_appending_method("Overall level", "🖤 Every Ten K Counts")

    def load_overall_level(self):
        """Loads the Overall level when app is opened"""
        file = Path(__file__).parent / "dashboard files/overall_level.json"

        with open(file, "r") as f:
            data = json.load(f)
        level = data["overall_level"]
        self._overAll_level = level
        return self._overAll_level

    def load_username(self):
        """"Load username""" 
        username_file = Path(__file__).parent / "dashboard files/username.json"
        try:
            with open(username_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        name = data["username"]
        return name
    
    def save_username(self):
        """Save new username""" 
        username_file = Path(__file__).parent / "dashboard files/username.json"
        try:
            with open(username_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
#--------------------------------------------------------------------------creating file anew---------------------------------------------------
            data = {}
            data["username"] = ""
            data["userstate"] = False
            with open(username_file, "r") as f:
                json.dump(data, f)
            logging.debug("New file written")

        data["username"] = self._name
#------------------------------------------------------------------------saving username--------------------------------------------------------
        open(username_file, "w").close()
        with open(username_file, "w") as f:
            json.dump(data, f)
        logging.debug(f"New username: {data["username"]}")
#===============================================================================================================================================
#***********************************************************************************************************************************************
#=====================================================================Autodidex bank class======================================================
class AutodidexBank:
    """Details with xp, badges,lumens and user bank details """
#------------------------------------------------------------------------Data field-------------------------------------------------------------
    def __init__(self, user_info):
        self._wallet_total: Optional[int] = None #intial value
        self._bank_details_file = Path(__file__).parent / "dashboard files/bank_details.json"
        self.badges: Optional[int] = None #intial value
        self.user_info = user_info #UserIfo()

#-------------------------------------------------------------loading lumens and xp #points------------------------------------------------------
        self._load_wallet_total_and_xp()
#=========================================================================Getters===============================================================
    @property
    def wallet(self) -> int:
        
        return self._wallet_total
    
    @property
    def xpPoints(self):
        return self._xp_total

    @property
    def subjectXp(self):
        return self._subjectXp

    @wallet.setter
    def wallet(self, lumens:int
               ):
        if not isinstance(lumens, int):
            raise TypeError("Lumens not the expect value.")

        if lumens < 0:
            raise ValueError("You cannot deposit negative lumens.")

        self._wallet_total += lumens
        self._save_wallet_total()

        logging.info(f"Deposited {lumens} lumens. New balance: {self._wallet_total}")
#=================================================================================Setters=======================================================
    @xpPoints.setter
    def xpPoints(self, points):
        if points < 0:
            return "You cannot earn negative xp points"
        else:
            self._xp_total += points

    @subjectXp.setter
    def subjecXp(self, points):
        if points < 0:
            return "You cannot earn negative xp points"
        else:
            self._xp_total += points
#===============================================================================================================================================
#============================================================================Class Methods======================================================
    def _save_wallet_total(self, withdraw=False):
        bank_details_file = Path(__file__).parent / "dashboard files/bank_details.json"
        try:
            with open(bank_details_file, "r") as f:
                bank_details = json.load(f)
        except FileNotFoundError:
            return "❌ File not found"
        
        bank_details["lumens"] = self._wallet_total
        open(bank_details_file, "w").close() #clearing file for updated data
        with open(self._bank_details_file, "w") as f:
            json.dump(bank_details, f, indent=4)
    
    def _load_wallet_total_and_xp(self):
        """Loads the wallet and total xp amounts when app is opened"""
        if self._bank_details_file.exists():
            try:
                with open(self._bank_details_file, "r") as f:
                    data = json.load(f)
                    self._wallet_total = data.get("lumens", 0)
                    self._xp_total = data.get("total_xp", 0)
            except json.JSONDecodeError:
                logging.warning("Bank details file is corrupted. Starting with 0 lumens and 0 xp.")
        else:
            self._wallet_total = 0
            
        self.load_earned_badges()

    def earn_subject_xp(self):
        """User earns XP in a specific subject."""
        progress_file = Path(__file__).parent / "habit tracker files/weekly_progress.json"
        subjects_file = Path(__file__).parent / "habit tracker files/last saved.txt"
        subjects_data = Path(__file__).parent / "dashboard files/subjects_level.json"
        date_file = Path(__file__).parent / "habit tracker files/save_state.pkl"
        state_file = Path(__file__).parent / "dashboard files/game_update_state.json" 
        today = datetime.datetime.today()
        subject_level_data = self.user_info.initialize_subjects()

        try:
            with open(progress_file, "r") as f:
                data = json.load(f)
            with open(subjects_file, "r") as f:
                subjects = f.readlines()
            with open(state_file, "r") as f:
                state = json.load(f)
                state = state["state"]
                logging.debug(f"The state is {state}")

#------------------------------------------------------------------Check if date file is empty ormissing---------------------------------------
            if not date_file.exists() or os.path.getsize(date_file) == 0:
                logging.warning("⚠️ Date file missing or empty. Saving today's date.")
                with open(date_file, "wb") as f:
                    pickle.dump(today, f)
                saved_date = today
            else:
                with open(date_file, "rb") as f:
                    saved_date = pickle.load(f)

        except (FileNotFoundError):
            raise FileNotFoundError("Couldn't find files for this process")
            

        if today.date() == saved_date.date() if isinstance(saved_date, datetime.datetime) else saved_date:
            if state:
                logging.debug(f"subject data is {subject_level_data}")
                self.update_user_info(data, subjects, subjects_data, subject_level_data)
                state = False
                self.user_info.save_update_state(state)
                self.user_info.overall_level_up()
                self._load_wallet_total_and_xp()
                self.user_info.append_badges()
            else:
                self._load_wallet_total_and_xp()
                logging.debug("app already updated")
        else:
            state = True
            self.user_info.save_update_state(state)
            logging.debug("state ready for update")

        
    def update_user_info(self, data, subjects, subjects_data, subject_level_data):
        """"Updates the subjesct level"""
        if data != {}:
            for key, value in data.items():
                        for i in range(len(subjects)):
                            if subjects[i].strip() == key.strip():
                                subject = subjects[i].strip()
                                if subject in subject_level_data:
                                    check = len(value)
                                    income = self.progress_conversion(check)
                                    self.add_subject_xp(subject, income)
                                    self.subject_level_up(subject)
                                    logging.debug(f'subject updated is {subject}')
                                    logging.debug(self.user_info.subjects)
                                    self.add_total_xp(income)

            open(subjects_data).close()
            with open(subjects_data, "w") as f:
                json.dump(self.user_info.subjects, f)
            return self.user_info.subjects
        else:
            empty_dict = {}
            return empty_dict
        
    def subject_level_up(self, subject):
        """Add level up for a subject if new level > current and rewards with 10 lumens"""
        subjects_data = self.user_info.subjects
        current_level = subjects_data[subject]["level"]
        new_level = subjects_data[subject]["xp"] //  200

        if new_level > current_level:
            subjects_data[subject]["level"] += new_level
            self.wallet = 10
        
    def add_total_xp(self, amount):
        """"Add total xp amount"""
        file = Path(__file__).parent / "dashboard files/bank_details.json"
        with open(file, "r") as f:
            bank_details = json.load(f)

        bank_details["total_xp"] += amount

        open(file).close()
        with open(file, "w") as f:
            json.dump(bank_details, f)
        
    def progress_conversion(self,value):
        """Performs conversion of checkboxes ticked for the week into xps for the subject"""
        subjectXP = value * 20
        return subjectXP 
    
    def spend_lumens(self, amount: int):
        """Withdraws amount being spent from user's lumen amount"""
        bank_details_file = Path(__file__).parent / "dashboard files/bank_details.json"
        with open(bank_details_file, "r") as f:
            bank_details = json.load(f)

        logging.debug(f"current bank amount: {self._wallet_total}")
        self._wallet_total = self._wallet_total - amount
        bank_details["lumens"] = self._wallet_total
        
#-----------------------------------------------------------------------clear old data-----------------------------------------------------------
        open(bank_details_file, "w").close()
#--------------------------------------------------------------------------load new data----------------------------------------------------------
        with open(bank_details_file, "w") as f:
            json.dump(bank_details, f, indent=4)
        logging.debug(f"Transection complete")
        return self._wallet_total
    
    def remove_badge(self, subject, badge, index):
        """"Removes traded badge from badge collection"""
        subject_badges_file = Path(__file__).parent / "dashboard files/subjects_badges.json"

        self.badges[subject].pop(index)
        logging.debug(f"remove(in Autodidex) {badge} badge from {subject}")
        logging.debug(self.badges)

        open(subject_badges_file, "w").close()
        with open(subject_badges_file, "w") as f:
            json.dump(self.badges, f, indent=4)
        return True

    def add_subject_xp(self, subject, points):
        """"Adds the xp points passed to the given subject"""
        subjects_data = self.user_info.subjects
        subjects_data[subject]["xp"] += points
        self._xp_total += points

    def load_lumens(self):
        """Loads the amount of lumens when app is open"""
        file = Path(__file__).parent / "dashboard files/bank_details.json"
        with open(file, "r") as f:
            data = json.load(f)
        lumens = data["lumens"]
        self._wallet_total = lumens

    def load_xp(self):
        """Loads the total xps when the app is started"""
        file = Path(__file__).parent / "dashboard files/bank_details.json"
        with open(file, "r") as f:
            data = json.load(f)
        xp = data["total_xp"]
        self._xp_total = xp
    
    def load_earned_badges(self):
        """Loads the badge collection when is started"""
        earned_badges_file = Path(__file__).parent / "dashboard files/subjects_badges.json"
        try:
            with open(earned_badges_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.badges = data
            # logging.debug(f"badges data(load_earned_badges): {self.badges}")
            return
        except FileNotFoundError:
            return "file not found"
        except json.JSONDecodeError:
            open(earned_badges_file, "w").close()
            return "subjects_badges.json file is corrupted. File has been reset"
    
    def load_internal_methods(self):
        """Loads internal methods needed when app is started"""
        self._load_wallet_total_and_xp()
#===============================================================================================================================================
#***********************************************************************************************************************************************
#======================================================================Polymart Class===========================================================
class PolyMart:
#-------------------------------------------------------------------------data fields-----------------------------------------------------------
    def __init__(self,bank_account):
        self.bank_account = bank_account #AutodidexBank(UserIfo())
        self.store_items = {}
        self.trade_items = {}
#-----------------------------------------------------------------------------------------------------------------------------------------------
#===============================================================================================================================================
#======================================================================Class Methods============================================================
    def load_store_items(self):
        """Load store items to correct item dict"""
        items_list_file = Path(__file__).parent / "dashboard files/store_items.json"
        
        with open(items_list_file, "r", encoding="utf-8") as f:
            items_list = json.load(f)
        
        for key, value in items_list[0].items():
            self.store_items[key] = value

        for key, value in items_list[1].items():
            self.trade_items[key] = value

    def purchase_item(self, item_name):
        """"Purchases or trades items selected"""
        logging.debug(item_name)
        
#------------------------------------------------------------------------ Separating the name from the price -----------------------------------
        tuple_items = item_name.partition(":")
        item = tuple_items[0]
        item_name = str(item).strip().lower()
        logging.debug(f"item for purchase {item_name}")
        logging.debug(self.store_items)

        for key, value in self.store_items.items():
            cost = int(value)
            key = str(key).strip().lower()

            if item_name == key:
                if self.bank_account.wallet >= cost:
                    self.bank_account.spend_lumens(cost)
                    return f"🛒 You bought {item_name} for {cost} lumens!"
                else:
                    return  "Transection Failed",f"💸 Not enough lumens to purchase {item_name}"
                    
                
#----------------------------------------------------------------------------trading badges-----------------------------------------------------
        for key, value in self.trade_items.items():
            trade_amount = int(value)
            trade_item = str(key).strip().lower()
            logging.debug(f'items for trand in polymart: {self.trade_items}')
            logging.debug(f"Item to be traded {item_name}")

            if item_name == trade_item:
                logging.debug("Item found")
                self.bank_account.wallet = trade_amount
                self.remove_traded_badge(item_name)
                return f"Transaction Complete Traded {item_name} for {trade_amount}"
                
#-------------------------------------------------------------------------If loop finishes and no item was found--------------------------------
        return "❌ Item not found in PolyMart."
    
    def remove_traded_badge(self, store_item):
        """Call the method for removes badges in AutodidexBank"""
        for key, value in self.bank_account.badges.items():
            subject = key
            badges_list = value
            for index, badges in enumerate(badges_list):
                badge_to_be_traded = badges.lower()
                logging.debug(f"badge to be traded: {store_item} badge in badge collection {badge_to_be_traded}")
                if store_item == badge_to_be_traded:
                    logging.debug(f"badges data(remove_traded_badge: method): {store_item} badge found in {subject}")
                    self.bank_account.remove_badge(subject, store_item, index)
                    return
                else:
                    logging.debug(f"badge not found in {subject}")

class SpinningLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 80, QFont.Bold))
        self.angle = 0

#----------------------------------------------------------------Timer to simulate 3D spin------------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.spin)
        self.timer.start(30)  # Spin speed
#=====================================================================Class Methods=============================================================
    def spin(self):
        self.angle += 2
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

#---------------------------------------------------------------------Create radial gradient (white to purple)----------------------------------
        gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()/1.5)
        gradient.setColorAt(0, QColor("white"))
        gradient.setColorAt(1, QColor(128, 0, 128))  # Purple
        painter.fillRect(self.rect(), QBrush(gradient))

#-----------------------------------------------------------------------Simulate 3D spin using scaling on the x-axis----------------------------
        transform = QTransform()
        scale = math.cos(math.radians(self.angle))
        transform.translate(self.width()/2, self.height()/2)
        transform.scale(scale, 1)
        transform.translate(-self.width()/2, -self.height()/2)
        painter.setTransform(transform)

#------------------------------------------------------------------------------Draw the text----------------------------------------------------
        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
#===============================================================================================================================================
#***********************************************************************************************************************************************
#=====================================================================Dashboard UI==============================================================
class MainWindow(QMainWindow):
#-----------------------------------------------------------------------Data Fields-------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex Dashboard")
        
        self.user = UserIfo()
        self.bank = AutodidexBank(self.user) 
        self.market = PolyMart(self.bank) 
        self.name_null_value: Optional[str] = None
        self.user_present = self.present_user_state()


        self.window_load = QWidget()
       
        self.label = SpinningLabel("Autodidex")
        self.label.setObjectName("onloadlabel")
        self.name_input =  QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        enter_icon = Path(__file__).parent / "Icons/icons8-enter-64.png"
        self.enter_btn = QPushButton("")
        self.enter_btn.setIcon(QIcon(str(enter_icon)))
        self.enter_btn.setIconSize(QSize(30, 30))
        self.name_input.returnPressed.connect(self.load_user_name)
        self.enter_btn.clicked.connect(self.load_user_name)

        self.buy_icon = Path(__file__).parent / "Icons/icons8-pay-64.png"
        self.trade_icon = Path(__file__).parent / "Icons/icons8-trade-64.png"
        self.light_icon = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.dark_icon = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.thm_pref = Path(__file__).parent / "v tab files/dashboard_config.json"

        self.theme_state: Optional[str] = None
        self.dark_mode: Optional[str] = None
        self.light_mode: Optional[str] = None
        self.theme_toggle = QPushButton("")
        self.theme_toggle.setIcon(QIcon(str(self.light_icon)))

        self.cpt_timer = QTimer(self)
        self.cpt_timer.setInterval(2000)  # 2000 ms = 2 seconds
        self.cpt_timer.timeout.connect(self.check_new_cpt)
        self.cpt_timer.start()

        self.badge_list = QListWidget()
        self.container = QWidget()

        self.subject_combo = QComboBox()

        # self.on_load()
        # if self.user_present == True:
        #     self.setup_ui()
        # self.thm_wrapper()
        # self.init_wrapper()
#===============================================================================Class Methods===================================================
    def setup_ui(self):
        """"Struture the UI"""
        layout = QVBoxLayout()

#---------------------------------------------------------------------------Header Section with Toggle------------------------------------------ 
        header_layout = QHBoxLayout()

        self.theme_toggle.clicked.connect(self.toggle_theme)
        self.theme_toggle.setIconSize(QSize(30, 30))
        header_layout.addWidget(self.theme_toggle, alignment=Qt.AlignmentFlag.AlignCenter)

        label_layout = QHBoxLayout()
        self.dashboard_label = SpinningLabel("Autodidex") 
        self.dashboard_label.setObjectName("dblabel")
        label_layout.addWidget(self.dashboard_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        n_icon = Path(__file__).parent / "Icons/icons8-name-64.png"
        self.name_label = QLabel(
                f'<img src="{n_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.user.name}</span>'
            )
        self.name_label.setToolTip("Name")

        l_icon = Path(__file__).parent / "Icons/icons8-bill-64.png" 
        self.level_label = QLabel(
                f'<img src="{l_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.user.load_overall_level()}</span>'
            )
        self.level_label.setToolTip("overall level")

        self.w_icon = Path(__file__).parent / "Icons/icons8-wallet-64.png"
        self.wallet_label = QLabel(
                f'<img src="{self.w_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.wallet} Lumens</span>'
            )
        self.wallet_label.setToolTip("Wallet")

        xp_icon = Path(__file__).parent / "Icons/icons8-points-64.png"
        self.xp_label = QLabel(
                f'<img src="{xp_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.xpPoints}</span>'
                            )
        self.xp_label.setToolTip("XP points")

        layout.addLayout(label_layout)
        layout.addLayout(header_layout)
        layout.addWidget(self.name_label)   
        layout.addWidget(self.level_label)
        layout.addWidget(self.wallet_label)
        layout.addWidget(self.xp_label)

#----------------------------------------------------------------------Subject XP System--------------------------------------------------------
        xp_layout = QHBoxLayout()
        self.subject_combo.currentIndexChanged.connect(self.display_badges)
        
        self.subject_combo.addItems(self.add_subject())

        subjects_label = QLabel()
        s_icon = Path(__file__).parent / "Icons/icons8-calibre-64.png"
        subjects_label.setText(f'<img src="{str(s_icon)}" width="40" height="40">')
        subjects_label.setToolTip("Subjects")

        xp_layout.addWidget(subjects_label)
        xp_layout.addWidget(self.subject_combo)
        layout.addLayout(xp_layout)

#-------------------------------------------------------------------------Badge Display---------------------------------------------------------
        badges_label = QLabel()
        b_icon = Path(__file__).parent / "Icons/icons8-trophy-64.png"
        badges_label.setText(f'<img src="{str(b_icon)}" width="40" height="40">')
        badges_label.setToolTip("Badges")
        layout.addWidget(badges_label)
        layout.addWidget(self.badge_list)

#--------------------------------------------------------------------------PolyMart-------------------------------------------------------------
        c_icon = Path(__file__).parent / "Icons/icons8-cart-64.png"
        cart_label = QLabel(f'<img src="{str(c_icon)}" width="40" height="40">'
                            f'<span style="font-size: 20px;"> PolyMart⁚ </span>')
        layout.addWidget(cart_label)
        self.store_combo = QComboBox()
        
        self.store_combo.addItems(self.polymart_items())
        self.store_combo.currentIndexChanged.connect(self.trade_btn)

        self.buy_btn = QPushButton("")
        self.buy_btn.setIcon(QIcon(str(self.buy_icon)))
        self.buy_btn.setIconSize(QSize(30, 30))

        self.buy_btn.clicked.connect(self.buy_item)
        layout.addWidget(self.store_combo)
        layout.addWidget(self.buy_btn)

        self.container.setLayout(layout)
        self.setCentralWidget(self.container)

    def on_load(self):
        """"Checks is there is a logging in, if not, asks for new user to loggin"""
        logging.debug(f"The name of the user is {self.user.name}")
        if self.user_present == False:
            if self.name_null_value == None:
                main_layout = QVBoxLayout()
                self.setLayout(main_layout)
                layout = QHBoxLayout()
                

                layout.addWidget(self.name_input)
                layout.addWidget(self.enter_btn)
                main_layout.addWidget(self.label)
                main_layout.addLayout(layout)
                self.window_load.setLayout(main_layout)
                self.setCentralWidget(self.window_load)
                # if self.user.name:
                    # self.save_user_state(True)
            # else:
            #     self.setup_ui()
        logging.debug(f"The user state is {self.user_present}")
        logging.debug(f"The name of the user is now {self.user.name}")
            
    def subject_clicked(self):
        logging.debug("Subject clicked")

    def load_user_name(self):
        name = self.name_input.text().strip()
        if name:
            try:
                self.user.name = name
                self.user.save_username()
                self.user_present = True
                logging.debug("User logged in as: %s", self.user.name)

#------------------------------------------------------------------replacing the window with the actual UI--------------------------------------
                self.setup_ui()
            except ValueError as e:
                logging.debug("Name validation failed: %s", e)
                QMessageBox.warning(self, "Invalid Name", str(e))
        else:
            QMessageBox.warning(self, "Missing Name", "Please enter a name to continue.")    

    def buy_item(self):
        """"Calls the method purchasing or trades from PolyMart"""
        item = self.store_combo.currentText()

        res = self.market.purchase_item(item)
        QMessageBox.information(self, "Transaction result", res, QMessageBox.Ok)
        new_amount = self.bank.wallet
        self.wallet_label.setText(
                f'<img src="{self.w_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {new_amount} Lumens</span>')

        logging.debug(res)

    def trade_btn(self):
        """Switches between trade item, buy items button when needed"""
        trade_items_file = Path(__file__).parent / "dashboard files/game_badges.json"
        try:
            with open(trade_items_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                trade_items = data['badges']
                logging.debug(f"badges for trade: {trade_items}")
        except FileNotFoundError:
#----------------------------------------------------------------------add back open back up file feature---------------------------------------
            raise ValueError("file not found. Loading back up")

        item = self.store_combo.currentText().partition(":")[0]
        logging.debug(f"item to be traded {item}")

        if item.strip() in trade_items:
            self.buy_btn.setIcon(QIcon(str(self.trade_icon)))
            self.buy_btn.setToolTip("Trade Item")
            logging.debug("switched to trade button")
        else:
            self.buy_btn.setIcon(QIcon(str(self.buy_icon)))
            self.buy_btn.setToolTip("Buy Item")
            logging.debug("switched back to buy button")

    def display_badges(self, index):
        """Display badges for a particular subject"""
        badges_list_file = Path(__file__).parent / "dashboard files/subjects_badges.json"

        try:
            if not badges_list_file.exists():
                with open(badges_list_file , "r", encoding="utf-8") as f:
                    badges_list = json.load(f)

                self.badge_list.clear()
                selected_item = self.subject_combo.itemText(index)

                subject_badges = badges_list[selected_item]
            
                self.badge_list.addItems(set(subject_badges))
        except FileNotFoundError:
            badges_list_file.touch(exist_ok=True)
        except (json.decoder.JSONDecodeError, Exception):
            open(badges_list_file, "w").close()
            self.user.subjects_badges_state()
        
    def add_subject(self):
        """Load subjects from JSON and return them as a list. Handles missing or empty files gracefully."""
        subjects_data = Path(__file__).parent / "habit tracker files/last saved.txt"
        subjects_list = []

        try:
            if not subjects_data.exists():
                logging.warning(f"Subjects file not found: {subjects_data}")
                return subjects_list

            if subjects_data.stat().st_size == 0:
                logging.debug("Subjects file is empty.")
                subjects_list.append("None")
                return subjects_list

            with open(subjects_data, "r", encoding="utf-8") as f:
                data = []
                cp_list = f.readlines()
                if not isinstance(cp_list, list):
                    logging.warning("Subjects file format is invalid (expected a list object).")
                    return subjects_list
                
                #removing whitespace
                for cp in cp_list:
                    cp = cp.strip()
                    data.append(cp)
                logging.debug(f"CP data {data}")
            
        except FileNotFoundError:
            logging.error("Failed to load file, file not found")
        except Exception as e:
            logging.error(f"Unexpected error while loading subjects: {e}")

        subjects_list = data

        return subjects_list

        
    def polymart_items(self):
        """Get list of items from Polymart class for the UI"""
        items_list_file = Path(__file__).parent / "dashboard files/store_items.json"
        store_products = []
        
        with open(items_list_file, "r", encoding="utf-8") as f:
            items_list = json.load(f)
        
        store_items = items_list[0]
        badge_trade_values = items_list[1]

        for key, value in store_items.items():
            item = f"{key} : {value} lumens"
            store_products.append(item)

        for key, value in badge_trade_values.items():
            item = f"{key} : {value}"
            store_products.append(item)

        return store_products
    
    def present_user_state(self):
        """checks whether or not a new username is required"""
        userstate_file = Path(__file__).parent / "dashboard files/username.json"

        try:
            with open(userstate_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
            data["username"] = ""
            data["userstate"] = False
            with open(userstate_file, "w") as f:
                json.dump(userstate_file, data)
        
        state = data["userstate"]
        self.name_null_value = data["username"]
        logging.debug(f"The present user state is {state}")
        return state
    
    def save_user_state(self, state):
        """saves whether or not there is a username saved"""
        userstate_file = Path(__file__).parent / "dashboard files/username.json"
        logging.debug(f"Passed in userstate is {state}")

#-------------------------------------------------------------------------laad data-------------------------------------------------------------
        with open(userstate_file, "r") as f:
            data = json.load(f)

#---------------------------------------------------------------------change value of state-----------------------------------------------------
        data["userstate"] = state
        
#---------------------------------------------------------------------------clear old data------------------------------------------------------
        open(userstate_file, "w").close()
#---------------------------------------------------------------------------load new data-------------------------------------------------------
        with open(userstate_file, "w") as f:
            json.dump(data, f)
        logging.debug(f'new user state saved')
        return

    def load_themes(self):
        theme_files = {
            "light_mode": Path(__file__).parent / "themes files/light_mode.txt",
            "dark_mode": Path(__file__).parent / "themes files/dark_mode.txt"
        }

        for name, path in theme_files.items():
            with open(path, "r") as f:
                setattr(self, name, f.read())

                
    def toggle_theme(self):
        """Switches between light and dark mode"""

        if self.theme_state == "light":
            stylesheet_file = Path(__file__).parent / "themes files/dark_mode.txt"
            self.theme_state = "dark"
            self.theme_toggle.setText("")
            self.theme_toggle.setIcon(QIcon(str(self.light_icon)))
        else:
            stylesheet_file = Path(__file__).parent / "themes files/light_mode.txt"
            self.theme_state = "light"
            self.theme_toggle.setText("")
            self.theme_toggle.setIcon(QIcon(str(self.dark_icon)))
        self.theme_toggle.setIconSize(QSize(30, 30))

        with open(stylesheet_file, "r") as f:
            stylesheet = f.read()

        self.setStyleSheet(stylesheet)
    
    def load_thm_pref(self):
        "loads user preffered theme"
        try:
            with open(self.thm_pref, "r") as f:
                data = json.load(f)
                self.theme_state = data["mode"]
        except (FileNotFoundError, json.decoder.JSONDecodeError):
#--------------------------------------------------------------------------------set to defaulf-------------------------------------------------
            self.theme_state = "dark"
        
        if self.theme_state == "dark":
            self.setStyleSheet(self.dark_mode)
        elif self.theme_state == "light":
            self.setStyleSheet(self.light_mode)
        return
    
    def thm_wrapper(self):
        self.load_themes()
        self.load_thm_pref()

    def check_new_cpt(self):
        """Checks for new subjects added to the last saved.txt"""
        # if self.user_present == True:
        #remove duplicates from list
        subjects = set(self.add_subject())
        #convert set into list
        subjects = list(subjects)
        self.subject_combo.clear()
        self.subject_combo.addItems(subjects)
    
    def update_ui(self):
        self.bank._load_wallet_total_and_xp()
        self.wallet_label.setText(
                f'<img src="{self.w_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.wallet} Lumens</span>'
            )
        

    def init_wrapper(self):
        self.on_load()
        if self.user_present == True:
            self.setup_ui()
        self.thm_wrapper()
        self.bank.earn_subject_xp()
        self.bank.load_internal_methods()
        self.market.load_store_items
#===========================================================================Run application=====================================================
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.resize(400, 600)
#     window.show()
#     sys.exit(app.exec())
