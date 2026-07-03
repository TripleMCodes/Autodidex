"""

A standalone PySide6 widget that renders a bar chart of check-in counts
using QtCharts — no matplotlib dependency, so it's lighter to ship and
renders natively inside the Qt widget tree (theming, DPI scaling, and
resizing all come for free).

Decoupled from HabitService on purpose — it only knows about a plain
dict of {label: count}, so it can be dropped into any app (habit
tracker, Autodidex dashboard, M Sona, etc.) without pulling in
habit_tracker as a dependency.

Two ways to feed it data:

  1. widget.set_data({"Read": 12, "Gym": 7, "Meditate": 20})
  2. widget.load_from(habit_service)   # duck-typed: calls
     .get_cp_with_check_marks() on whatever object you pass in
"""

from __future__ import annotations

from typing import Protocol

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis,
)


class SupportsCheckMarkCounts(Protocol):
    """Duck-typing contract — anything with this method works with load_from()."""
    def get_cp_with_check_marks(self) -> dict[str, int]: ...


class HabitBarChartWidget(QWidget):
    """Embeddable bar chart of habit/check-in counts, built on QtCharts."""

    # Emitted whenever set_data() is called with an empty/None dict,
    # so a host app can react (e.g. show its own onboarding hint)
    # instead of this widget popping a dialog on someone else's window.
    no_data = Signal()

    def __init__(
        self,
        title: str = "Habit Completion Frequency",
        bar_color: str = "#9370DB",  # mediumpurple
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._title = title
        self._bar_color = QColor(bar_color)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._chart = QChart()
        self._chart.setTitle(self._title)
        self._chart.setTitleFont(QFont(self._chart.titleFont().family(), 14, QFont.Bold))
        self._chart.legend().hide()
        self._chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self._chart_view)

        # Shown in place of the chart when there's nothing to plot yet.
        self._empty_label = QLabel("No data to display yet.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(self._empty_label)
        self._empty_label.hide()

    # --- public API -------------------------------------------------------

    def set_data(self, counts: dict[str, int] | None) -> None:
        """Redraw the chart from a plain {label: count} dict."""
        print(f"the count is: {counts}")
        if not counts:
            self._show_empty_state()
            self.no_data.emit()
            return

        self._empty_label.hide()
        self._chart_view.show()
        self._chart.removeAllSeries()
        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        labels = list(counts.keys())
        values = list(counts.values())

        bar_set = QBarSet("Check-ins")
        bar_set.append(values)
        bar_set.setColor(self._bar_color)
        bar_set.setLabelColor(QColor("black"))

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)  # shows the count on top of each bar
        self._chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        self._chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Check-ins")
        axis_y.setRange(0, max(values) * 1.15)  # explicit range avoids relying on
        axis_y.setTickCount(6)                  # auto-sizing before the view has laid out
        self._chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

    def load_from(self, source: SupportsCheckMarkCounts) -> None:
        """Convenience wrapper — pulls data from any object exposing
        get_cp_with_check_marks(), e.g. HabitService(), without this
        module importing habit_tracker directly."""
        self.set_data(source.get_cp_with_check_marks())

    def clear(self) -> None:
        self._show_empty_state()

    # --- internal -----------------------------------------------------

    def _show_empty_state(self) -> None:
        self._chart.removeAllSeries()
        self._chart_view.hide()
        self._empty_label.show()