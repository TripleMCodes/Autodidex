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
from PySide6.QtCore import QSize, Qt, QTimer, QFileSystemWatcher
from PySide6.QtGui import (QBrush, QColor, QFont, QIcon, QLinearGradient,
                           QPainter, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
                               QLabel, QLineEdit, QListWidget, QMainWindow,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)
from autodidex_cache import DictionaryCache
from themes_db import Themes
from dash_board_db import Dashboard
from cp_tracker_db import Cp_tracker
#cache class instance
cache = DictionaryCache()
cp_tracker = Cp_tracker()
dashboard = Dashboard()
themes = Themes()
#=====================================================================logs enable/disable======================================================
logging.basicConfig(level=logging.DEBUG) 
# logging.disable(logging.DEBUG)
#===============================================================================================================================================
#***********************************************************************************************************************************************
#========================================================================User INfo Class=======================================================
class UserIfo:

    def __init__(self):
        self._name = dashboard.get_user_name()
        # self._title = ""
        self._overAll_level = self.load_overall_level() 
        self.subjects = []
#============================================================================================================================================= 
#==================================================================================Getters=====================================================
    @property
    def name(self):
        return self._name
    
    @property
    def level(self):
        return self._overAll_level
#==============================================================================================================================================
#===============================================================================Setters=========================================================
    @name.setter
    def name(self, name):
        if name and name[0].isupper():
            self._name = name
        else:
            raise ValueError("Please capitalize the first letter of your name")
        
    @level.setter
    def level(self, total):
        self._overAll_level += total

#==============================================================================================================================================
#===========================================================================Class Methods======================================================
    def initialize_subjects(self):
        """Load subjects saved in Habit Tracker"""
        
        self.subjects = cp_tracker.get_cerebral_pursuits()
        return self.subjects

    def load_overall_level(self):
        """Load overall level from db if not cached, otherwise load cached overall level."""

        level = cache.get("overall_level")
        print(f'the overall level is: {level}')
        if level == None:
            level = dashboard.get_overall_level()
            cache.set("overall_level", level)
        return level
 
    def overall_level_up(self):
        """Sum all subject XP points, each new gain of 500 XP points gives 1 overall level up."""
        xp_amount = dashboard.get_total_xp()
        new_overall_level = xp_amount // 500

        if new_overall_level > cache.get("overall_level"):
            self._overAll_level = new_overall_level
            dashboard.increment_overall_level(new_overall_level)
            self._oveall_level_badge_reward()
            cache.set("overall_level", new_overall_level)
            self._overAll_level = new_overall_level

    def _oveall_level_badge_reward(self):
        """Give overall badge reward"""
#--------------------------------------------------------------------badge for over level 5----------------------------------------------------
        if self._overAll_level == 5:
            dashboard.add_new_badge("🎖️ Level 5 Unlocked")
#----------------------------------------------------------badge for every tenth level achieved.-----------------------------------------------
        if self._overAll_level % 10 == 0:
            dashboard.add_new_badge("💎 Every Tenth Tier counts")
        
        cp_with_badges = dashboard.get_cp_with_badges()
        cache.set("cp_badges", cp_with_badges)
        
        badges = dashboard.get_all_badges()
        cache.set("badges", badges)

    def cp_level_badge_reward(self):
        """Reward every level for a particular of a cp"""

        reward_badges = [ "🎯 Every Ten Counts", "🏆 1K Subject XP Master"]

        cp_with_levels = cp_tracker.get_cp_with_level()
        cp_with_xp = cp_tracker.get_cp_with_xp()

        for k, v in cp_with_levels.items():
            if v % 10 == 0 and v != 0:
                msg = dashboard.add_cp_badge(reward_badges[0], k)
                if msg:
                    logging.debug(msg["message"])
    
        for k, v in cp_with_xp.items():
                if v % 10 == 0 and v != 0:
                    msg = dashboard.add_cp_badge(reward_badges[1], k)
                    if msg:
                        logging.debug(msg["message"])
        
        cp_with_badges = dashboard.get_cp_with_badges()
        cache.set("cp_badges", cp_with_badges)
        
        badges = dashboard.get_all_badges()
        cache.set("badges", badges)

