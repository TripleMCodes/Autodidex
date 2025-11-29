#===============================================================Imports=====================================================================
#*******************************************************************************************************************************************
from PySide6.QtCore import Qt,QTimer,QRegularExpression
from PySide6.QtWidgets import (
                                QApplication,
                                QWidget,QPushButton,
                                QVBoxLayout, QHBoxLayout,
                                QTextEdit, QPushButton,
                                QFileDialog,QMessageBox,
                                QLabel,QComboBox,
                                QLineEdit,QTextBrowser, QSplitter
                                )
from PySide6.QtGui import QFont,QIcon
from pathlib import Path
from markdown import markdown
import shelve
import nltk
from nltk.corpus import wordnet
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
import sys
import json
from typing import Optional
from spellchecker import SpellChecker
from PySide6.QtGui import QTextCharFormat, QTextCursor, QColor
from lyric_n_summarization_ui import LyricsSummarizationUi
from themes_db import Themes
from autodidex_cache import DictionaryCache

cache = DictionaryCache()
themes = Themes()

# Download WordNet if not already downloaded
nltk.download('wordnet')

CONFIG_FILE = Path(__file__).parent / "noteworthy files/config.json"  # File to store user preferences


class SpellCheckTextEdit(QTextEdit):
    def __init__(self, spell_checker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spell_checker = spell_checker

    def highlight_misspelled_words(self):
        self.blockSignals(True)  # Prevent recursion

        cursor = self.textCursor()
        text = self.toPlainText()
        words = text.split()
        misspelled = self.spell_checker.unknown(words)

        # Remove previous formatting
        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(fmt)
        cursor.clearSelection()
        cursor.endEditBlock()

        # Highlight misspelled words
        for word in misspelled:
            fmt = QTextCharFormat()
            fmt.setUnderlineColor(QColor("red"))
            fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
            pattern = r'\b{}\b'.format(word)
            regex = QRegularExpression(pattern)
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart()
                end = match.capturedEnd()
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(fmt)

        self.blockSignals(False)  # Re-enable signals

   
class NoteWorthy(QWidget):
    def __init__(self):
        super().__init__()

       
#===============================================================Main Layout=====================================================================
        self.main_layout = QHBoxLayout(self)
        self.setGeometry(100, 100, 600, 400)
        # self.setMinimumHeight(600)  
        self.setWindowTitle("Note Worthy")  
        win_icon = Path(__file__).parent / "Icons/icons8-notebook-64.png"
        self.setWindowIcon(QIcon(str(win_icon)))

#===============================================================================================================================================
#======================================================splitter=================================================================================
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setMinimumSize(QSize(500, 500))
        # self.splitter.setSizes([700, 900])
#===============================================================================================================================================
#================================================================Text box=======================================================================
        self.spell = SpellChecker()
        self.text_edit = SpellCheckTextEdit(self.spell)
        self.text_edit.textChanged.connect(self.update_word_count)
        self.text_edit.textChanged.connect(self._md_formatter)
        self.text_edit.textChanged.connect(self._restart_timer)
        self.text_edit.setPlaceholderText("Type your notes here...")
        self.splitter.addWidget(self.text_edit)

        # self.preview = QTextBrowser()
        # self.splitter.addWidget(self.preview)      
        self.md_mode = False

        
        
        self.previous_text = True

        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self._autosave)

        self.text_edit.textChanged.connect(self.text_edit.highlight_misspelled_words)
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.contextMenuEvent)
#===============================================================================================================================================
#================================================================Sidebar Widget=================================================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)  # Default width
        self.sidebar.setStyleSheet("")
#===============================================================================================================================================
##===================================================================word count label===========================================================
        self.wc_icon = Path(__file__).parent / "Icons/icons8-word-file-64.png"
        self.word_count_label = QLabel(
            f'<img src="{str(self.wc_icon)}" width="40" height="40">'
            f'<span style="font-size: 20px;"> ⁚ 0</span>', self)
        self.word_count_label.setToolTip("word count")
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.splitter)   
        self.v_layout.addWidget(self.word_count_label)
#===============================================================================================================================================
#===============================================================Dictionary======================================================================
        self.word_input = QLineEdit(self)
        self.word_input.setPlaceholderText("Enter a word for definition...")

        enter_icon = Path(__file__).parent / "Icons/icons8-enter-64.png"
        self.search_button = QPushButton("", self)
        self.search_button.setIcon(QIcon(str(enter_icon)))
        self.search_button.setIconSize(QSize(30, 30))
        self.search_button.clicked.connect(self.get_definition)

        self.definition_output = QLabel(self)
        self.definition_output.setWordWrap(True)
        self.definition_output.setMinimumSize(14, 18)

        self.v_layout.addWidget(self.word_input)
        self.v_layout.addWidget(self.search_button)
        self.v_layout.addWidget(self.definition_output)
