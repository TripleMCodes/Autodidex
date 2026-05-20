from datetime import date, timedelta

from PySide6.QtWidgets import (
    QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from calender.services.color_service import ColorService


class HeatmapWidget(QWidget):
    """
    Pure visual component — renders a GitHub-style contribution grid.

    Receives already-parsed data; does zero I/O.
    Columns = weeks, rows = days (Sunday → Saturday).
    """

    def __init__(
        self,
        study_data: dict[date, int],
        start_date: date,
        end_date: date,
        parent=None,
    ):
        super().__init__(parent)
        self._colors = ColorService()
        self._build_grid(study_data, start_date, end_date)

    # ------------------------------------------------------------------
    def _build_grid(
        self,
        study_data: dict[date, int],
        start_date: date,
        end_date: date,
    ):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #ba9dcab0; }")

        grid = QGridLayout(container)
        grid.setSpacing(4)

        # Rewind to the nearest Sunday so the grid aligns like GitHub
        current = start_date
        while current.weekday() != 6:   # 6 = Sunday in Python's Mon=0 scheme
            current -= timedelta(days=1)

        column = 0
        while current <= end_date:
            for row in range(7):
                day = current + timedelta(days=row)
                if day > end_date:
                    break
                count  = study_data.get(day, 0)
                colour = self._colors.get(count)

                cell = QLabel()
                cell.setFixedSize(20, 20)
                cell.setStyleSheet(
                    f"background-color: {colour}; border-radius: 3px; color: black;"
                )
                cell.setToolTip(f"{day.isoformat()}\nSessions: {count}")
                grid.addWidget(cell, row, column)

            current += timedelta(days=7)
            column  += 1

        scroll.setWidget(container)
        layout.addWidget(scroll)
