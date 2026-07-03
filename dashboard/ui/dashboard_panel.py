from pathlib import Path
from datetime import date

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QVBoxLayout, QWidget,
)


from calender.ui.streak_tracker import StreakTracker
from dashboard.ui.spinning_label import SpinningLabel
from calender.services.session_reader import SessionReader


class DashboardPanel(QWidget):
    """
    The main game dashboard shown after login.

    Exposes widget references that main_window connects to service calls.
    Contains zero business logic — layout and labels only.
    """

    def __init__(self, base_path: Path, user, bank, store_items: list, parent=None):
        super().__init__(parent)
        self._path = base_path
        self._build_ui(user, bank, store_items)

    # ------------------------------------------------------------------
    def _build_ui(self, user, bank, store_items: list):
        main_layout = QVBoxLayout(self)
        layout = QVBoxLayout()
        h_layout = QVBoxLayout()
        h_layout.geometry()

        main_layout.addLayout(layout)
        main_layout.addLayout(h_layout)

        # ---- spinning header ----
        label_row = QHBoxLayout()
        self.dashboard_label = SpinningLabel("Autodidex")
        self.dashboard_label.setObjectName("dblabel")
        label_row.addWidget(self.dashboard_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(label_row)

        # ---- theme toggle ----
        header_row = QHBoxLayout()
        self.theme_btn = QPushButton("")
        self.theme_btn.setIconSize(QSize(30, 30))
        header_row.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(header_row)

        # ---- stat labels ----
        n_icon = self._path / "Icons/icons8-name-64.png"
        self.name_label = self._icon_label(n_icon, user.name, "Name")

        self.l_icon = self._path / "Icons/icons8-bill-64.png"
        self.level_label = self._icon_label(self.l_icon, str(user.level), "Overall Level")

        self.w_icon = self._path / "Icons/icons8-wallet-64.png"
        self.wallet_label = self._icon_label(self.w_icon, f"{bank.wallet} Lumens", "Wallet")

        self.xp_icon = self._path / "Icons/icons8-points-64.png"
        self.xp_label = self._icon_label(self.xp_icon, str(bank.xp), "XP Points")

        for lbl in (self.name_label, self.level_label, self.wallet_label, self.xp_label):
            layout.addWidget(lbl)

        # ---- subject / badge section ----
        xp_row = QHBoxLayout()
        s_icon = self._path / "Icons/icons8-calibre-64.png"
        subj_icon_label = QLabel()
        subj_icon_label.setText(f'<img src="{s_icon}" width="40" height="40">')
        subj_icon_label.setToolTip("Subjects")

        self.subject_combo = QComboBox()
        xp_row.addWidget(subj_icon_label)
        xp_row.addWidget(self.subject_combo)
        layout.addLayout(xp_row)

        b_icon = self._path / "Icons/icons8-trophy-64.png"
        badge_icon_label = QLabel()
        badge_icon_label.setText(f'<img src="{b_icon}" width="40" height="40">')
        badge_icon_label.setToolTip("Badges")
        self.badge_list = QListWidget()
        layout.addWidget(badge_icon_label)
        layout.addWidget(self.badge_list)

        
        

        # ---- PolyMart section ----
        c_icon = self._path / "Icons/icons8-cart-64.png"
        cart_label = QLabel(
            f'<img src="{c_icon}" width="40" height="40">'
            f'<span style="font-size:20px;"> PolyMart⁚ </span>'
        )
        layout.addWidget(cart_label)

        self.store_combo = QComboBox()
        self.store_combo.addItems(store_items)

        self.buy_icon   = self._path / "Icons/icons8-pay-64.png"
        self.trade_icon = self._path / "Icons/icons8-trade-64.png"
        self.buy_btn    = QPushButton("")
        self.buy_btn.setIcon(QIcon(str(self.buy_icon)))
        self.buy_btn.setIconSize(QSize(30, 30))

        layout.addWidget(self.store_combo)
        layout.addWidget(self.buy_btn)
        layout.addLayout(h_layout)

    # ------------------------------------------------------------------
    # Stat label update helpers
    # ------------------------------------------------------------------
    def refresh_level(self, level: int):
        self.level_label.setText(self._html(self.l_icon, str(level), "Overall Level"))

    def refresh_wallet(self, amount: int):
        self.wallet_label.setText(self._html(self.w_icon, f"{amount} Lumens", "Wallet"))

    def refresh_xp(self, xp: int):
        self.xp_label.setText(self._html(self.xp_icon, str(xp), "XP Points"))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _icon_label(self, icon_path: Path, value: str, tooltip: str) -> QLabel:
        lbl = QLabel(self._html(icon_path, value, tooltip))
        lbl.setToolTip(tooltip)
        return lbl

    @staticmethod
    def _html(icon_path: Path, value: str, tooltip: str = "") -> str:
        return (
            f'<img src="{icon_path.as_posix()}" width="40" height="40">'
            f'<span style="font-size:20px;"> ⁚ {value}</span>'
        )
