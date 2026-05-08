Welcome to your personal growth adventure, Autodidex! This application is designed to help you track your learning progress, reward your efforts, and keep you motivated on your journey to becoming a "self-learner." Think of it as your personal quest log and reward system rolled into one.

Here's how it all works:

### Your Profile: Found on the Dashboard

This is where your journey begins and all your personal progress is stored.

* **Your Name:** When you first start, you'll set up your name. Make sure to capitalize the first letter – it's a small detail, but it makes your profile feel official!
* **Overall Level:** This is your grand progress indicator. As you learn more and gain experience points across all your subjects, your overall level will increase. Every **500 XP** you accumulate will grant you a new overall level. This is a big one, so keep an eye on it!
* **Your Subjects:** This is the core of your learning.
    * **Tracking Your Subjects:** The game integrates with a "Habit Tracker" (Cerebral Pursuit Tracker) to identify the subjects you're focusing on. When you load up the game, it automatically pulls in your subjects from a "last saved" list.
    * **Subject Levels & XP:** For each subject, you'll have a specific level and experience points (XP). As you put in work on a subject, you'll earn XP towards that specific subject's level.
    * **New Subjects:** If you add new subjects to your Habit Tracker, don't worry! The game will automatically recognize them and set them up with their own level and XP counter, starting from zero.

### Earning Rewards: The Autodidex Bank & Badges

This is where your hard work pays off!

* **Your Wallet (Lumens):** As you progress in your subjects, you'll earn "Lumens," which are the in-game currency.
    * **How to Earn Lumens:** Every time a subject levels up by a significant amount (specifically, for every **200 XP** you earn in a subject, it gains a level), you'll be rewarded with **10 Lumens!**
    * **Spending Lumens:** You can use your Lumens to purchase items in the "PolyMart" (more on that below!).
* **XP Points (Overall & Subject Specific):**
    * **Subject XP:** When you mark tasks as complete in your Habit Tracker for a specific subject, you'll earn XP for that subject. The more you do, the more XP you get! Each completed task or "check" in your habit tracker translates to **20 XP** for that subject.
    * **Total XP:** All the XP you earn across your individual subjects contributes to your grand "Total XP" amount. This total XP is what determines your "Overall Level."
* **Badges:** These are special achievements you unlock as you progress, showcasing your dedication and mastery!
    * **Automatic Awards:** The game constantly checks your progress to see if you've earned any new badges.
    * **Badge Types:**
        * **Overall Level Badges:**
            * "🎖️ Level 5 Unlocked"
            * "💎 Every Tenth Tier Counts" (awarded for every 10th overall level you achieve)
            * "🖤 Every Ten K Counts" (awarded when your total XP reaches multiples of 10,000!)
        * **Subject-Specific Badges:**
            * "🏆 1K Subject XP Master" (awarded when a subject reaches multiples of 1,000 XP)
            * "🎯 Every Ten Counts" (awarded for every 10th level a specific subject achieves)
    * **Your Badge Collection:** All your earned badges are stored in your profile for you to admire!

### The PolyMart: Your In-Game Store

This is where you can use your hard-earned Lumens and even trade in some of your badges!

* **Buying Items:** You can browse the PolyMart for items that can be purchased with your Lumens. When you select an item, the game checks if you have enough Lumens in your wallet. If you do, the Lumens are deducted, and you get your item!
* **Trading Badges:** Some special items in the PolyMart might require you to *trade in* one of your hard-earned badges for Lumens. If you choose to trade a badge, it will be removed from your collection, and you'll receive the specified amount of Lumens. It's a way to convert certain achievements into more Lumens if you need them!

### How Progress is Saved and Updated:

The game diligently saves your progress so you never lose your hard-earned achievements:

* **Automatic Saving:** Your Lumens, XP, subject levels, and earned badges are all saved automatically in various files (mostly JSON files) within the application's data folders.
* **Daily Updates:** The game checks the current date against the last time it updated your progress. If it's a new day, it will process any new progress you've made (from your Habit Tracker) and update your XP, levels, Lumens, and check for new badges. This ensures your rewards are always up-to-date.

In essence, this game encourages you to set and track your learning goals. The more consistent you are with your studies and habits (as tracked in the connected Habit Tracker), the more XP and Lumens you'll earn, the higher your levels will climb, and the more prestigious badges you'll collect, making your learning journey a rewarding and motivating experience!








/* === GLOBAL BASE === */
* {
    font-family: "Fira Sans", "Segoe UI", sans-serif;
    color: #E8E3FF;
}

/* === MAIN BACKGROUND === */
QWidget {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1A152E,
        stop:1 #2C2444
    );
}
QHBoxLayout#mainframe {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1A152E,
        stop:1 #2C2444
    );
    font-size: 120px;
}

/* === LABELS === */
QLabel {
    color: #DAD2FF;
    font-size:14px;
}
QLabel#onloadlabel {
    font-size: 80px;
    font-family:"Arial";
    border-radius: 3px;
    color: #FFFFFF;
}
QLabel#dblabel {
    font-size: 50px;
    color:#D1BCFF;
    font-family:"Arial";
}

/* === BUTTONS === */
QPushButton {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #4C3C70,
        stop:1 #6A54A3
    );
    border: 1px solid #7C69BD;
    border-radius: 10px;
    padding: 8px 16px;
    color: #E8E3FF;
    font-weight: bold;
    font-size:14px;
}
QPushButton:hover {
    background-color: #5C4A89;
    border: 1px solid #9A7EF2;
}
QPushButton:pressed {
    background-color: #3F2D66;
    border: 1px solid #A88CF5;
}

/* === LINE EDITS === */
QLineEdit {
    background-color: #2B2440;
    border: 1px solid #7F67C9;
    border-radius: 6px;
    padding: 6px;
    color: #E8E3FF;
}
QLineEdit:focus {
    border: 1px solid #BFA6FF;
    background-color: #362E52;
}