#==============================================================================================================================================
#**********************************************************************************************************************************************
#=====================================================================Autodidex bank class=====================================================
class AutodidexBank:
    """Details with xp, badges,lumens and user bank details """
#------------------------------------------------------------------------Data field------------------------------------------------------------
    def __init__(self, user_info):
        self._wallet_total: Optional[int] = None #intial value
        self._bank_details_file = Path(__file__).parent / "dashboard files/bank_details.json"
        self.badges: Optional[int] = None #intial value
        self._xp_total = dashboard.get_total_xp()
        self._wallet_total = dashboard.get_lumens_amount()
        self.user_info = user_info #UserIfo()

#-------------------------------------------------------------loading lumens and xp #points----------------------------------------------------
        # self._load_wallet_total_and_xp()
        # self.earn_subject_xp()
#=========================================================================Getters==============================================================
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
    def wallet(self, lumens:int):
        if not isinstance(lumens, int):
            raise TypeError("Lumens not the expect value.")

        if lumens < 0:
            raise ValueError("You cannot deposit negative lumens.")

        self._wallet_total += lumens
        dashboard.add_lumens(self._wallet_total)
        # self._save_wallet_total()

        logging.info(f"Deposited {lumens} lumens. New balance: {self._wallet_total}")
#=================================================================================Setters======================================================
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
#==============================================================================================================================================
#============================================================================Class Methods=====================================================
    def earn_subject_xp(self):
        """User earns XP in a specific subject."""

        subjects_data = cp_tracker.get_cp_with_check_marks()
        logging.debug(f"subject data is {subjects_data}")
        self.update_user_info(subjects_data)
    
    def update_user_info(self,subjects_data):
        """"Updates the subjesct level"""

        cp_cached_data = cache.get("cp_streak")

        if cp_cached_data == None:
            cache.set("cp_streak", subjects_data)
        else:
            for cp, streak in subjects_data.items():
                for cache_cp, cache_streak in cp_cached_data.items():
                    if cp == cache_cp:
                        if cache_streak < streak:
                            xp = self.progress_conversion(streak)
                            dashboard.add_total_xp(xp)
                            self._xp_total += xp
                            cp_tracker.save_cp_xp(cp, xp)
                            self.subject_level_up(cp)
                            self.user_info.cp_level_badge_reward()
                            self.user_info.overall_level_up()
                            logging.debug(f'Update added for {cp}')
        cache.set("cp_streak", subjects_data)

    def subject_level_up(self, subject):
        """Add level up for a subject if new level > current and rewards with 10 lumens"""
        #get subject xp
        subject_xp = cp_tracker.get_cp_specific_xp(subject)
        current_level = cp_tracker.get_cp_specific_level(subject)
        #check for new level
        new_level = subject_xp //  200

        #set new level
        if new_level > current_level:
            cp_tracker.increment_cp_level(subject, new_level)
            #add lumens
            self.wallet = 10
        
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
        msg = dashboard.decrement_lumens(self._wallet_total)
        return msg

    
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
    
#==============================================================================================================================================
#**********************************************************************************************************************************************
#======================================================================Polymart Class==========================================================
class PolyMart:
#-------------------------------------------------------------------------data fields----------------------------------------------------------
    def __init__(self,bank_account):
        self.bank_account = bank_account #AutodidexBank(UserIfo())
        self.store_items = {}
        self.trade_items = {}
#----------------------------------------------------------------------------------------------------------------------------------------------
#==============================================================================================================================================
#======================================================================Class Methods===========================================================
    def load_store_items(self):
        """Load store items to correct item dict"""
        items_list_file = Path(__file__).parent / "dashboard files/store_items.json"
        
        with open(items_list_file, "r", encoding="utf-8") as f:
            items_list = json.load(f)
        
        for key, value in items_list[0].items():
            self.store_items[key] = value
        logging.debug(f"The store items {self.store_items}")

        for key, value in items_list[1].items():
            self.trade_items[key] = value
        logging.debug(f"The store items {self.trade_items}")

    def purchase_item(self, item_name):
        """"Purchases or trades items selected"""
        logging.debug(f"the item name is {item_name}")
#------------------------------------------------------------------------ Separating the name from the price ----------------------------------
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
                    msg = self.bank_account.spend_lumens(cost)
                    return msg["message"]
                else:
                    return  f"Transection Failed ,💸 Not enough lumens to purchase {item_name}"
