"""
Monitoring & Analytics Page for Bower GUI
Displays real-time metrics, performance data, and system health.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

from src.gui.styles.theme import COLORS, SPACING
from src.gui.components.cards import StatCard
from src.gui.components.tables import DataTable
from src.gui.components.common import Spinner, EmptyState
from src.gui.components.buttons import Button, ButtonVariant
from src.gui.components.charts import LineChart, BarChart


@dataclass
class MetricData:
    """Metric data point."""
    label: str
    value: float
    unit: str = ""
    trend: str = "up"  # up, down, stable
    change_percent: float = 0.0


class MonitoringPage:
    """Monitoring and analytics dashboard page."""

    def __init__(self, app):
        self.app = app
        self.window_id: Optional[str] = None
        self._refresh_interval = 5000
        self._is_refreshing = False
        self._metrics: dict[str, Any] = {}
        self._charts: dict = {}

    def create(self):
        """Create the monitoring page."""
        with dpg.window(
            tag="monitoring_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "monitoring_window"
            self._create_content()

    def _create_content(self):
        """Create main content area."""
        with dpg.group(horizontal=True):
            self._create_sidebar()
            self._create_main_panel()

    def _create_sidebar(self):
        """Create sidebar navigation."""
        with dpg.child_window(
            tag="monitoring_sidebar",
            width=220,
            height=-1,
            border=False,
        ):
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
            )
            dpg.add_text("Monitoring", color=COLORS["text_secondary"])
            dpg.add_separator()
            dpg.add_text(" ")

            nav_items = [
                ("Dashboard", "nav_monitoring_dashboard"),
                ("Sessions", "nav_monitoring_sessions"),
                ("Proxies", "nav_monitoring_proxies"),
                ("Performance", "nav_monitoring_performance"),
                ("Logs", "nav_monitoring_logs"),
            ]

            for label, tag in nav_items:
                dpg.add_button(
                    label=label,
                    tag=tag,
                    width=190,
                    callback=lambda s=tag: self._handle_navigation(s),
                )

            dpg.add_spacer()
            dpg.add_text(" ")

            with dpg.group():
                dpg.add_text("Auto Refresh", color=COLORS["text_secondary"])
                dpg.add_checkbox(
                    tag="auto_refresh_checkbox",
                    label="Enable",
                    default_value=True,
                    callback=self._toggle_auto_refresh,
                )

            dpg.add_spacer()
            dpg.add_button(
                label="Refresh Now",
                tag="btn_refresh_metrics",
                width=190,
                callback=self._refresh_metrics,
            )

    def _create_main_panel(self):
        """Create main monitoring panel."""
        with dpg.group():
            with dpg.child_window(
                tag="monitoring_main",
                width=-1,
                height=-1,
                border=False,
            ):
                dpg.add_text(
                    "System Monitoring",
                    color=COLORS["text_primary"],
                )
                dpg.add_text(
                    "Real-time performance metrics and health status",
                    color=COLORS["text_secondary"],
                )
                dpg.add_text(" ")

                self._create_metric_cards()
                dpg.add_text(" ")

                self._create_charts_section()
                dpg.add_text(" ")

                self._create_sessions_table()
                dpg.add_text(" ")

                self._create_proxy_health_section()

    def _create_metric_cards(self):
        """Create metric summary cards."""
        with dpg.group(horizontal=True):
            cards_data = [
                ("Active Sessions", "12", "sessions", "up"),
                ("CPU Usage", "34%", "cpu", "down"),
                ("Memory Usage", "2.4 GB", "memory", "stable"),
                ("Network I/O", "145 MB", "network", "up"),
                ("Proxy Health", "98%", "health", "up"),
                ("Uptime", "99.9%", "uptime", "stable"),
            ]

            for title, value, icon, trend in cards_data:
                self._create_metric_card(title, value, icon, trend)

    def _create_metric_card(self, title: str, value: str, icon: str, trend: str):
        """Create a single metric card."""
        trend_colors = {
            "up": COLORS["success"],
            "down": COLORS["danger"],
            "stable": COLORS["text_secondary"],
        }

        with dpg.group():
            with dpg.child_window(
                tag=f"metric_{title.replace(' ', '_').lower()}",
                width=180,
                height=100,
                border=True,
            ):
                dpg.add_text(
                    title,
                    color=COLORS["text_secondary"],
                )
                dpg.add_text(" ")
                dpg.add_text(
                    value,
                    color=COLORS["text_primary"],
                )
                dpg.add_text(" ")
                dpg.add_text(
                    f"{'↑' if trend == 'up' else '↓' if trend == 'down' else '→'} {trend}",
                    color=trend_colors.get(trend, COLORS["text_secondary"]),
                )

    def _create_charts_section(self):
        """Create charts section."""
        with dpg.group():
            dpg.add_text(
                "Performance Charts",
                color=COLORS["text_primary"],
            )
            dpg.add_text(" ")

            with dpg.group(horizontal=True):
                self._create_cpu_chart()
                self._create_memory_chart()
                self._create_network_chart()

    def _create_cpu_chart(self):
        """Create CPU usage chart."""
        with dpg.group():
            with dpg.child_window(
                tag="cpu_chart",
                width=350,
                height=200,
                border=True,
            ):
                dpg.add_text("CPU Usage", color=COLORS["text_primary"])
                dpg.add_text(" ")

                with dpg.plot(
                    tag="cpu_plot",
                    width=320,
                    height=160,
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisX,
                        tag="cpu_x_axis",
                        label="Time",
                    )
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisY,
                        tag="cpu_y_axis",
                        label="%",
                        min_scale=0,
                        max_scale=100,
                    )

                    dpg.add_line_series(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        [45, 42, 38, 35, 40, 42, 38, 36, 34, 32],
                        label="CPU %",
                        tag="cpu_series",
                        parent="cpu_y_axis",
                    )

    def _create_memory_chart(self):
        """Create memory usage chart."""
        with dpg.group():
            with dpg.child_window(
                tag="memory_chart",
                width=350,
                height=200,
                border=True,
            ):
                dpg.add_text("Memory Usage", color=COLORS["text_primary"])
                dpg.add_text(" ")

                with dpg.plot(
                    tag="memory_plot",
                    width=320,
                    height=160,
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisX,
                        tag="memory_x_axis",
                        label="Time",
                    )
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisY,
                        tag="memory_y_axis",
                        label="MB",
                        min_scale=0,
                        max_scale=4096,
                    )

                    dpg.add_line_series(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        [2048, 2100, 2200, 2150, 2300, 2400, 2350, 2450, 2500, 2450],
                        label="Memory MB",
                        tag="memory_series",
                        parent="memory_y_axis",
                    )

    def _create_network_chart(self):
        """Create network traffic chart."""
        with dpg.group():
            with dpg.child_window(
                tag="network_chart",
                width=350,
                height=200,
                border=True,
            ):
                dpg.add_text("Network I/O", color=COLORS["text_primary"])
                dpg.add_text(" ")

                with dpg.plot(
                    tag="network_plot",
                    width=320,
                    height=160,
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisX,
                        tag="network_x_axis",
                        label="Time",
                    )
                    dpg.add_plot_axis(
                        dpg.mvPlotAxisY,
                        tag="network_y_axis",
                        label="KB/s",
                        min_scale=0,
                    )

                    dpg.add_line_series(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        [120, 145, 132, 156, 168, 155, 172, 165, 180, 175],
                        label="Download",
                        tag="network_download_series",
                        parent="network_y_axis",
                    )
                    dpg.add_line_series(
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        [45, 52, 48, 55, 62, 58, 65, 60, 68, 72],
                        label="Upload",
                        tag="network_upload_series",
                        parent="network_y_axis",
                    )

    def _create_sessions_table(self):
        """Create sessions monitoring table."""
        with dpg.group():
            dpg.add_text(
                "Active Sessions",
                color=COLORS["text_primary"],
            )
            dpg.add_text(" ")

            with dpg.table(
                tag="sessions_monitor_table",
                resizable=True,
                reorderable=True,
                sortable=True,
                headers=[
                    "Session ID",
                    "Profile",
                    "Status",
                    "CPU",
                    "Memory",
                    "Network",
                    "Duration",
                ],
                widths=[150, 150, 100, 80, 80, 80, 100],
            ):
                sample_data = [
                    ("sess_001", "Profile 1", "Running", "12%", "256MB", "1.2MB/s", "00:15:30"),
                    ("sess_002", "Profile 2", "Running", "8%", "192MB", "0.8MB/s", "00:10:22"),
                    ("sess_003", "Profile 3", "Idle", "2%", "128MB", "0.1MB/s", "00:45:10"),
                ]

                for row in sample_data:
                    with dpg.table_row():
                        for cell in row:
                            dpg.add_text(cell, color=COLORS["text_primary"])

    def _create_proxy_health_section(self):
        """Create proxy health monitoring section."""
        with dpg.group():
            dpg.add_text(
                "Proxy Health",
                color=COLORS["text_primary"],
            )
            dpg.add_text(" ")

            with dpg.table(
                tag="proxy_health_table",
                resizable=True,
                headers=["Proxy", "Status", "Latency", "Success Rate", "Country"],
                widths=[200, 100, 100, 120, 100],
            ):
                proxy_data = [
                    ("us-east-1.proxy.com", "Online", "45ms", "99.8%", "US"),
                    ("eu-west-1.proxy.com", "Online", "82ms", "98.5%", "DE"),
                    ("ap-south-1.proxy.com", "Online", "120ms", "97.2%", "IN"),
                    ("sa-east-1.proxy.com", "Offline", "-", "0%", "BR"),
                ]

                for row in proxy_data:
                    with dpg.table_row():
                        for i, cell in enumerate(row):
                            color = (
                                COLORS["success"]
                                if cell == "Online"
                                else COLORS["danger"]
                                if cell == "Offline"
                                else COLORS["text_primary"]
                            )
                            dpg.add_text(cell, color=color)

    def _handle_navigation(self, tag: str):
        """Handle navigation clicks."""
        page_map = {
            "nav_monitoring_dashboard": "dashboard",
            "nav_monitoring_sessions": "sessions",
            "nav_monitoring_proxies": "proxies",
            "nav_monitoring_performance": "monitoring",
            "nav_monitoring_logs": "logs",
        }
        page = page_map.get(tag)
        if page and self.app:
            self.app.navigate(page)

    def _toggle_auto_refresh(self, sender, app_data):
        """Toggle automatic refresh."""
        self._is_refreshing = app_data
        if self._is_refreshing:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _start_auto_refresh(self):
        """Start automatic refresh."""
        if hasattr(self, '_refresh_task'):
            return
        self._is_refreshing = True

    def _stop_auto_refresh(self):
        """Stop automatic refresh."""
        self._is_refreshing = False

    def _refresh_metrics(self):
        """Manually refresh metrics."""
        pass

    def update_metrics(self, metrics: dict):
        """Update displayed metrics."""
        self._metrics = metrics

    def destroy(self):
        """Clean up resources."""
        self._stop_auto_refresh()
        if self.window_id:
            dpg.delete_item(self.window_id)


def create_monitoring_page(app) -> MonitoringPage:
    """Factory function to create monitoring page."""
    return MonitoringPage(app)
