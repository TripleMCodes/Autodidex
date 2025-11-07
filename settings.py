# settings_ui.py

from PySide6.QtWidgets import (QApplication,
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QCheckBox, QPushButton, QMessageBox )
from PySide6.QtCore import Qt
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG) 
# from settings_manager import SettingsManager

# settings_manager.py

class SettingsManager:
    def __init__(self):
        # Theme Settings
        self.theme = "light"  # options: "light", "dark"
        self.primary_color = "#6F54D8"
        self.secondary_color = "#BFA6FF"
        self.background_gradient = {
            "light": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FAF8FF, stop:1 #E8E3FF)",
            "dark": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A1A2E, stop:1 #16213E)"
        }

        # Font Settings
        self.font_family = "Fira Sans"
        self.base_font_size = 14
        self.header_font_size = 24

        # Behavior Settings
        self.autosave_enabled = True
        self.notifications_enabled = True
        self.pomodoro_duration = 25  # in minutes

        # Placeholder for future expansions
        self.user_data_path = "./userdata/"
        self.language = "en"

    def get_stylesheet(self):
        """Return a formatted stylesheet string based on current settings."""
        pass
       

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        logging.debug(f"chosen theme is {self.theme}")

    

class SettingsWidget(QWidget):
    def __init__(self, settings: SettingsManager, apply_callback=None):
        super().__init__()
        self.settings = settings
        self.apply_callback = apply_callback  # Optional: function to re-style the app

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Theme selector
        self.thm_mode = "dark"
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.thm_btn = QPushButton("☀️ light mode")
        self.thm_btn.clicked.connect(self.apply_settings)
        # self.theme_combo = QComboBox()
        # self.theme_combo.addItems(["light", "dark"])
        # self.theme_combo.setCurrentText(self.settings.theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.thm_btn)
        layout.addLayout(theme_layout)

        # Font size selector
        # font_layout = QHBoxLayout()
        # font_label = QLabel("Font Size:")
        # self.font_spin = QSpinBox()
        # self.font_spin.setRange(8, 48)
        # self.font_spin.setValue(self.settings.base_font_size)
        # font_layout.addWidget(font_label)
        # font_layout.addWidget(self.font_spin)
        # layout.addLayout(font_layout)

        # Pomodoro duration
        # pomo_layout = QHBoxLayout()
        # pomo_label = QLabel("Pomodoro Duration (min):")
        # self.pomo_spin = QSpinBox()
        # self.pomo_spin.setRange(5, 90)
        # self.pomo_spin.setValue(self.settings.pomodoro_duration)
        # pomo_layout.addWidget(pomo_label)
        # pomo_layout.addWidget(self.pomo_spin)
        # layout.addLayout(pomo_layout)

        # Autosave
        # self.autosave_check = QCheckBox("Enable Autosave")
        # self.autosave_check.setChecked(self.settings.autosave_enabled)
        # layout.addWidget(self.autosave_check)

        # # Notifications
        # self.notifications_check = QCheckBox("Enable Notifications")
        # self.notifications_check.setChecked(self.settings.notifications_enabled)
        # layout.addWidget(self.notifications_check)

        # Apply Button
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_btn)

        # Set layout
        layout.addStretch()
        self.setLayout(layout)

    def apply_settings(self):
        # Update settings
        self.settings.theme = self.theme_combo.currentText()
        # self.settings.set_font_size(self.font_spin.value())
        # self.settings.pomodoro_duration = self.pomo_spin.value()
        # self.settings.autosave_enabled = self.autosave_check.isChecked()
        # self.settings.notifications_enabled = self.notifications_check.isChecked()

        # Optional callback to update app
        if self.apply_callback:
            self.apply_callback()

        QMessageBox.information(self, "Settings Applied", "Your settings have been updated.")

if __name__ == "__main__":
    app = QApplication([])
    window = SettingsWidget(SettingsManager())
    window.show()
    app.exec()