#----------------------------------------------------------------------------trading badges----------------------------------------------------
        for key, value in self.trade_items.items():
            trade_amount = int(value)
            trade_item = str(key).strip().lower()
            logging.debug(f'items for trand in polymart: {self.trade_items}')
            logging.debug(f"Item to be traded {item_name}")

            cached_badges = cache.get("badges")
            if item_name.title() not in cached_badges:
                return  f"Transection Failed , you don't have `{item_name.title()}` yet."
            if item_name == trade_item:
                logging.debug("Item found")
                if dashboard.remove_badge(item_name.title()):
                    self.bank_account.wallet = trade_amount
                    # self.remove_traded_badge(item_name)
                    badges = dashboard.get_all_badges()
                    cache.set("badges", badges)
                    return f"Transaction Complete Traded {item_name} for {trade_amount}"
                return f"An error occurred. Please try again."
#-------------------------------------------------------------------------If loop finishes and no item was found-------------------------------
        return "❌ Item not found in PolyMart."

class SpinningLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 80, QFont.Bold))
        self.angle = 0
#----------------------------------------------------------------Timer to simulate 3D spin-----------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.spin)
        self.timer.start(30)  # Spin speed
#=====================================================================Class Methods============================================================
    def spin(self):
        self.angle += 2
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

#---------------------------------------------------------------------Create radial gradient (white to purple)---------------------------------
        gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()/1.5)
        gradient.setColorAt(0, QColor("white"))
        gradient.setColorAt(1, QColor(128, 0, 128))  # Purple
        painter.fillRect(self.rect(), QBrush(gradient))

#-----------------------------------------------------------------------Simulate 3D spin using scaling on the x-axis---------------------------
        transform = QTransform()
        scale = math.cos(math.radians(self.angle))
        transform.translate(self.width()/2, self.height()/2)
        transform.scale(scale, 1)
        transform.translate(-self.width()/2, -self.height()/2)
        painter.setTransform(transform)

#------------------------------------------------------------------------------Draw the text---------------------------------------------------
        painter.setPen(Qt.black)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
#==============================================================================================================================================
#**********************************************************************************************************************************************
#=====================================================================Dashboard UI=============================================================
class MainWindow(QMainWindow):
#-----------------------------------------------------------------------Data Fields------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex Dashboard")
#============================================================================
        self.trigger_file = Path(__file__).parent / "update.txt"
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(str(self.trigger_file))
        self.watcher.fileChanged.connect(self.check_new_cp)

        self.trigger_file_2 = Path(__file__).parent / "update_db_ui.txt"
        self.watcher_2 = QFileSystemWatcher()
        self.watcher_2.addPath(str(self.trigger_file_2))
        self.watcher_2.fileChanged.connect(self.update_wrapper)
#================================================================
        self.user = UserIfo()
        self.bank = AutodidexBank(self.user) 
        self.market = PolyMart(self.bank) 
        self.name_null_value: Optional[str] = None
        self.user_present = dashboard.get_user_state()

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
        # self.trade_icon = Path(__file__).parent / "Icons/icons8-trade-64.png"
        # self.light_icon = Path(__file__).parent / "Icons/icons8-light-64.png"
        # self.dark_icon = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        # self.thm_pref = Path(__file__).parent / "v tab files/dashboard_config.json"

        # self.theme_state: Optional[str] = None
        # self.dark_mode: Optional[str] = None
        # self.light_mode: Optional[str] = None

        self.light_mode: Optional[str] = None
        self.dark_mode: Optional[str] = None
        self.neutral_mode: Optional[str] = None
        self.mode = cache.get("theme") or themes.get_chosen_theme()

        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.n_mode = Path(__file__).parent / "Icons/icons8-day-and-night-50.png"

        # self.thm_btn = QPushButton("")
        # self.thm_btn.setIcon(QIcon(str(self.d_mode)))
        # self.thm_btn.setIconSize(QSize(30, 30))
        # self.thm_btn.clicked.connect(self.theme)

        self.theme_toggle = QPushButton("")
        self.theme_toggle.setIcon(QIcon(str(self.l_mode)))
        self.badge_list = QListWidget()
        self.container = QWidget()
        self.subject_combo = QComboBox()

        self.init_wrapper()