/* === COMBOBOX === */
QComboBox {
    background-color: #2E2646;
    border: 1px solid #856FD4;
    border-radius: 6px;
    padding: 6px;
    color: #E8E3FF;
}
QComboBox:hover {
    border-color: #A88CF5;
}
QComboBox QAbstractItemView {
    background-color: #3A2F57;
    border: 1px solid #967BE3;
    selection-background-color: #5A47A0;
    color: #E8E3FF;
}

/* === CHECKBOXES === */
QCheckBox {
    color: #DAD2FF;
    padding: 4px;
}
QCheckBox::indicator {
    border: 1px solid #9F87DD;
    width: 16px;
    height: 16px;
    background-color: #3A2F57;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #6F54D8;
    border: 1px solid #BFA6FF;
}

/* === SCROLLBARS === */
QScrollBar:vertical {
    background: #1E1B2E;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #6F54D8;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #967BE3;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
}

/* === TOOLTIP === */
QToolTip {
    background-color: #4A3D70;
    color: #E8E3FF;
    border: 1px solid #BBA9F2;
    padding: 6px;
    border-radius: 4px;
}

/* === MENUBAR === */
QMenuBar {
    background-color: #2C2444;
    color: #E8E3FF;
}
QMenuBar::item:selected {
    background-color: #443865;
}
QMenu {
    background-color: #2E2646;
    color: #E8E3FF;
    border: 1px solid #7C69BD;
}
QMenu::item:selected {
    background-color: #5A47A0;
    color: #FFFFFF;
}

/* === GROUPBOX === */
QGroupBox {
    border: 1px solid #6F54D8;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px;
}
QGroupBox:title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #BFA6FF;
    font-weight: bold;
}

/* === TABS === */
QTabWidget::pane {
    border: 1px solid #4C3C70;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1A152E,
        stop:1 #2C2444
    );
    padding: 3px;
    border-radius: 3px;
}

QTabBar {
    background: transparent;
    alignment: left;
}

QTabBar::tab {
    background: rgba(60, 50, 95, 0.9);
    color: #BFA6FF;
    border: 1px solid #4C3C70;
    padding: 5px 10px;
    margin: 4px;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    min-width: 110px;
    text-align: left;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    transition: all 0.2s ease;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #6F54D8, stop:1 #BFA6FF);
    color: white;
    border: 2px solid #9D78FF;
    font-weight: bold;
    margin-left: 0px;
    z-index: 2;
}

QTabBar::tab:hover {
    background-color: rgba(111, 84, 216, 0.3);
    color: #E8E3FF;
    border: 1px solid #A88CF5;
}

QTabBar::tab:!selected {
    margin-top: 6px;
    opacity: 0.95;
}

QTabBar::tab {
    padding: 12px;
    margin: 4px;
    border: none;
    background: transparent;
}

QTabBar::tab:selected {
    background-color: rgba(111, 84, 216, 0.3);
    border-radius: 8px;
}

/* === TABLE & CALENDAR === */
/* Reuse the dark table + calendar styles from earlier QTableWidget and QCalendarWidget dark mode styles */

QTableWidget {
    background-color: #1E1B2E; /* deep twilight purple */
    border: 1px solid #4B3D74; /* muted violet border */
    gridline-color: #3B2F56; /* dark gridlines */
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 14px;
    color: #D8D3FF; /* soft lavender text */
    selection-background-color: #5D4D9A; /* dusky selection highlight */
    selection-color: #FFFFFF;
    alternate-background-color: #2B2640;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QHeaderView::section {
    background-color: #3C2F5C;
    color: #E1DBFF;
    font-weight: bold;
    border: none;
    padding: 6px;
    border-bottom: 1px solid #5A4A80;
    border-right: 1px solid #4B3D74;
}

QHeaderView::section:horizontal {
    border-top: 1px solid #4B3D74;
}

QHeaderView::section:vertical {
    border-left: 1px solid #4B3D74;
}

QTableCornerButton::section {
    background-color: #3C2F5C;
    border: none;
    border-top-left-radius: 4px;
}

QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #6F5AA7;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #6F5AA7;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTableWidget::item:hover {
    background-color: #4C3C70;
}

/* QCalendarWidget Dark Mode */
QCalendarWidget {
    background-color: #1E1B2E;
    border: 1px solid #4B3D74;
    border-radius: 10px;
    padding: 10px;
    font-family: "Segoe UI", "Arial";
    font-size: 14px;
    color: #E5DEFF;
    selection-background-color: #5D4D9A;
    selection-color: #FFFFFF;
}

/* Navigation bar (month/year header) */
QCalendarWidget QToolButton {
    background-color: #3C2F5C;
    color: #E5DEFF;
    border: none;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: bold;
}

QCalendarWidget QToolButton:hover {
    background-color: #504073;
}

/* Left/right arrows */
QCalendarWidget QToolButton::menu-indicator {
    image: none;
}

QCalendarWidget QAbstractItemView {
    selection-background-color: #5D4D9A;
    selection-color: #FFFFFF;
    background-color: #1E1B2E;
    alternate-background-color: #2B2640;
    gridline-color: #3B2F56;
}

/* Weekday headers (Mon, Tue, etc.) */
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: transparent;
}

QCalendarWidget QTableView {
    border: none;
}

/* Days of week */
QCalendarWidget QHeaderView::section {
    background-color: #2F2844;
    color: #D8D3FF;
    font-weight: 600;
    padding: 5px;
    border: none;
}

/* Selected day */
QCalendarWidget QAbstractItemView::item:selected {
    background-color: #7A68C1;
    color: #FFFFFF;
    border-radius: 4px;
}


