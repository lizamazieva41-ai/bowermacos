"""
Charts components for Bower GUI
Provides line charts, bar charts, and other visualization components.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass

from src.gui.styles.theme import COLORS


@dataclass
class ChartConfig:
    """Configuration for charts."""
    width: int = 400
    height: int = 300
    title: str = ""
    show_legend: bool = True
    show_grid: bool = True
    animate: bool = True


class LineChart:
    """Line chart component."""

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self.tag = f"line_chart_{id(self)}"
        self.series: List[Tuple[str, List[float], str]] = []

    def add_series(
        self,
        name: str,
        data: List[float],
        color: Optional[str] = None
    ):
        """Add a data series."""
        self.series.append((name, data, color or COLORS["accent"]))

    def render(self) -> str:
        """Render the chart."""
        with dpg.plot(
            tag=self.tag,
            width=self.config.width,
            height=self.config.height,
        ):
            if self.config.show_legend:
                dpg.add_plot_legend()

            dpg.add_plot_axis(
                dpg.mvPlotAxisX,
                tag=f"{self.tag}_x",
                label="X",
            )
            dpg.add_plot_axis(
                dpg.mvPlotAxisY,
                tag=f"{self.tag}_y",
                label="Y",
            )

            x_values = list(range(len(self.series[0][1]) if self.series else [0]))

            for name, data, color in self.series:
                dpg.add_line_series(
                    x_values,
                    data,
                    label=name,
                    parent=f"{self.tag}_y",
                    color=_parse_color(color),
                )

        return self.tag


class BarChart:
    """Bar chart component."""

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self.tag = f"bar_chart_{id(self)}"
        self.labels: List[str] = []
        self.values: List[float] = []
        self.color = COLORS["accent"]

    def set_data(self, labels: List[str], values: List[float], color: Optional[str] = None):
        """Set chart data."""
        self.labels = labels
        self.values = values
        self.color = color or COLORS["accent"]

    def render(self) -> str:
        """Render the chart."""
        with dpg.plot(
            tag=self.tag,
            width=self.config.width,
            height=self.config.height,
        ):
            if self.config.show_legend:
                dpg.add_plot_legend()

            dpg.add_plot_axis(
                dpg.mvPlotAxisX,
                tag=f"{self.tag}_x",
                label="",
            )
            dpg.add_plot_axis(
                dpg.mvPlotAxisY,
                tag=f"{self.tag}_y",
                label="Value",
            )

            x_values = list(range(len(self.values)))

            dpg.add_bar_series(
                x_values,
                self.values,
                label="Value",
                parent=f"{self.tag}_y",
                color=_parse_color(self.color),
            )

        return self.tag


class PieChart:
    """Pie chart component."""

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self.tag = f"pie_chart_{id(self)}"
        self.data: List[Tuple[str, float, str]] = []

    def add_segment(self, label: str, value: float, color: str):
        """Add a pie segment."""
        self.data.append((label, value, color))

    def render(self) -> str:
        """Render the pie chart."""
        colors = [
            COLORS["accent"],
            COLORS["success"],
            COLORS["warning"],
            COLORS["danger"],
            "#8B5CF6",
            "#EC4899",
            "#06B6D4",
        ]

        total = sum(v for _, v, _ in self.data)

        with dpg.group(tag=self.tag):
            for i, (label, value, _) in enumerate(self.data):
                percentage = (value / total * 100) if total > 0 else 0
                color = colors[i % len(colors)]

                with dpg.group(horizontal=True, horizontal_spacing=10):
                    dpg.add_text(
                        "●",
                        color=color,
                    )
                    dpg.add_text(
                        f"{label}: {value} ({percentage:.1f}%)",
                        color=COLORS["text_primary"],
                    )

        return self.tag


class GaugeChart:
    """Gauge chart component."""

    def __init__(self, value: float = 0.0, max_value: float = 100.0):
        self.value = value
        self.max_value = max_value
        self.tag = f"gauge_{id(self)}"

    def render(self) -> str:
        """Render gauge chart."""
        percentage = (self.value / self.max_value) if self.max_value > 0 else 0

        color = (
            COLORS["success"] if percentage < 0.6
            else COLORS["warning"] if percentage < 0.85
            else COLORS["danger"]
        )

        with dpg.group(tag=self.tag, horizontal=True):
            dpg.add_text(
                f"{self.value:.1f}",
                color=color,
            )
            dpg.add_text(
                f"/ {self.max_value}",
                color=COLORS["text_secondary"],
            )

        return self.tag


class Sparkline:
    """Sparkline chart for inline data visualization."""

    def __init__(self, data: List[float], color: Optional[str] = None):
        self.data = data
        self.color = color or COLORS["accent"]
        self.tag = f"sparkline_{id(self)}"

    def render(self) -> str:
        """Render sparkline."""
        with dpg.plot(
            tag=self.tag,
            width=100,
            height=30,
            no_title=True,
            no_mouse_pos=True,
        ):
            dpg.add_plot_axis(dpg.mvPlotAxisX, no_gridlines=True)
            dpg.add_plot_axis(dpg.mvPlotAxisY, no_gridlines=True)

            x_values = list(range(len(self.data)))

            dpg.add_line_series(
                x_values,
                self.data,
                parent=dpg.last_item(),
                color=_parse_color(self.color),
            )

        return self.tag


class Heatmap:
    """Heatmap component."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data: List[List[float]] = [[0] * cols for _ in range(rows)]
        self.tag = f"heatmap_{id(self)}"
        self.color_scale = [COLORS["success"], COLORS["warning"], COLORS["danger"]]

    def set_cell(self, row: int, col: int, value: float):
        """Set a cell value."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.data[row][col] = value

    def render(self) -> str:
        """Render heatmap."""
        with dpg.group(tag=self.tag):
            pass

        return self.tag


def _parse_color(color: str) -> tuple:
    """Parse color string to tuple."""
    color_map = {
        "accent": (59, 130, 246, 255),
        "primary": (99, 102, 241, 255),
        "success": (34, 197, 94, 255),
        "warning": (234, 179, 8, 255),
        "danger": (239, 68, 68, 255),
    }

    if color in color_map:
        return color_map[color]

    if color.startswith("#") and len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return (r, g, b, 255)

    return (128, 128, 128, 255)


def create_line_chart(
    data: List[float],
    title: str = "",
    width: int = 400,
    height: int = 300,
) -> LineChart:
    """Factory function to create a line chart."""
    config = ChartConfig(title=title, width=width, height=height)
    chart = LineChart(config)
    chart.add_series("Data", data)
    return chart


def create_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    width: int = 400,
    height: int = 300,
) -> BarChart:
    """Factory function to create a bar chart."""
    config = ChartConfig(title=title, width=width, height=height)
    chart = BarChart(config)
    chart.set_data(labels, values)
    return chart


def create_gauge(value: float, max_value: float = 100.0) -> GaugeChart:
    """Factory function to create a gauge."""
    return GaugeChart(value, max_value)
