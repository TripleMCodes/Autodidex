import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QHBoxLayout,QSizePolicy,
    QComboBox, QRadioButton,QSplitter,QFileDialog,QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
import numpy as np
from lyrics_n_summarization import OpenRouterClient 
import sounddevice as sd
from scipy.io.wavfile import write
from typing import Optional
from pathlib import Path
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtGui import QTextCursor
import logging
from PySide6.QtGui import QIcon
from wordfinder import WordFinder
from lyrics_n_summarization import OpenRouterClient
from recorder import VoiceRecorder
import json
import pyphen
import pronouncing
from autodidex_cache import DictionaryCache
from themes_db import Themes

themes = Themes()
cache = DictionaryCache()

logging.basicConfig(level=logging.DEBUG)
logging.disable()

CONFIG_FILE = Path(__file__).parent / "noteworthy files/config.json"  # File to store user preferences

dic = pyphen.Pyphen(lang='en')

class RecorderThread(QThread):
    finished = Signal(str) #sends message when recording is done
    

    def __init__(self, duration=0, samplerate=44100, song="recording"):
        super().__init__()
        self.duration = duration
        self.samplerate = samplerate
        self.recording = []
        self.running = False
        self.song_name = song
        self.basepath = Path(__file__).parent
        self.count = 1

    def run(self):
        logging.debug(f"in run(), recording started")
        self.running = True
        with sd.InputStream(samplerate=self.samplerate, channels=1, callback=self.callback):
            while self.running:
                sd.sleep(100)
                logging.debug(f"in run(), recording started")

        filename = self.basepath / f"recording{self.count}.wav"
        audio_data = np.concatenate(self.recording, axis=0)
        write(filename, self.samplerate, audio_data)
        self.finished.emit(filename)
    
    def callback(self, indata, frames, time, status):
        logging.debug("callback invoked")
        if status:
            logging.debug(f"The status is {status}")
            self.recording.append(indata.copy())
        
    def stop(self):
        self.running = False
        self.count = self.count + 1
        logging.debug(f"Done recording, now in stop()")

