"""
ui/reminder_panel.py

Drop-in widget for the Autodidex shell. Mirrors the NotesSide pattern:
a QCalendarWidget drives selection, a side list shows detail for the
selected day, and everything is kept in sync with ReminderService via
signals rather than direct DB calls.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, QTimeEdit,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
    QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QDateTime, QTime, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QIcon, QAction

from calender.services.reminder_service import ReminderService


class ReminderPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = ReminderService()

        self._build_ui()
        self._build_tray()
        self._wire_signals()

        self._refresh_calendar_marks()
        self._refresh_day_list(self.calendar.selectedDate())

    # --- UI construction ------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)

        self.day_label = QLabel()
        self.day_label.setStyleSheet("font-weight: 600; margin-top: 4px;")
        layout.addWidget(self.day_label)

        self.day_list = QListWidget()
        layout.addWidget(self.day_list)

        input_row = QHBoxLayout()
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Reminder text…")
        self.text_input.returnPressed.connect(self._add_reminder)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_reminder)

        input_row.addWidget(self.time_edit)
        input_row.addWidget(self.text_input, stretch=1)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._delete_selected)
        layout.addWidget(delete_btn)

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(QIcon.fromTheme("appointment-new"), self)
        menu = QMenu()
        show_action = QAction("Open Autodidex", self)
        show_action.triggered.connect(self.window().show)
        menu.addAction(show_action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _wire_signals(self) -> None:
        self.calendar.selectionChanged.connect(
            lambda: self._refresh_day_list(self.calendar.selectedDate())
        )
        self.service.reminder_due.connect(self._on_reminder_due)
        self.service.reminders_changed.connect(self._refresh_calendar_marks)
        self.service.reminders_changed.connect(
            lambda: self._refresh_day_list(self.calendar.selectedDate())
        )

    # --- actions ----------------------------------------------------------

    def _add_reminder(self) -> None:
        text = self.text_input.text().strip()
        if not text:
            return
        dt = QDateTime(self.calendar.selectedDate(), self.time_edit.time())
        self.service.add_reminder(text, dt)
        self.text_input.clear()

    def _delete_selected(self) -> None:
        item = self.day_list.currentItem()
        if item is None:
            return
        reminder_id = item.data(Qt.UserRole)
        self.service.delete_reminder(reminder_id)

    def _on_reminder_due(self, reminder_id: int, text: str) -> None:
        self.tray.showMessage("Reminder", text, QSystemTrayIcon.Information, 10_000)

    # --- rendering ----------------------------------------------------------

    def _refresh_day_list(self, date: QDate) -> None:
        self.day_label.setText(f"Reminders — {date.toString('dddd, d MMMM yyyy')}")
        self.day_list.clear()
        for row in self.service.reminders_for_date(date):
            dt = QDateTime.fromString(row["remind_at"], "yyyy-MM-ddTHH:mm:ss")
            status = "✓ fired" if row["fired"] else dt.time().toString("HH:mm")
            item = QListWidgetItem(f"{status} — {row['text']}")
            item.setData(Qt.UserRole, row["id"])
            if row["fired"]:
                item.setForeground(QColor("gray"))
            self.day_list.addItem(item)

    def _refresh_calendar_marks(self) -> None:
        # Clear previous formatting, then bold/color any date with a pending reminder.
        default_format = QTextCharFormat()
        self.calendar.setDateTextFormat(QDate(), default_format)

        marked_format = QTextCharFormat()
        marked_format.setFontWeight(75)  # bold
        marked_format.setForeground(QColor("#e07b39"))  # matches Onyx Crown gold-ish accent

        for date_str in self.service.dates_with_reminders():
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.calendar.setDateTextFormat(date, marked_format)