#===============================================================================Class Methods==================================================
    def setup_ui(self):
        """"Struture the UI"""
        layout = QVBoxLayout()
#---------------------------------------------------------------------------Header Section with Toggle-----------------------------------------
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

        self.l_icon = Path(__file__).parent / "Icons/icons8-bill-64.png" 
        self.level_label = QLabel(
                f'<img src="{self.l_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.user.level}</span>'
            )
        self.level_label.setToolTip("overall level")

        self.w_icon = Path(__file__).parent / "Icons/icons8-wallet-64.png"
        self.wallet_label = QLabel(
                f'<img src="{self.w_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.wallet} Lumens</span>'
            )
        self.wallet_label.setToolTip("Wallet")

        self.xp_icon = Path(__file__).parent / "Icons/icons8-points-64.png"
        self.xp_label = QLabel(
                f'<img src="{self.xp_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.xpPoints}</span>'
                            )
        self.xp_label.setToolTip("XP points")

        layout.addLayout(label_layout)
        layout.addLayout(header_layout)
        layout.addWidget(self.name_label)   
        layout.addWidget(self.level_label)
        layout.addWidget(self.wallet_label)
        layout.addWidget(self.xp_label)
#----------------------------------------------------------------------Subject XP System-------------------------------------------------------
        xp_layout = QHBoxLayout()
        self.subject_combo.currentIndexChanged.connect(self.display_badges)
        
        self.subject_combo.addItems(self.add_subject())

        subjects_label = QLabel()
        self.s_icon = Path(__file__).parent / "Icons/icons8-calibre-64.png"
        subjects_label.setText(f'<img src="{str(self.s_icon)}" width="40" height="40">')
        subjects_label.setToolTip("Subjects")

        xp_layout.addWidget(subjects_label)
        xp_layout.addWidget(self.subject_combo)
        layout.addLayout(xp_layout)
#-------------------------------------------------------------------------Badge Display--------------------------------------------------------
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
                if self.user.name:
                    dashboard.update_is_active_state(1)
                    dashboard.starter_badge()
            else:
                self.setup_ui()
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
                state = dashboard.create_new_user(name)
                self.user_present = state
                logging.debug("User logged in as: %s", self.user.name)

#------------------------------------------------------------------replacing the window with the actual UI-------------------------------------
                self.setup_ui()
            except ValueError as e:
                logging.debug("Name validation failed: %s", e)
                QMessageBox.warning(self, "Invalid Name", str(e))
        else:
            QMessageBox.warning(self, "Missing Name", "Please enter a name to continue.")    

    def buy_item(self):
        """"Calls the method purchasing or trades from PolyMart"""
        item = self.store_combo.currentText()
        logging.debug(f'The current item is {item}')

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
#----------------------------------------------------------------------add back open back up file feature--------------------------------------
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
       
        badges_list = cache.get("cp_badges")
        logging.debug(f"The badges: {badges_list}")

        self.badge_list.clear()
        selected_item = self.subject_combo.itemText(index)

        subject_badges = badges_list[selected_item]
    
        self.badge_list.addItems(set(subject_badges))
        
    def add_subject(self):
        """Load subjects from db"""
       
        subjects_list = sorted(self.user.initialize_subjects())
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
    
    
    # def load_themes(self):
    #     theme_files = {
    #         "light_mode": Path(__file__).parent / "themes files/light_mode.txt",
    #         "dark_mode": Path(__file__).parent / "themes files/dark_mode.txt"
    #     }

    #     for name, path in theme_files.items():
    #         with open(path, "r") as f:
    #             setattr(self, name, f.read())

    def load_themes(self):
        """loads the themes, and sets them to their data fields"""
        # light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"
        # dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"
        # neutral_mode_file = Path(__file__).parent / "themes files/neutral_mode.txt"
#------------------------------------------------------------------------load light mode-----------------------------------------
        # with open(light_mode_file, "r") as f:
        #     light_mode = f.read()
        if cache.get("light"):
            self.light_mode = cache.get("light")
        else:
            self.light_mode = themes.get_theme_mode("light")
        cache.set("light", self.light_mode)