class LyricsSummarizationUi(QWidget):
    def __init__(self):
        super().__init__()

        # --- Main Layout ---
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.search_mode = None #flag for lyric gen or FOS gen mode
        self.lyric_mode = "lyric mode"
        self.fos_mode = "fos mode"
        self.openning_app = True

        #recording class
        self.m_recorder = RecorderThread()

        #rhhymes and lexicon class
        self.rimes_n_lex = WordFinder(15, "music,poetry")

        #openclient classs
        self.gen_class = OpenRouterClient()

        # --- Sidebar Layout ---
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        # self.sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        self.sidebar_layout.setSpacing(5)  # Space between widgets

        # sidebar header label
        self.header_label = QLabel("Lyrics and FOS generation")
        self.sidebar_layout.addWidget(self.header_label, alignment=Qt.AlignHCenter)

        # Line Edit (Prompt Area)
        self.prompt_area = QLineEdit()
        self.prompt_area.setPlaceholderText("Enter prompt here")
        self.prompt_area.setFixedSize(300, 30)  # Proper size for a line edit
        self.sidebar_layout.addWidget(self.prompt_area)

        # Generate Button
        self.btn = QPushButton("Generate")
        self.btn.clicked.connect(self.generate)
        # self.btn.setFixedSize(150, 40)  # Fixed size for button
        self.sidebar_layout.addWidget(self.btn, alignment=Qt.AlignHCenter)
        self.sidebar_layout.addWidget(self.btn)

        # Generation options
        self.gen_layout = QHBoxLayout()
        self.sidebar_layout.addLayout(self.gen_layout)

        #lyric generation
        self.lyric_gen_mode = QRadioButton("Lyric gen mode")
        self.lyric_gen_mode.toggled.connect(self.update_search_mode)
        self.lyric_gen_layout = QVBoxLayout()
        self.lyric_gen_layout.setSpacing(5)
       
        self.genre_label = QLabel("Genres")
        self.lyric_gen_layout.addWidget(self.genre_label)
        self.genre_list = [
            "Pop",
            "Alt Pop",
            "Hip Hop",
            "Rap",
            "Trap",
            "Rock",
            "Rnb",
            "Punk",
            "Emo",
            "Indie",
            "Folk",
        ]
        self.genres = QComboBox()
        self.genres.addItems(self.genre_list)
        self.lyric_gen_layout.addWidget(self.genres)
        self.lyric_gen_layout.addWidget(self.lyric_gen_mode, alignment=Qt.AlignHCenter)       
        self.gen_layout.addLayout(self.lyric_gen_layout)

        #Figure of speech generation
        self.fos_gen_mode = QRadioButton("FOS gen mode")
        self.fos_gen_mode.toggled.connect(self.update_search_mode)
        self.fos_gen_layout = QVBoxLayout()

        self.fos_label = QLabel("Figures of Speech")
        self.fos_gen_layout.addWidget(self.fos_label)

        self.figure_of_speech_list = [
            "simile",
            "metaphor",
            "analogy",
            "Analogy",
            "Assonance",   
            "Consonance",         
            "Pun",
            "Alliteration",  
            "Onomatopoeia",      
            "Oxymoron",           
            "Irony"           
        ]
        self.figure_of_speech = QComboBox()
        self.figure_of_speech.addItems(self.figure_of_speech_list)
        self.fos_gen_layout.addWidget(self.figure_of_speech)
        self.fos_gen_layout.addWidget(self.fos_gen_mode, alignment=Qt.AlignHCenter)
        self.gen_layout.addLayout(self.fos_gen_layout)

        #Rhymes and lexicon layout
        self.header2_label = QLabel("Rhymes and Lexicon")
        self.sidebar_layout.addWidget(self.header2_label, alignment=Qt.AlignHCenter)

        #Rhymes and lexicon line edit 
        self.prompt2_area = QLineEdit()
        self.prompt2_area.setPlaceholderText("Enter word search here")
        self.prompt2_area.setFixedSize(300, 30)  # Proper size for a line edit
        self.sidebar_layout.addWidget(self.prompt2_area)

        #search Button
        self.btn2 = QPushButton("Search")
        self.btn2.setFixedSize(150, 40)  # Fixed size for button
        self.btn2.clicked.connect(self.search_lexicon)
        self.sidebar_layout.addWidget(self.btn2, alignment=Qt.AlignHCenter)
        
        #Rhymes and lexicon options
        self.options_list = [
            "Rhymes",
            "Slant Rhymes",
            "Synonyms",
            "Antonyms",
            "Homophones",
            "Related",
            "Adjectives described by",
            "Nouns described by",
            "Spelling pattern match",
            "hyponyms",
            "Hypernyms",
            "Sound alike"
        ]

        self.rhymes_n_lexicon = QComboBox()
        self.rhymes_n_lexicon.addItems(self.options_list)
        self.sidebar_layout.addWidget(self.rhymes_n_lexicon, alignment=Qt.AlignHCenter)

        #Melody and flows recorder
        self.m_label = QLabel("Melody & Flow Recorder")
        self.sidebar_layout.addWidget(self.m_label, alignment=Qt.AlignHCenter)

        self.launch_btn = QPushButton("Launch M recorder")
        self.launch_btn.clicked.connect(self.launch_m_recorder)
        self.sidebar_layout.addWidget(self.launch_btn)

        # self.m_layout = QVBoxLayout()
        # self.sidebar_layout.addLayout(self.m_layout)

        # self.recording_status = QLabel("Ready to record...")
        # self.m_layout.addWidget(self.recording_status)

        # self.m_btn_layout = QHBoxLayout()
        # self.m_layout.addLayout(self.m_btn_layout)

        # self.record_btn = QPushButton("Record")
        # self.stop_btn = QPushButton("Stop")
        # self.stop_btn.setEnabled(False)
        # self.record_btn.clicked.connect(self.start_recording)
        # self.stop_btn.clicked.connect(self.stop_recording)
        # self.m_btn_layout.addWidget(self.record_btn)
        # self.m_btn_layout.addWidget(self.stop_btn)

        #Font combobox
        self.font_size: Optional[int] = 10
        self.font_label = QLabel("Font Size")
        self.sidebar_layout.addWidget(self.font_label)
        self.font_sizes = ["10", "12", "14", "16", "18", "20", "22", "24", "26"]
        self.font_size_opt = QComboBox()
        self.font_size_opt.addItems(self.font_sizes)
        self.font_size_opt.currentIndexChanged.connect(self.change_font_size)
        self.sidebar_layout.addWidget(self.font_size_opt)

        #setting and files related buttons
        self.container_layout = QHBoxLayout()
        self.sidebar_layout.addLayout(self.container_layout)

        # self.inner_layout = QVBoxLayout()
        # self.container_layout.addLayout(self.inner_layout)

        #theme btn
        self.thm_label = QLabel("Theme Label")
        self.l_mode = Path(__file__).parent / "Icons/icons8-light-64.png"
        self.d_mode = Path(__file__).parent / "Icons/icons8-dark-mode-48.png"
        self.n_mode = Path(__file__).parent / "Icons/icons8-day-and-night-50.png"

        # theme attr
        self.light_mode: Optional[str] = None
        self.dark_mode: Optional[str] = None
        self.neutral_mode: Optional[str] = None

        self.theme_btn = QPushButton("")
        self.theme_btn.setIcon(QIcon(str(self.d_mode)))
        self.theme_btn.setIconSize(QSize(30, 30))
        self.theme_btn.clicked.connect(self.apply_theme)

        files_icon = Path(__file__).parent / "Icons/icons8-new-document-48.png"
        self.file = QPushButton("")
        self.file.setIcon(QIcon(str(files_icon)))
        self.file.setIconSize(QSize(30, 30))
        self.file.setToolTip("files")
        self.file.clicked.connect(self.open_file)

        self.container2_layout = QHBoxLayout()
        self.sidebar_layout.addLayout(self.container2_layout)

        self.check_flow_icon = Path(__file__).parent /"icons" / "icons8-foursquare-64.png"
        self.check_flow_btn = QPushButton()
        self.check_flow_btn.setIcon(QIcon(str(self.check_flow_icon)))
        self.check_flow_btn.setIconSize(QSize(30,30))
        self.check_flow_btn.setToolTip("Check flow")
        self.check_flow_btn.clicked.connect(lambda: check_flow_of_selection(self))

        # self.about_button.clicked.connect(self.save_file)

        save_icon = Path(__file__).parent / "Icons/icons8-save-64.png"
        self.save_button = QPushButton("")
        self.save_button.setIcon(QIcon(str(save_icon)))
        self.save_button.setIconSize(QSize(30, 30))
        self.save_button.setToolTip("save")
        self.save_button.clicked.connect(self.save_file)

        self.container2_layout.addWidget(self.save_button)
        self.container2_layout.addWidget(self.check_flow_btn)

        self.container3_layout = QHBoxLayout()
        self.sidebar_layout.addLayout(self.container3_layout)

        about_icon = Path(__file__).parent / "Icons/icons8-brain-64.png"
        self.about_info = """
            <h2>🎵 Welcome to Lyrical Lab</h2>
            <p><b>Lyrical Lab</b> is the all-in-one songwriting companion for <b>Autodidex</b>. 
            This powerful sub-app helps you transform your ideas into polished songs.</p>

            <p>Whether you're battling writer's block or fine-tuning your masterpiece, 
            Lyrical Lab has you covered. Generate lyric suggestions in your chosen genre, 
            or spark your creativity with a library of figures of speech.</p>

            <p>Explore our <b>Comprehensive Lexicon</b> for instant access to 
            rhymes, synonyms, and related words.</p>

            <p>Our unique <b>Flow Analysis</b> tool shows the syllable count of each line 
            and highlights stressed and unstressed syllables, helping you perfect rhythm 
            and delivery.</p>

            <p>Record melody ideas, save your work, and customize your workspace with 
            themes and font sizes. <b>Lyrical Lab</b> is your personal studio for 
            precision, purpose, and perfect flow.</p>
            """
        self.about_button = QPushButton("")
        self.about_button.setIcon(QIcon(str(about_icon)))
        self.about_button.setIconSize(QSize(30, 30))
        self.about_button.setToolTip("About")
        self.container3_layout.addWidget(self.about_button)
        self.about_button.clicked.connect(self.about_app)
        

        self.container_layout.addWidget(self.theme_btn)
        self.container_layout.addWidget(self.file)



        # --- Editor Layout ---
        self.editor_layout = QVBoxLayout()
        self.editor_layout.setContentsMargins(10, 10, 10, 10)


        #splitter (like VS code resizable panel)
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setSizes([300, 100])  # Top bigger than bottom
        self.editor_layout.addWidget(self.splitter)


        # Writing Editor (Text Area)
        self.writing_editor = QTextEdit()
        self.writing_editor.setMinimumSize(400, 300)
        self.writing_editor.setPlaceholderText("Type your lyrics here")
        self.writing_editor.textChanged.connect(self.update_word_count)
        self.writing_editor.textChanged.connect(self.update_syllable_counts)
        self.writing_editor.textChanged.connect(self.autosave)
        self.writing_editor.textChanged.connect(self.update_word_count)
        self.splitter.addWidget(self.writing_editor)
        
        self.wc_icon = Path(__file__).parent / "Icons/icons8-word-file-64.png"
        self.word_count_label = QLabel(
            f'<img src="{str(self.wc_icon)}" width="40" height="40">'
            f'<span style="font-size: 20px;"> ⁚ 0</span>', self)
        self.word_count_label.setToolTip("word count")
        self.editor_layout.addWidget(self.word_count_label)

        #Output edit
        self.display_editor = QTextEdit()
        self.display_editor.setReadOnly(True)
        self.display_editor.setPlaceholderText("Rhymes, words, and lyrics generated will be displayed here...")
        self.splitter.addWidget(self.display_editor)

        self.editors = [self.writing_editor, self.display_editor]
        # --- Combine Layouts ---
        self.main_layout.addLayout(self.sidebar_layout)
        self.main_layout.addLayout(self.editor_layout)
        self.init_wrapper()

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

    def change_font_size(self):
        if self.openning_app == True:
            self.font = QFont("Arial", self.font_size)

        else: 
            self.font_size = int(self.font_size_opt.currentText())
            self.font = QFont("Arial", self.font_size)

        for editor in self.editors:
            editor.setFont(self.font)
    
    def update_search_mode(self):
        if self.fos_gen_mode.isChecked():
            self.search_mode = self.fos_mode
            logging.debug(f"Search is {self.search_mode}")

        elif self.lyric_gen_mode.isChecked():
            self.search_mode = self.lyric_mode
            logging.debug(f"Searching is {self.search_mode}")

    def generate(self):
        user_prompt = self.prompt_area.text().strip()
        if not user_prompt:
            self.display_editor.setPlainText("⚠️ Please enter a prompt first!")
            return

        # --- Lyric Generation Mode ---
        if self.search_mode == self.lyric_mode:
            genre = self.genres.currentText()
            logging.debug(f"Generating {genre} lyric suggestions for prompt: {user_prompt}")
            try:
                raw_output = self.gen_class.generate_lyrics(user_prompt, genre)
            except Exception as e:
                self.display_editor.setText(f"There has been an error: {e}")
                return
            
            if raw_output == None:
                self.display_editor.setText(f"⚠️API request failed,Couldn't generate lyrics")
                return
            
            # Create bullet list
            bullet_items = "".join([
                f"<li>{line.strip()}</li>" 
                for line in raw_output.splitlines() if line.strip()
            ])

            formatted = f"""
            🎵 <b>{genre} Lyric Suggestions:</b><br><br>
            <ul>
                {bullet_items}
            </ul>
            """
            self.display_editor.setHtml(formatted)

        # --- Figure of Speech Generation Mode ---
        elif self.search_mode == self.fos_mode:
            figure_of_speech = self.figure_of_speech.currentText()
            logging.debug(f"Generating {figure_of_speech}s related to {user_prompt}")

            raw_output = self.gen_class.cliches_phrase_quotes(user_prompt, figure_of_speech)

            if raw_output == None:
                self.display_editor.setText(f"⚠️API request failed,Couldn't generate lyrics")
                return

            # Create numbered list
            numbered_items = "".join([
                f"<li>{line.strip()}</li>"
                for line in raw_output.splitlines() if line.strip()
            ])

            formatted = f"""
            ✨ <b>{figure_of_speech} Suggestions for '{user_prompt}':</b><br><br>
            <ol>
                {numbered_items}
            </ol>
            """
            self.display_editor.setHtml(formatted)

        # Clear prompt after generation
        self.prompt_area.clear()


    
    def search_lexicon(self):
        part_of_search = self.rhymes_n_lexicon.currentText()
        word = self.prompt2_area.text()
        logging.debug(f"Searching for {part_of_search} -> {word} ")
        self.search_lexicon_helper(part_of_search, word)
        self.prompt2_area.clear()

    
    def search_lexicon_helper(self, part_of_speech, word):
        if part_of_speech == self.options_list[0]:
            logging.debug(f"Here a {part_of_speech} found for {word}")
            res = f"🎤 Rhymes with '{word}': {self.rimes_n_lex.rhymes_with(word)}"
            res = "".join(res) 
            self.display_editor.setPlainText(res)

        elif part_of_speech == self.options_list[1]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🧠 Slant rhymes for '{word}': {self.rimes_n_lex.slant_rhymes(word)}"
            self.display_editor.setPlainText(res)

        elif part_of_speech == self.options_list[2]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🍃 Synonyms for '{word}': {self.rimes_n_lex.synonyms_for(word)}"
            self.display_editor.setPlainText(res)
            
        elif part_of_speech == self.options_list[3]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🌑 Antynoms for '{word}': {self.rimes_n_lex.antonyms_for(word)}"
            self.display_editor.setPlainText(res)
            
        elif part_of_speech == self.options_list[4]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🧩 Homophones for '{word}': {self.rimes_n_lex.homophones_for(word)}"
            self.display_editor.setPlainText(res)
            

        elif part_of_speech == self.options_list[5]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🔗 Related words for '{word}': {self.rimes_n_lex.triggers(word)}"
            self.display_editor.setPlainText(res)
            

        elif part_of_speech == self.options_list[6]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🎨 Adjectives words for '{word}': {self.rimes_n_lex.adjectives_for(word)}"
            self.display_editor.setPlainText(res)
            

        elif part_of_speech == self.options_list[7]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"💡 Nouns words for '{word}': {self.rimes_n_lex.nouns_described_by(word)}"
            self.display_editor.setPlainText(res)

        elif part_of_speech == self.options_list[8]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🕵️ Spelled like words for '{word}': {self.rimes_n_lex.spelled_like(word)}"
            self.display_editor.setPlainText(res)

        elif part_of_speech == self.options_list[9]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🧬  More specific words for '{word}': {self.rimes_n_lex.more_specific_than(word)}"
            self.display_editor.setPlainText(res)
            
        elif part_of_speech == self.options_list[10]:
            logging.debug(f"Here are {part_of_speech} found for {word}")
            res = f"🧠  More general like words for '{word}': {self.rimes_n_lex.more_general_than(word)}"
            self.display_editor.setPlainText(res)

        elif part_of_speech == self.options_list[11]:
            logging.debug(f"Hare a are {part_of_speech} found {word}")    
            res = f"📝  Sound like words for '{word}': {self.rimes_n_lex.sounds_like(word)}"
            self.display_editor.setPlainText(res)

    def update_word_count(self):
        text = self.writing_editor.toPlainText()
        words_num = len(text.split()) 
        self.word_count_label.setText( 
            f'<img src="{str(self.wc_icon)}" width="40" height="40">'
            f'<span style="font-size: 20px;"> ⁚ {str(words_num)}</span>')
        
    def launch_m_recorder(self):
        self.m_recorder = VoiceRecorder()
        self.m_recorder.show()

    def update_syllable_counts(self):
        lines = self.writing_editor.toPlainText().splitlines()
        logging.debug(lines)
        
        results = []

        for index,  line in enumerate(lines):
            index = index + 1
            # logging.debug(line)
            results.append(self.word_counts(line, index))
        
        logging.debug(results)

        if results:
            self.display_editor.setPlainText("\n".join(results))
        else:
            self.display_editor.setPlainText("")
 
    def word_counts(self, line, index):
        
        #split the words in a line
        words = line.split()
        # logging.debug(f"line {index} has {len(words)} words")

        #get the syllable count in a word
        
        list_syllable = []
        for word in words:
            syllable_num = self.syllable_count(word, index)
            list_syllable.append(syllable_num)

        return f"{line}({sum(list_syllable)})"
            
        # logging.debug(self.lines_dict)
                                    
            # logging.debug(f"{line}({sum(list_syllble)})")
            # line_with_syllable_count = f"{line}({sum(list_syllble)})"
            # self.display_editor.setPlainText(line_with_syllable_count)
        # list_syllble = []

    def syllable_count(self, word, index):

        syllables = pronouncing.phones_for_word(word)
        
        if not syllables:
            syllables = len(dic.inserted(word).split('-'))
            # logging.debug(f"The number of syllables in {word} is {syllables}, in line {index}")
            return syllables
        else:
            logging.debug(f"{syllables}")
            syllable_number = pronouncing.syllable_count(syllables[0])
            # logging.debug(f"Numbers of syllabes in {word} are {syllable_number} in {index}")
            return syllable_number    

    def autosave(self):
        current_text = self.writing_editor.toPlainText()
        if current_text != getattr(self, "last_saved_text",""):
            file = Path(__file__).parent / "noteworthy files/temp.txt"
            with open(file, "w", encoding="utf-8") as f:
                f.write(current_text)
            self.last_saved_text = current_text

    def get_last_written(self):
        file = Path(__file__).parent / "noteworthy files/temp.txt"
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            for editor in self.editors:
                editor.setText(text)
            
            self.previous_text = False
        except FileNotFoundError:
            return
    
    def save_preferences(self):
        """Save user preferences (theme & font size) to a JSON file."""
        data = {
            "dark_mode": self.mode,
            "font_size": self.font_size_opt.currentText()
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file)

    def load_preferences(self):
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
    
    def apply_theme(self):
        # if self.mode:
        #     self._dark_mode()
        # else:
        #     self._light_mode()
        if self.mode == "light":
            self.setStyleSheet(self.dark_mode)
            self.theme_btn.setIcon(QIcon(str(self.l_mode)))
            self.mode = "dark"
            cache.set("theme", "dark")
        elif self.mode == "dark":
            self.setStyleSheet(self.neutral_mode)
            self.theme_btn.setIcon(QIcon(str(self.n_mode)))
            self.mode = "neutral"
            cache.set("theme", "neutral")
        elif self.mode == "neutral":
            self.theme_btn.setIcon(QIcon(str(self.d_mode)))
            self.setStyleSheet(self.light_mode)
            self.mode = "light"
            cache.set("theme", "light")

    def _dark_mode(self):
        """Apply dark mode styles"""
        dark_mode_file = Path(__file__).parent / "themes files/dark_mode.txt"

        with open(dark_mode_file, "r") as f:
            dark_mode = f.read()
        self.setStyleSheet(dark_mode)
        self.theme_btn.setIcon(QIcon(str(self.l_mode)))
        

    def _light_mode(self):
        """Apply light mode styles."""
        light_mode_file = Path(__file__).parent / "themes files/light_mode.txt"

        with open(light_mode_file, "r") as f:
            light_mode = f.read()

        self.setStyleSheet(light_mode)
        self.theme_btn.setIcon(QIcon(str(self.d_mode)))

    def init_wrapper(self):
        self.mode, self.font_size = self.load_preferences()
        self.load_themes()
        self.apply_theme()
        self.change_font_size()
        self.get_last_written()
        self.openning_app = False
    

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)")

        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                for editor in self.editors:
                    editor.setText(file.read())
    
    def save_file(self):
        #Prompts the user for filename and location
        file_name, _ = QFileDialog.getSaveFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)") 

        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.writing_editor.toPlainText())
        
    def theme(self):
        self.mode = not self.mode
        self.apply_theme()
        self.save_preferences()

    
    def about_app(self):
        """Triggered by About button click."""
        msg = QMessageBox(self)                     # 1️⃣ Create a QMessageBox instance
        msg.setWindowTitle("About Lyrical Lab")      # 2️⃣ Title of the box
        msg.setTextFormat(Qt.TextFormat.RichText)    # 3️⃣ Enable HTML
        msg.setText(self.about_info)                 # 4️⃣ Use stored HTML
        msg.setStandardButtons(QMessageBox.Ok)       # 5️⃣ Add OK button
        msg.exec()         # 6️⃣ Show the message box

    def start_recording(self):
        logging.debug("Recording started")
        self.recording_status.setText("Recording...")
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.m_recorder.run()
        logging.debug("Still recording")

    def stop_recording(self):
        self.recording_status.setText("Ready to record...")
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.m_recorder.stop()
        logging.debug("Recording Done")

