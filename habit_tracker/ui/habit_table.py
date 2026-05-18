from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QCheckBox, QGraphicsDropShadowEffect, QHeaderView,
    QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


DAYS = ["Habits", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MAX_ROWS = 15


class HabitTable(QWidget):
    """
    The main content area: the weekly habit grid plus the add-habit input row.

    Signals (emit data; main_window connects them to services):
        checkbox_toggled(row, col, day, subject)
        habit_submitted(text)
        context_edit_requested(row, subject)
        context_delete_requested(row, subject)
    """

    checkbox_toggled        = Signal(int, int, str, str)   # row, col, day, subject
    habit_submitted         = Signal(str)
    context_edit_requested  = Signal(int, str)             # row, old_subject
    context_delete_requested = Signal(int, str)            # row, subject

    def __init__(self, base_path: Path, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self.enable_checkbox_save = False
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- shadow effect ----
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(180, 150, 255, 120))

        # ---- table ----
        self.table = QTableWidget()
        self.table.setGraphicsEffect(shadow)
        self.table.setAlternatingRowColors(True)
        self.table.setRowCount(MAX_ROWS)
        self.table.setColumnCount(8)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setHorizontalHeaderLabels(DAYS)

        for col in range(1, 8):
            for row in range(MAX_ROWS):
                cb = QCheckBox()
                cb.setStyleSheet("margin-left:25px;")
                cb.stateChanged.connect(
                    lambda state, r=row, c=col: self._on_checkbox_state_changed(r, c, state)
                )
                self.table.setCellWidget(row, col, cb)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

        # ---- input row ----
        h_row = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter habit here")
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input.returnPressed.connect(self._submit_habit)
        h_row.addWidget(self.input)

        enter_icon = self.base_path / "Icons/icons8-enter-64.png"
        self.enter_btn = QPushButton("")
        self.enter_btn.setIcon(QIcon(str(enter_icon)))
        self.enter_btn.setIconSize(QSize(30, 30))
        self.enter_btn.setToolTip("enter")
        self.enter_btn.clicked.connect(self._submit_habit)
        h_row.addWidget(self.enter_btn)

        layout.addLayout(h_row)

    # ------------------------------------------------------------------
    # Public helpers called by main_window
    # ------------------------------------------------------------------
    def populate_habits(self, habits: list[str]):
        """Fill column 0 with habit names from the DB."""
        for r in range(self.table.rowCount()):
            self.table.setItem(r, 0, QTableWidgetItem(""))
        for idx, habit in enumerate(habits):
            if habit and habit.strip():
                self.table.setItem(idx, 0, QTableWidgetItem(habit.strip()))
        return len(habits)

    def apply_checkbox_states(self, states: dict):
        """Restore saved checkbox states without triggering saves."""
        was_enabled = self.enable_checkbox_save
        self.enable_checkbox_save = False
        for col in range(1, 8):
            for row in range(MAX_ROWS):
                cb = self.table.cellWidget(row, col)
                if isinstance(cb, QCheckBox):
                    key = f"{row},{col}"
                    if key in states:
                        cb.setChecked(states[key])
        self.enable_checkbox_save = was_enabled

    def clear_input(self):
        self.input.clear()

    def next_empty_row(self) -> int:
        """Return the first row index where column 0 is empty."""
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item is None or not item.text().strip():
                return r
        return self.table.rowCount() - 1

    # ------------------------------------------------------------------
    # Internal signal dispatchers
    # ------------------------------------------------------------------
    def _on_checkbox_state_changed(self, row: int, col: int, state: int):
        if not self.enable_checkbox_save:
            return
        if state != 2:       # only fire on checked, not unchecked
            return
        day_item = self.table.horizontalHeaderItem(col)
        subject_item = self.table.item(row, 0)
        if not day_item or not subject_item:
            return
        day     = day_item.text()
        subject = subject_item.text()
        if not subject.strip():
            return
        self.checkbox_toggled.emit(row, col, day, subject)

    def _submit_habit(self):
        self.habit_submitted.emit(self.input.text())

    def _show_context_menu(self, pos):
        idx = self.table.indexAt(pos)
        if not idx.isValid() or idx.column() != 0:
            return
        item = self.table.item(idx.row(), 0)
        if item is None or not item.text().strip():
            return

        subject = item.text()
        menu = QMenu(self)
        edit_action   = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == edit_action:
            self.context_edit_requested.emit(idx.row(), subject)
        elif action == delete_action:
            self.context_delete_requested.emit(idx.row(), subject)
