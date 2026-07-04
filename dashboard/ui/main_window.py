import logging
import sys
from pathlib import Path

from autodidex_cache import DictionaryCache
from dash_board_db import Dashboard

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from dashboard.services.bank_service    import BankService
from dashboard.services.store_service   import StoreService
from dashboard.services.theme_service   import ThemeService
from dashboard.services.trigger_service import TriggerService
from dashboard.services.user_service    import UserService

from dashboard.ui.dashboard_panel import DashboardPanel
from dashboard.ui.onload_screen   import OnloadScreen


class MainWindow(QMainWindow):
    """
    Thin orchestration shell.

    Responsibilities:
      - Instantiate all services and UI panels.
      - Connect widget signals → service calls.
      - Push service results back into the UI.
      - Decide which panel to show (onload vs dashboard).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autodidex Dashboard")

        self._path      = Path(__file__).parent.parent.parent
        self._dashboard = Dashboard()
        self._cache     = DictionaryCache()

        # ---- services ----
        self._themes   = ThemeService(self._path)
        self._user     = UserService()
        self._bank     = BankService(self._user)
        self._store    = StoreService(self._bank)
        self._triggers = TriggerService()

        # ---- register file triggers ----
        self._triggers.watch(
            self._path / "update.txt",
            self._on_new_cp,
        )
        self._triggers.watch(
            self._path / "update_db_ui.txt",
            self._on_db_ui_update,
        )

        # ---- init data ----
        self._cache.set("cp_badges", self._dashboard.get_cp_with_badges())
        self._cache.set("badges",    self._dashboard.get_all_badges())
        self._store.load_store_items()
        self._bank.earn_subject_xp()

        # ---- decide entry screen ----
        user_present = self._dashboard.get_user_state()
        if user_present:
            self._show_dashboard()
        else:
            self._show_onload()

    # ------------------------------------------------------------------
    # Screen transitions
    # ------------------------------------------------------------------
    def _show_onload(self):
        screen = OnloadScreen(self._path)
        screen.name_submitted.connect(self._on_name_submitted)
        self.setCentralWidget(screen)

    def _show_dashboard(self):
        self._panel = DashboardPanel(
            self._path,
            self._user,
            self._bank,
            self._store.get_display_items(),
        )
        self._connect_dashboard_signals()
        self.setCentralWidget(self._panel)

        # populate subjects and initial badge list
        self._panel.subject_combo.addItems(sorted(self._user.initialize_subjects()))
        if self._panel.subject_combo.count():
            self._on_subject_changed(0)

    def _connect_dashboard_signals(self):
        self._panel.subject_combo.currentIndexChanged.connect(self._on_subject_changed)
        self._panel.store_combo.currentIndexChanged.connect(self._on_store_selection_changed)
        self._panel.buy_btn.clicked.connect(self._on_buy)

    # ------------------------------------------------------------------
    # Onload
    # ------------------------------------------------------------------
    def _on_name_submitted(self, name: str):
        try:
            self._user.name = name
            state = self._dashboard.create_new_user(name)
            if state:
                self._dashboard.update_is_active_state(1)
                self._dashboard.starter_badge()
                self._show_dashboard()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Name", str(e))

    # ------------------------------------------------------------------
    # Dashboard interactions
    # ------------------------------------------------------------------
    def _on_subject_changed(self, index: int):
        cp_badges = self._cache.get("cp_badges") or {}
        self._panel.badge_list.clear()
        subject = self._panel.subject_combo.itemText(index)
        badges  = cp_badges.get(subject, ["No badge yet"])
        self._panel.badge_list.addItems(set(badges))

    def _on_store_selection_changed(self):
        label     = self._panel.store_combo.currentText()
        tradeable = self._store.is_tradeable(label)
        if tradeable:
            self._panel.buy_btn.setIcon(QIcon(str(self._panel.trade_icon)))
            self._panel.buy_btn.setToolTip("Trade Item")
        else:
            self._panel.buy_btn.setIcon(QIcon(str(self._panel.buy_icon)))
            self._panel.buy_btn.setToolTip("Buy Item")

    def _on_buy(self):
        item   = self._panel.store_combo.currentText()
        result = self._store.purchase(item)
        QMessageBox.information(self, "Transaction Result", result)
        self._panel.refresh_wallet(self._bank.wallet)

    # ------------------------------------------------------------------
    # File-trigger callbacks
    # ------------------------------------------------------------------
    def _on_new_cp(self):
        """Called when update.txt changes — a new cerebral pursuit was added."""
        self._user.refresh_subjects()
        if hasattr(self, "_panel"):
            self._panel.subject_combo.clear()
            self._panel.subject_combo.addItems(
                sorted(set(self._user.initialize_subjects()))
            )

    def _on_db_ui_update(self):
        """Called when update_db_ui.txt changes — checkbox states changed."""
        self._bank.earn_subject_xp()
        if hasattr(self, "_panel"):
            self._panel.refresh_level(self._user.level)
            self._panel.refresh_xp(self._bank.xp)
            self._panel.refresh_wallet(self._bank.wallet)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _toggle_theme(self, mode:str = "dark"):
        print(f"the mode is (dashboard): {mode}")
        self._themes.toggle(mode)
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(self._themes.stylesheet())