def get_stress_pattern(line):
    """Return a string of U (unstressed) and S (stressed) syllables for a line"""
    words = line.lower().split()
    # logging.debug(f"words in the sentence {words}")
    pattern = []
    
    for word in words:
        #Looks up the pronunciation(s) of the word in the CMU Pronouncing Dictionary.
        #Returns them in ARPABET phonetic notation. R  IH0  S  T  AO1  R  IH0  NG
        # 0 = unstressed
        # 1 = primary stress
        # 2 = secondary stress
        phones = pronouncing.phones_for_word(word)

        if phones:
            logging.debug(phones[0])
            stress = pronouncing.stresses(phones[0])
            logging.debug(f'stress is {stress}')

            # stress is something like "010"
            for c in stress:  # Loop through each digit in the stress string
                if c in '12':         # If this syllable is primary or secondary stress
                    pattern.append('S')  # Add a stressed syllable marker
                else:                 # Otherwise (c == '0')
                    pattern.append('u')  # Add an unstressed syllable marker
        else:
            pattern.append('?')  # Unknown word
    
    logging.debug(f"The line pattern is {''.join(pattern)}")
    
    return ''.join(pattern)


def alignment_score(patterns):
    """Calculate how aligned the stressed syllables are across multiple lines."""
    if len(patterns) < 2:
        return None  # Can't compare if only 1 line
    
    # Pad patterns to the same length
    max_len = max(len(p) for p in patterns)
    padded = [p.ljust(max_len) for p in patterns]
    
    # Compare syllables column by column
    aligned = 0
    total = 0
    for i in range(max_len):
        # Check if all non-space syllables in this column are the same
        column = [p[i] for p in padded if p[i] != ' ']
        if column:
            total += 1
            if all(c == column[0] for c in column):
                aligned += 1
    
    return aligned / total if total else 0


