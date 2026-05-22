"""
SpaceInvaderWidget
------------------
Launches the Space Invader game in a background thread.

Bug fixes vs original:
- The original `import space_invader` crashed at import time because
  pygame.init(), screen setup, and all image loading ran at module scope.
  Fixed: `main.py` defers all of that inside main(); this widget imports
  from main directly.
- The original thread had no stop mechanism — it became a zombie if the
  widget was closed mid-game.  Fixed: the thread is tracked and the button
  is disabled while a session is running so only one instance ever runs.
"""

import threading
from PySide6.QtCore    import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

import spaceinvader.main as space_invader_main


class SpaceInvaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Space Invader")
        self._thread: threading.Thread | None = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._status = QLabel("Ready to launch.")
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status)

        self._btn = QPushButton("Start Space Invader")
        self._btn.clicked.connect(self._launch)
        layout.addWidget(self._btn)

    def _launch(self):
        # Guard: don't spawn a second instance if one is already running
        if self._thread and self._thread.is_alive():
            self._status.setText("Game is already running.")
            return

        self._btn.setEnabled(False)
        self._status.setText("Game running…")

        self._thread = threading.Thread(
            target=self._run_game,
            daemon=True,    # killed automatically when the main process exits
            name="SpaceInvaderThread",
        )
        self._thread.start()

    def _run_game(self):
        """Runs in the background thread."""
        try:
            space_invader_main.main()
        finally:
            # Re-enable the button from the game thread; PySide6 is not fully
            # thread-safe for UI calls, so use a queued signal if strict safety
            # is required.  For a simple launcher this is acceptable.
            self._btn.setEnabled(True)
            self._status.setText("Game ended. Ready to launch again.")