#===============================================================================================================================================
#============================================================Sidebar Layout (Vertical)==========================================================
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
#===============================================================================================================================================
#===========================================================Toggle Button (Collapses Sidebar)===================================================
        self.menu_icon = Path(__file__).parent / "Icons/icons8-menu-48.png"
        self.x_icon = Path(__file__).parent / "Icons/icons8-close-64.png"
        self.toggle_btn = QPushButton("")
        self.toggle_btn.setIcon(QIcon(str(self.x_icon)))
        self.toggle_btn.setIconSize(QSize(30, 30))

        self.toggle_btn.clicked.connect(self._toggle_sidebar)
#==============================================================================================================================================
#====================================================================Sidebar Buttons============================================================
        self.md_icon = Path(__file__).parent / "Icons/icons8-markdown-64.png"
        self.md_btn = QPushButton("")
        self.md_btn.setIcon(QIcon(str(self.md_icon)))
        self.md_btn.setIconSize(QSize(30, 30))
        self.md_btn.setToolTip("markdown")
        self.md_btn.clicked.connect(self._add_browser)
        
        copy_icon = Path(__file__).parent / "Icons/icons8-copy-64.png"
        self.copy_button = QPushButton("")
        self.copy_button.setIcon(QIcon(str(copy_icon)))
        self.copy_button.setIconSize(QSize(30, 30))
        self.copy_button.setToolTip("copy")
        self.copy_button.clicked.connect(self.text_edit.copy)

        cut_icon = Path(__file__).parent / "Icons/icons8-cut-48.png"
        self.cut_button = QPushButton("")
        self.cut_button.setIcon(QIcon(str(cut_icon))) 
        self.cut_button.setIconSize(QSize(30, 30))  
        self.cut_button.setToolTip("cut")  
        self.cut_button.clicked.connect(self.text_edit.cut)

        paste_icon = Path(__file__).parent / "Icons/icons8-paste-64.png"
        self.paste_button = QPushButton("")
        self.paste_button.setIcon(QIcon(str(paste_icon)))
        self.paste_button.setIconSize(QSize(30, 30))
        self.paste_button.setToolTip("paste")
        self.paste_button.clicked.connect(self.text_edit.paste)

        undo_icon = Path(__file__).parent / "Icons/icons8-undo-64.png"
        self.undo_button = QPushButton("")
        self.undo_button.setIcon(QIcon(str(undo_icon)))
        self.undo_button.setIconSize(QSize(30,30))
        self.undo_button.setToolTip("undo")
        self.undo_button.clicked.connect(self.text_edit.undo)
        
        redo_icon = Path(__file__).parent / "Icons/icons8-redo-64.png"
        self.redo_button = QPushButton("")
        self.redo_button.setIcon(QIcon(str(redo_icon)))
        self.redo_button.setIconSize(QSize(30, 30))
        self.redo_button.setToolTip("redo")
        self.redo_button.clicked.connect(self.launch_lyrical_lab)

        clear_icon = Path(__file__).parent / "Icons/icons8-clear-64.png"
        self.clear_button = QPushButton("")
        self.clear_button.setIcon(QIcon(str(clear_icon)))
        self.clear_button.setIconSize(QSize(30, 30))
        self.clear_button.setToolTip("clear")
        self.clear_button.clicked.connect(self.text_edit.clear)

        save_icon = Path(__file__).parent / "Icons/icons8-save-64.png"
        self.save_button = QPushButton("")
        self.save_button.setIcon(QIcon(str(save_icon)))
        self.save_button.setIconSize(QSize(30, 30))
        self.save_button.setToolTip("save")
        self.save_button.clicked.connect(self.save_file)
        
        exit_icon = Path(__file__).parent / "Icons/icons8-exit-sign-64.png"
        self.exit = QPushButton("")
        self.exit.setIcon(QIcon(str(exit_icon)))
        self.exit.setIconSize(QSize(30, 30))
        self.exit.setToolTip("exit")
        self.exit.clicked.connect(self.exit_button)

        files_icon = Path(__file__).parent / "Icons/icons8-new-document-48.png"
        self.file = QPushButton("")
        self.file.setIcon(QIcon(str(files_icon)))
        self.file.setIconSize(QSize(30, 30))
        self.file.setToolTip("files")
        self.file.clicked.connect(self.open_file)

        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.n_mode = Path(__file__).parent / "Icons/icons8-day-and-night-50.png"

        self.dark_mode : Optional[None] = str
        self.light_mode : Optional[None] = str
        self.neutral_mode : Optional[None] = str

        self.theme_btn = QPushButton("")
        self.theme_btn.setIcon(QIcon(str(self.d_mode)))
        self.theme_btn.setIconSize(QSize(30, 30))
        self.theme_btn.clicked.connect(self.theme)

        self.font_size_box = QComboBox(self)
        self.font_size_box.addItems(["10", "12", "14", "16", "18", "20", "22", "24", "26"])
        self.font_size_box.currentIndexChanged.connect(self._change_font_size)