def highlight_flow(patterns, lines):
    """Return HTML showing flow patterns with color coding"""

    logging.debug(f"What is lines: {lines}")
    logging.debug(f"What is patterns: {patterns}")
    # Pad patterns to same length
    #Each string is a line’s stress pattern of syllables (u = unstressed, S = stressed).
    # But they don’t all have the same length, which makes alignment and column-by-column comparison tricky
    max_len = max(len(p) for p in patterns)
    logging.debug(f"The maximum length is {max_len}")
    # This finds the length of the longest pattern.
    # len(p) for p in patterns creates a list of lengths:
    padded = [p.ljust(max_len) for p in patterns]
    logging.debug(f"The aligned pattern is {padded}")
    # .ljust(max_len) left-justifies each string and pads it with spaces to make all patterns the same length.
    

    # Determine alignment per column
    column_alignment = []
    for i in range(max_len):
        #Loops over every line’s stress pattern (p)
        # Looks at the i-th syllable (or space)
        # Skips if it’s just a padding space
        # Collects only the real syllables into the column list
        column = [p[i] for p in padded if p[i] != ' ']
        if not column:
            column_alignment.append(None)
        # 
#         column[0] is the first syllable in the column (used as the “reference”).
        # for c in column loops through each syllable in that column.
        # c == column[0] checks if every syllable matches the first one.
        # all(...) returns True only if every check is True.
        elif all(c == column[0] for c in column):
            column_alignment.append(True)  # aligned
        else:
            column_alignment.append(False) # misaligned
    
    # Build HTML with colors
    html_lines = []
    for line, pattern in zip(lines, padded):
        
        # Green if it aligns with the other lines
        # Red if it’s off-beat
        # Add it as bold colored HTML
        colored_pattern = ""
        for char, aligned in zip(pattern, column_alignment):
            if char == 'S':
                color = "green" if aligned else "red"
                colored_pattern += f"<span style='color:{color};font-weight:bold'>{char}</span>"
            elif char == 'u':
                colored_pattern += f"<span style='color:gray'>{char}</span>"
            else:
                colored_pattern += " "
        html_lines.append(f"<b>{line}</b><br>{colored_pattern}<br><br>")
    
    logging.debug("".join(html_lines))    
    return "".join(html_lines)