#------------------------------------------------------------------load dark mode------------------------------------------------
        # with open(dark_mode_file, "r") as f:
        #     dark_mode = f.read()
        if cache.get("dark"):
            self.dark_mode = cache.get("dark")
        else:
            self.dark_mode = themes.get_theme_mode("dark")
        cache.set("dark", self.dark_mode)

        # with open(neutral_mode_file, "r") as f:
        #     neutral_mode = f.read()
        if cache.get("neutral"):
            self.neutral_mode = cache.get("neutral")
        self.neutral_mode = themes.get_theme_mode("neutral")
        cache.set("neutral", self.neutral_mode)



                
    def toggle_theme(self):
        """Switches between themes"""

        # if self.theme_state == "light":
        #     stylesheet_file = Path(__file__).parent / "themes files/neutral_mode.txt"
        #     self.theme_state = "dark"
        #     self.theme_toggle.setText("")
        #     self.theme_toggle.setIcon(QIcon(str(self.light_icon)))
        # else:
        #     stylesheet_file = Path(__file__).parent / "themes files/light_mode.txt"
        #     self.theme_state = "light"
        #     self.theme_toggle.setText("")
        #     self.theme_toggle.setIcon(QIcon(str(self.dark_icon)))
        # self.theme_toggle.setIconSize(QSize(30, 30))

        # with open(stylesheet_file, "r") as f:
        #     stylesheet = f.read()
        if self.mode == "light":
            self.theme_toggle.setIcon(QIcon(str(self.d_mode)))
            self.setStyleSheet(self.dark_mode)
            self.mode = "dark"
            cache.set("theme", "dark")
        elif self.mode == "dark":
            self.theme_toggle.setIcon(QIcon(str(self.n_mode)))
            self.setStyleSheet(self.neutral_mode)
            self.mode = "neutral"
            cache.set("theme","neutral")
        elif self.mode == "neutral":
            self.theme_toggle.setIcon(QIcon(str(self.l_mode)))
            self.setStyleSheet(self.light_mode)
            self.mode = "light"
            cache.set("theme", "light")
            
    
    def load_thm_pref(self):
        "loads user preferred theme"
#         try:
#             with open(self.thm_pref, "r") as f:
#                 data = json.load(f)
#                 self.theme_state = data["mode"]
#         except (FileNotFoundError, json.decoder.JSONDecodeError):
# #--------------------------------------------------------------------------------set to defaulf------------------------------------------------
#             self.theme_state = "dark"
        
#         if self.theme_state == "dark":
#             self.setStyleSheet(self.dark_mode)
#         elif self.theme_state == "light":
#             self.setStyleSheet(self.light_mode)
#         return
        self.toggle_theme()
            
    
    def thm_wrapper(self):
        self.load_themes()
        self.toggle_theme()

    def check_new_cp(self):
        """Checks for new subjects added"""
        # if self.user_present == True:
        #remove duplicates from list
        subjects = set(cp_tracker.get_cerebral_pursuits())
        #convert set into list
        subjects = list(subjects)
        self.subject_combo.clear()
        self.subject_combo.addItems(subjects)
    
    def update_wrapper(self):
        self.bank.earn_subject_xp()
        # level = self.user.load_overall_level()
        # xp_points = dashboard.get_total_xp()
        # wallet = dashboard.get_lumens_amount()
        self.level_label.setText(
                f'<img src="{self.l_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.user.level}</span>'
            )
        self.xp_label.setText(
                f'<img src="{self.xp_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.xpPoints}</span>'
                            )
        self.wallet_label.setText(
                f'<img src="{self.w_icon.as_posix()}" width="40" height="40">'
                f'<span style="font-size: 20px;"> ⁚ {self.bank.wallet} Lumens</span>'
            )
    
    def init_wrapper(self):
        badges = dashboard.get_all_badges()
        cp_with_badges = dashboard.get_cp_with_badges()
        cache.set("cp_badges", cp_with_badges)
        cache.set("badges", badges)
        self.on_load()
        if self.user_present == True:
            self.setup_ui()
        self.thm_wrapper()
        self.bank.earn_subject_xp()
        self.market.load_store_items()
        
#===========================================================================Run application====================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 600)
    window.show()
    sys.exit(app.exec())
