"""
Dashboard Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class DashboardPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None
        self.view_mode = "grid"  # grid or list
        self._view_toggle = None
        self.sidebar_id = None

    def create(self):
        with dpg.window(
            tag="dashboard_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "dashboard_window"

            with dpg.group(horizontal=True):
                self.create_sidebar()
                self.create_main_content()

    def create_sidebar(self):
        with dpg.child_window(
            tag="sidebar",
            width=220,
            height=-1,
            border=False,
        ):
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
            )
            dpg.add_text("Antidetect Browser", color=COLORS["text_secondary"])
            dpg.add_separator()
            dpg.add_text(" ")

            dpg.add_button(
                label="Dashboard",
                tag="nav_dashboard",
                width=190,
                callback=lambda: self.navigate("dashboard"),
            )
            dpg.add_button(
                label="Profiles",
                tag="nav_profiles",
                width=190,
                callback=lambda: self.navigate("profiles"),
            )
            dpg.add_button(
                label="Sessions",
                tag="nav_sessions",
                width=190,
                callback=lambda: self.navigate("sessions"),
            )
            dpg.add_button(
                label="Proxies",
                tag="nav_proxies",
                width=190,
                callback=lambda: self.navigate("proxies"),
            )
            dpg.add_button(
                label="Settings",
                tag="nav_settings",
                width=190,
                callback=lambda: self.navigate("settings"),
            )

            dpg.add_spacer()

            dpg.add_separator()

            with dpg.group():
                dpg.add_text("API Status", color=COLORS["text_muted"])
                dpg.add_text(
                    "Connected",
                    tag="api_status",
                    color=COLORS["success"],
                )

            dpg.add_button(
                label="Logout",
                tag="logout_btn",
                width=190,
                callback=self.logout,
            )

    def create_main_content(self):
        with dpg.child_window(
            tag="main_content",
            width=-1,
            height=-1,
            border=False,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Dashboard")
                dpg.add_text("", width=-1)
                
                self.create_view_toggle()
                
                dpg.add_button(
                    label="🔄",
                    tag="refresh_dashboard_btn",
                    width=35,
                    callback=self.refresh,
                )
            
            dpg.add_text(
                "Overview of your browser profiles and sessions",
                color=COLORS["text_secondary"],
            )
            dpg.add_separator()
            dpg.add_text(" ")

            with dpg.group(horizontal=True):
                self.create_stat_card(
                    "Active Sessions",
                    "0",
                    "sessions_count",
                    COLORS["primary"],
                )
                self.create_stat_card(
                    "Total Profiles",
                    "0",
                    "profiles_count",
                    COLORS["success"],
                )
                self.create_stat_card(
                    "CPU Usage",
                    "0%",
                    "cpu_usage",
                    COLORS["warning"],
                )
                self.create_stat_card(
                    "Memory Usage",
                    "0%",
                    "memory_usage",
                    (168, 85, 247),
                )

            dpg.add_text(" ")
            dpg.add_text("Quick Actions")
            dpg.add_text(" ")

            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="➕ New Profile",
                    tag="quick_new_profile",
                    width=150,
                    callback=lambda: self.navigate("profiles"),
                )
                dpg.add_button(
                    label="🌐 New Session",
                    tag="quick_new_session",
                    width=150,
                    callback=lambda: self.navigate("profiles"),
                )
                dpg.add_button(
                    label="🔗 Add Proxy",
                    tag="quick_add_proxy",
                    width=150,
                    callback=lambda: self.navigate("proxies"),
                )
                dpg.add_button(
                    label="⚙️ Settings",
                    tag="quick_settings",
                    width=150,
                    callback=lambda: self.navigate("settings"),
                )

            dpg.add_text(" ")
            dpg.add_text("Recent Sessions")
            dpg.add_text(" ")

            with dpg.child_window(tag="recent_sessions", height=300):
                dpg.add_text(
                    "No active sessions",
                    tag="no_sessions_text",
                    color=COLORS["text_muted"],
                )
                with dpg.table(
                    tag="sessions_table",
                    header_row=True,
                    resizable=True,
                    show=False,
                ):
                    dpg.add_table_column(label="Session ID")
                    dpg.add_table_column(label="Profile")
                    dpg.add_table_column(label="Status")
                    dpg.add_table_column(label="Started")

    def create_stat_card(self, title, value, tag, color):
        with dpg.child_window(
            tag=f"stat_{tag}",
            width=200,
            height=100,
        ):
            dpg.add_text(title, color=COLORS["text_secondary"])
            dpg.add_text(value, tag=tag, color=color)

    def navigate(self, page: str):
        self.app.show_page(page)
        if page in self.app.pages:
            self.app.pages[page].refresh()

    def logout(self):
        self.app.logout()

    def create_view_toggle(self):
        """Create view toggle button (grid/list)."""
        with dpg.group(horizontal=True):
            grid_btn = dpg.add_button(
                label="▦",
                tag="dashboard_view_grid",
                width=35,
                height=30,
                callback=lambda: self.set_view_mode("grid"),
            )
            list_btn = dpg.add_button(
                label="☰",
                tag="dashboard_view_list",
                width=35,
                height=30,
                callback=lambda: self.set_view_mode("list"),
            )
        
        self._update_view_toggle_styles()

    def set_view_mode(self, mode: str):
        """Set view mode and refresh display."""
        self.view_mode = mode
        self._update_view_toggle_styles()
        self.refresh()

    def _update_view_toggle_styles(self):
        """Update view toggle button styles."""
        active_color = COLORS.get("primary", (59, 130, 246))
        inactive_color = (100, 100, 100)
        
        grid_color = active_color if self.view_mode == "grid" else inactive_color
        list_color = active_color if self.view_mode == "list" else inactive_color
        
        if dpg.does_item_exist("dashboard_view_grid"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, grid_color)
            dpg.bind_item_theme("dashboard_view_grid", theme)
        
        if dpg.does_item_exist("dashboard_view_list"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, list_color)
            dpg.bind_item_theme("dashboard_view_list", theme)

    def refresh(self):
        try:
            health = self.app.api_client.get_health()
            dpg.set_value("api_status", "Connected")
            dpg.set_value("sessions_count", str(health.get("sessions", 0)))

            profiles = self.app.api_client.get_profiles()
            dpg.set_value("profiles_count", str(len(profiles)))

            metrics = self.app.api_client.get_metrics()
            dpg.set_value("cpu_usage", f"{metrics.get('cpu_percent', 0)}%")
            dpg.set_value("memory_usage", f"{metrics.get('memory_percent', 0)}%")

            sessions = self.app.api_client.get_sessions()
            self.update_sessions_table(sessions)

        except Exception as e:
            dpg.set_value("api_status", "Disconnected")

    def update_sessions_table(self, sessions):
        table = "sessions_table"
        no_sessions = "no_sessions_text"

        if not sessions:
            dpg.hide_item(table)
            dpg.show_item(no_sessions)
            return

        dpg.show_item(table)
        dpg.hide_item(no_sessions)

        for child in dpg.get_item_children(table)[1]:
            dpg.delete_item(child)

        for session in sessions:
            with dpg.table_row(parent=table):
                dpg.add_text(session.get("session_id", ""))
                dpg.add_text(session.get("profile_name", ""))
                dpg.add_text(
                    session.get("status", "unknown"),
                    color=COLORS["success"]
                    if session.get("status") == "active"
                    else COLORS["text_muted"],
                )
                dpg.add_text(session.get("started_at", "")[:19] if session.get("started_at") else "")

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)

    def update(self):
        pass