def check_flow_of_selection(self):
    """Analyze flow of the selected text in QTextEdit"""
    cursor = self.writing_editor.textCursor()
    selected = cursor.selectedText()
    
    if not selected.strip():
        self.display_editor.setPlainText("⚠️ No text selected.")
        return
    
    lines = selected.splitlines()
    patterns = [get_stress_pattern(line) for line in lines]
    logging.debug(patterns)
    
    # Generate color-coded HTML flow map
    html = highlight_flow(patterns, lines)
    
    # # Compute alignment score
    score = alignment_score(patterns)
    if score is not None:
        html += f"<b>🎯 Flow Alignment Score: {score:.2f}</b>"
    
    self.display_editor.setHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsSummarizationUi()
    window.show()
    sys.exit(app.exec())
















# class AutodidexUI(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Autodidex Lyric & Summary Tool")
#         self.setGeometry(200, 200, 700, 600)

#         # --- LAYOUTS ---
#         layout = QVBoxLayout()
#         self.setLayout(layout)

#         # Lyric Theme
#         self.theme_label = QLabel("🎤 Lyric Theme:")
#         self.theme_input = QLineEdit()
#         layout.addWidget(self.theme_label)
#         layout.addWidget(self.theme_input)

#         # Text for Summarization
#         self.text_label = QLabel("🧠 Text to Summarize:")
#         self.text_input = QTextEdit()
#         self.text_input.setPlaceholderText("Paste your text here...")
#         layout.addWidget(self.text_label)
#         layout.addWidget(self.text_input)