#===============================================================================================================================================
#============================================================List of side bar buttons===========================================================
        buttons = [
                    self.file,
                    self.theme_btn,
                    self.font_size_box,
                    self.copy_button,
                    self.cut_button,
                    self.paste_button,
                    self.redo_button,
                    self.undo_button,
                    self.clear_button,
                    self.save_button,
                    self.md_btn

                 ]
#===============================================================================================================================================
#================================================================style Buttons==================================================================
        for btn in buttons:
            # btn.setStyleSheet("color: white; background: #444; border: none; padding: 10px;")
            self.sidebar_layout.addWidget(btn)
#===============================================================================================================================================
#================================================================Add Widgets to Main Layout=====================================================
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(self.v_layout)
       
        self.setLayout(self.main_layout)
#===============================================================================================================================================
#==============================================Load user preference (default: light mode)=======================================================
        # Load user preferences
        # self.mode, self.font_size = self._load_preferences()
        # self. apply_theme()
        # self._set_font_size(self.font_size)

        # self._get_last_written()
        self.init_wrapper()
#===============================================================================================================================================
#===================================================================Funtions====================================================================
    def load_themes(self):
        """Loads the themes, and sets them to their data fields"""
        
        if cache.get("light"):
            self.light_mode = cache.get("light")
        self.light_mode = themes.get_theme_mode("light")
        cache.set("light", self.light_mode)

        if cache.get("dark"):
            self.dark_mode = cache.get("dark")
        self.dark_mode = themes.get_theme_mode("dark")
        cache.set("dark", self.dark_mode)

        if cache.get("neutral"):
            self.neutral_mode = cache.get("neutral")
        self.neutral_mode = themes.get_theme_mode("neutral")
        cache.set("neutral", self.neutral_mode)

    def _toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setText("")
            self.toggle_btn.setIcon(QIcon(str(self.menu_icon)))
        else:
            self.sidebar.show()
            self.toggle_btn.setText("")
            self.toggle_btn.setIcon(QIcon(str(self.x_icon)))


    def paste(self):            
        self.text_edit.paste()

    def save_file(self):
        #Prompts the user for filename and location
        file_name, _ = QFileDialog.getSaveFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)") 

        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)")

        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.text_edit.setText(file.read())

    def about_noteWorthy(self):
         ret = QMessageBox.information(self,"About Note worthy",
                                      "Created by Connor Connorson",
                                      QMessageBox.Ok
                                      )
    
    def get_definition(self):
        word = self.word_input.text().strip().lower()  # Ensure lowercase
        if not word:
            self.definition_output.setText("⚠️ Please enter a word.")
            return

        synsets = wordnet.synsets(word)
        if synsets:
            definitions = '\n'.join([f"• {s.definition()}" for s in synsets[:3]])  # Add bullet points
            self.definition_output.setText(definitions)
        else:
            self.definition_output.setText("❌ No definition found.")
       

    def update_word_count(self):
        text = self.text_edit.toPlainText()
        words_num = len(text.split()) 
        self.word_count_label.setText( 
            f'<img src="{str(self.wc_icon)}" width="40" height="40">'
            f'<span style="font-size: 20px;"> ⁚ {str(words_num)}</span>')
        

    def theme(self):
        if self.mode == "light":
            self.sidebar.setStyleSheet(self.dark_mode)
            self.setStyleSheet(self.dark_mode)
            self.theme_btn.setIcon(QIcon(str(self.l_mode)))
            self.mode = "dark"
            cache.set("theme", "dark")
        elif self.mode == "dark":
            self.sidebar.setStyleSheet(self.neutral_mode)
            self.setStyleSheet(self.neutral_mode)
            self.theme_btn.setIcon(QIcon(str(self.n_mode)))
            self.mode = "neutral"
            cache.set("theme", "neutral")
        elif self.mode == "neutral":
            self.sidebar.setStyleSheet(self.light_mode)
            self.theme_btn.setIcon(QIcon(str(self.d_mode)))
            self.setStyleSheet(self.light_mode)
            self.mode = "light"
            cache.set("theme", "light")

    def apply_theme(self):
        # if self.mode:
        #     self._dark_mode()
        # else:
        #     self._light_mode()
        pass

    def _dark_mode(self):
        """Apply dark mode styles"""
        dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"

        with open(dark_mode_file, "r") as f:
            dark_mode = f.read()
        self.setStyleSheet(dark_mode)
        self.theme_btn.setText("")
        self.theme_btn.setIcon(QIcon(str(self.l_mode)))
        

    def _light_mode(self):
        """Apply light mode styles."""
        light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"

        with open(light_mode_file, "r") as f:
            light_mode = f.read()

        self.setStyleSheet(light_mode)
        self.theme_btn.setText("")
        self.theme_btn.setIcon(QIcon(str(self.d_mode)))
        

    def _change_font_size(self):
        """Change the font size when the user selects a new size."""
        selected_size = int(self.font_size_box.currentText())
        self._set_font_size(selected_size)
        print(f"changing font size to {selected_size}")
        self._save_preferences()  # Save font size selection
    
    def _set_font_size(self, size):
        """Apply the selected font size."""
        font = QFont("Arial", size)
        self.text_edit.setFont(font)

        count = self.splitter.count()
        last_widget = self.splitter.widget(count - 1)
        last_widget.setFont(font)
        self.font_size_box.setCurrentText(str(size))  # Ensure dropdown reflects the selection
        
    
    def _save_preferences(self):
        """Save user preferences (theme & font size) to a JSON file."""
        data = {
            "dark_mode": self.mode,
            "font_size": self.font_size_box.currentText()
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file)

    def _load_preferences(self):
        """Load user preferences (theme & font size) from a JSON file."""
        if cache.get("theme"):
            selected_theme = cache.get("theme")
        else:
            selected_theme = themes.get_chosen_theme()

        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                return selected_theme, int(data.get("font_size", 14))  # Default: Light mode, Font size 14
        except (FileNotFoundError, json.JSONDecodeError):
            # return False, 14  # Default values if file is missing or corrupted
            return
        
    def _add_browser(self):
        count = self.splitter.count()
        if count == 1:
            new_widget = QTextEdit()
            new_widget.setReadOnly(True)
            self.splitter.addWidget(new_widget)
            count = self.splitter.count()
            self.md_mode = True
            self._md_formatter()
            self._md_formatter()
            self._change_font_size()
        else:
            last_widget = self.splitter.widget(count - 1)
            last_widget.setParent(None)
            self.md_mode = False     
   
    def _md_formatter(self):
        if self.md_mode:
            md_text = self.text_edit.toPlainText()
            html = markdown(md_text)
            # print(html)
            count = self.splitter.count()
            last_widget = self.splitter.widget(count - 1)
            last_widget.setText(html)
        
        
    def _restart_timer(self):
        self.typing_timer.start(1000)  # Waits 10 seconds after last keypress

    def _autosave(self):
        current_text = self.text_edit.toPlainText()
        if current_text != getattr(self, "last_saved_text",""):
            file = Path(__file__).parent / "noteworthy files/temp.txt"
            with open(file, "w", encoding="utf-8") as f:
                f.write(current_text)
            self.last_saved_text = current_text

    def _get_last_written(self):
        file = Path(__file__).parent / "noteworthy files/temp.txt"
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            self.text_edit.setText(text)
            self.previous_text = False
        except FileNotFoundError:
            return
    
    def launch_lyrical_lab(self):
        self.lyrical_window = LyricsSummarizationUi()
        self.lyrical_window.show()
        # self.destroy()
    
    def init_wrapper(self):
        self.mode, self.font_size = self._load_preferences()
        self.load_themes()
        self.theme()
        # self.apply_theme()
        self._set_font_size(self.font_size)
        self._get_last_written()

    def exit_button(self):
        self.destroy()
        sys.exit()

