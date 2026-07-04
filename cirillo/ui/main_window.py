import sys
from pathlib import Path


from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QMessageBox, QVBoxLayout, QWidget


from cirillo.services.audio_service import AudioService
from cirillo.services.reward_service import RewardService
from cirillo.services.session_logger import SessionLogger
from cirillo.services.theme_service import ThemeService
from cirillo.services.timer_service import TimerService
from autodidex_services.files_formats import file_types

from cirillo.ui.controls import Controls
from cirillo.ui.sidebar import Sidebar
from cirillo.ui.timer_display import TimerDisplay


SOUND_FILES = {
    "lofi":   "sounds/lofi.mp3",
    "Forest": "sounds/forestsounds.mp3",
    "Rain":   "sounds/25 Minutes Sound Rain Noise to SleepRelaxing Rain.mp3",
    "Cafe":   "sounds/25 minutes of Cafe Noise.mp3",
}


class PomodoroGUI(QWidget):
    """
    Thin orchestration shell.

    Responsibilities:
      - Instantiate services and UI sub-widgets.
      - Connect signals → service calls.
      - React to service callbacks → update UI.
    """

    def __init__(self):
        super().__init__()
        self.path = Path(__file__).parent

        # ---- services ----
        self.audio    = AudioService()
        self.logger   = SessionLogger(self.path.parent / "sessions.csv")
        self.themes   = ThemeService(self.path.parent.parent)
        self.reward   = RewardService(self.path.parent.parent)
        self.timer_svc = TimerService()

        # Session state shared between timer callbacks and logger
        self._current_sessions = self.logger.load_current_sessions()

        # ---- window chrome ----``
        self.setWindowTitle("Cirillo")
        icon_path = self.path.parent.parent / "Icons/icons8-pomodoro-50.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        # ---- build layout ----
        root = QHBoxLayout()
        self.setLayout(root)

        self.sidebar = Sidebar(self.path.parent.parent)
        root.addWidget(self.sidebar)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.display  = TimerDisplay()
        self.controls = Controls(self.path.parent.parent)

        right_layout.addWidget(self.display)
        right_layout.addWidget(self.controls)
        root.addWidget(right_panel)

        # ---- wire signals ----
        self._connect_signals()


    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------
    def _connect_signals(self):
        # sidebar
        self.sidebar.sound_selector.currentTextChanged.connect(self._on_sound_changed)
        self.sidebar.volume_slider.valueChanged.connect(self.audio.set_volume)

        # controls
        self.controls.start_btn.clicked.connect(self._start_session)
        self.controls.pause_btn.clicked.connect(self._toggle_pause)
        self.controls.stop_btn.clicked.connect(self._quit_session)
        self.controls.reward_folder_btn.clicked.connect(self._choose_reward_folder)

        # timer service callbacks
        self.timer_svc.on_tick = self.display.set_time
        self.timer_svc.on_work_complete = self._on_work_complete
        self.timer_svc.on_break_complete = self._on_break_complete

    # ------------------------------------------------------------------
    # Session flow
    # ------------------------------------------------------------------
    def _start_session(self):
        self.timer_svc.start_work(self.display.work_duration)
        self._play_selected_sound()

    def _on_work_complete(self):
        """Called by TimerService when a work interval ends."""
        self.audio.stop()
        total = self.timer_svc.sessions_this_run + self._current_sessions
        self.logger.log(total, self.timer_svc.time_studied_mins + self.display.work_duration)
        self._current_sessions = total
        self.timer_svc.sessions_this_run = 0
        self._start_break()

    def _start_break(self):
        duration = self.display.break_duration
        if self.timer_svc.needs_long_break():
            duration *= 3
            QMessageBox.information(self, "Long break!", f"Reward: {self.controls.reward}")
        else:
            QMessageBox.information(self, "Break time!", f"Reward: {self.controls.reward}")

        self.timer_svc.start_break(duration)
        self._play_reward(duration)

    def _on_break_complete(self):
        """Called by TimerService when a break ends."""
        self.reward.stop()
        QMessageBox.information(self, "Break Over", "Time to get back to work!")
        self._start_session()

    def _quit_session(self):
        if not self.timer_svc.is_running():
            QMessageBox.warning(self, "Warning", "Cannot end session — you haven't started yet.")
            return
        self.timer_svc.stop()
        self.audio.stop()
        self.display.reset()
        self.controls.set_paused_icon(False)
        QMessageBox.information(self, "Goodbye!", f"You completed {self._current_sessions} session(s).")

    def _toggle_pause(self):
        if not self.timer_svc.is_running():
            QMessageBox.warning(self, "Warning", "Pomodoro session hasn't started yet.")
            return
        paused = self.timer_svc.toggle_pause()
        if paused:
            self.audio.pause()
        else:
            self.audio.unpause()
        self.controls.set_paused_icon(paused)

    # ------------------------------------------------------------------
    # Sound
    # ------------------------------------------------------------------
    def _on_sound_changed(self, text: str):
        if text == "None":
            self.audio.stop()
        # Actual playback starts when the session starts

    def _play_selected_sound(self):
        sound_name = self.sidebar.sound_selector.currentText()
        if sound_name != "None":
            rel = SOUND_FILES.get(sound_name)
            if rel:
                try:
                    self.audio.play(self.path.parent / rel)
                except RuntimeError as e:
                    QMessageBox.critical(self, "Audio error", str(e))

    # ------------------------------------------------------------------
    # Reward
    # ------------------------------------------------------------------
    def _play_reward(self, break_duration_mins: int):
        choice = self.controls.reward
        if choice == "None":
            return
        ext_map = {"Video": "Videos", "Music": "Music", "Image": "Images"}
        key = ext_map.get(choice)
        if key:
            self.reward.play(file_types[key])
        # reward.stop() is called in _on_break_complete

    def _choose_reward_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select reward folder",
            str(self.reward.search_root),
        )
        if folder:
            self.reward.search_root = Path(folder)
            self.controls.set_reward_folder_path(folder)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _toggle_theme(self, mode: str = "dark"):
        print(f"the mode is {mode}")
        self.themes.toggle(mode)
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(self.themes.stylesheet())

# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroGUI()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