#         # Buttons
#         button_layout = QHBoxLayout()
#         self.lyric_button = QPushButton("Generate Lyrics")
#         self.summary_button = QPushButton("Summarize Text")
#         button_layout.addWidget(self.lyric_button)
#         button_layout.addWidget(self.summary_button)
#         layout.addLayout(button_layout)

#         # Output Box
#         self.output_label = QLabel("📜 Output:")
#         self.output_box = QTextEdit()
#         self.output_box.setReadOnly(True)
#         layout.addWidget(self.output_label)
#         layout.addWidget(self.output_box)

#         # --- EVENTS ---
#         self.lyric_button.clicked.connect(self.generate_lyrics)
#         self.summary_button.clicked.connect(self.summarize_text)

#     # --- METHODS ---
#     def generate_lyrics(self):
#         theme = self.theme_input.text().strip()
#         if theme:
#             self.output_box.setText("Generating lyrics...\n")
#             lyrics = client.generate_lyrics(theme)
#             self.output_box.setText(lyrics if lyrics else "❌ Error generating lyrics.")

#     def summarize_text(self):
#         text = self.text_input.toPlainText().strip()
#         if text:
#             self.output_box.setText("Summarizing text...\n")
#             summary = client.summarize_text(text)
#             self.output_box.setText(summary if summary else "❌ Error summarizing text.")


# # --- RUN APP ---
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = AutodidexUI()
#     window.show()
#     sys.exit(app.exec())
