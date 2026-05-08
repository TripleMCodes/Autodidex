import logging
import os
import random
import subprocess
from pathlib import Path

import psutil
from PySide6.QtWidgets import QMessageBox


MEDIA_APPS = {
    "Photos", "mspaint", "IrfanView", "Photoshop", "VLC", "MediaMonkey",
    "MusicBee", "Media Player", "5KPlayer", "GOM Player", "PotPlayer",
    "MPV", "KMPlayer", "Quicklook", "Preview", "IINA", "Kodi", "DivX",
}


class RewardService:
    """Opens a random media file for break rewards and kills it afterwards."""

    def __init__(self, search_root: Path):
        self.search_root = search_root
        self.proc: subprocess.Popen | None = None

    # ------------------------------------------------------------------
    def play(self, file_extensions: list[str]) -> bool:
        """
        Walk *search_root* for files matching *file_extensions*, open a
        random one with the OS default app, and return True on success.
        """
        candidates = [
            os.path.join(dp, fn)
            for dp, _, files in os.walk(self.search_root)
            for fn in files
            if any(fn.endswith(ext) for ext in file_extensions)
        ]
        if not candidates:
            logging.debug("RewardService: no media files found.")
            return False

        path = random.choice(candidates)
        self.proc = subprocess.Popen(["start", path], shell=True)
        logging.debug(f"RewardService: opened {path}")
        return True

    def stop(self):
        """Kill any common media viewer / player that is currently running."""
        killed = False
        for proc in psutil.process_iter(["pid", "name"]):
            name = proc.info.get("name", "")
            if any(app.lower() in name.lower() for app in MEDIA_APPS):
                try:
                    os.system(f"taskkill /IM {name} /F")
                    logging.debug(f"RewardService: killed {name}")
                    killed = True
                except Exception as e:
                    logging.error(f"RewardService: error closing {name}: {e}")
                break
        if not killed:
            logging.debug("RewardService: no media viewer found to close.")