#===============================================================================================================================================
    # def contextMenuEvent(self, event):
    #     cursor = self.text_edit.cursorForPosition(event.pos())
    #     pos = cursor.position()
    #     for word, positions in self.text_edit.misspelled_positions.items():
    #         for start, end in positions:
    #             if start <= pos <= end:
    #                 # Show suggestions
    #                 suggestions = list(self.spell.candidates(word))
    #                 menu = self.text_edit.createStandardContextMenu()
    #                 if suggestions:
    #                     for suggestion in suggestions:
    #                         action = menu.addAction(f"Replace with '{suggestion}'")
    #                         action.triggered.connect(lambda checked, s=suggestion, st=start, en=end: self.replace_word(st, en, s))
    #                 menu.exec(event.globalPos())
    #                 return
    #     # Default menu if not on a misspelled word
    #     self.text_edit.createStandardContextMenu().exec(event.globalPos())

    # def replace_word(self, start, end, new_word):
    #     cursor = self.text_edit.textCursor()
    #     cursor.setPosition(start)
    #     cursor.setPosition(end, QTextCursor.KeepAnchor)
    #     cursor.insertText(new_word)
#===============================================================================================================================================
#===========================================================Run Application====================================================================
if __name__ == "__main__":
    app = QApplication([])
    window = NoteWorthy()
    window.show()
    app.exec()