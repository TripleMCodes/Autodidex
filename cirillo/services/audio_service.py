import pygame
from PySide6.QtWidgets import QMessageBox


class AudioService:
    """Handles ambient sound playback and volume via pygame."""

    def __init__(self):
        pygame.mixer.init()
        self.current_sound = None

    def play(self, sound_path):
        """Load and loop a sound file indefinitely."""
        self.stop()
        try:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)
            self.current_sound = sound_path
        except Exception as e:
            raise RuntimeError(f"Failed to play sound: {e}") from e

    def stop(self):
        """Stop current ambient sound."""
        pygame.mixer.music.stop()
        self.current_sound = None

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def set_volume(self, value: int):
        """Accept 0-100 int, convert to pygame 0.0-1.0 float."""
        pygame.mixer.music.set_volume(value / 100)
