"""
Sessions Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class SessionsPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None

    def create(self):
        with dpg.window(
            tag="sessions_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "sessions_window"

            with dpg.group(horizontal=True):
                self.create_sidebar()
                self.create_main_content()

    def create_sidebar(self):
        with dpg.child_window(
            tag="sessions_sidebar",
            width=220,
            height=-1,
            border=False,
        ):
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
                font=28,
            )
            dpg.add_text("Antidetect Browser", color=COLORS["text_secondary"], font=14)
            dpg.add_separator()
            dpg.add_text("", height=10)

            dpg.add_button(
                label="Dashboard",
                width=190,
                callback=lambda: self.navigate("dashboard"),
            )
            dpg.add_button(
                label="Profiles",
                width=190,
                callback=lambda: self.navigate("profiles"),
            )
            dpg.add_button(
                label="Sessions",
                width=190,
            )
            dpg.add_button(
                label="Proxies",
                width=190,
                callback=lambda: self.navigate("proxies"),
            )
            dpg.add_button(
                label="Settings",
                width=190,
                callback=lambda: self.navigate("settings"),
            )

            dpg.add_spacer()
            dpg.add_separator()

            with dpg.group():
                dpg.add_text("API Status", color=COLORS["text_muted"], font=12)
                dpg.add_text("Connected", color=COLORS["success"])

            dpg.add_button(
                label="Logout",
                width=190,
                callback=self.logout,
            )

    def create_main_content(self):
        with dpg.child_window(
            tag="sessions_content",
            width=-1,
            height=-1,
            border=False,
        ):
            dpg.add_text("Sessions", font=28)
            dpg.add_text(
                "Manage active browser sessions",
                color=COLORS["text_secondary"],
            )
            dpg.add_separator()
            dpg.add_text("", height=10)

            dpg.add_button(
                label="Refresh",
                tag="refresh_sessions_btn",
                callback=self.refresh,
            )

            dpg.add_text("", height=15)

            with dpg.child_window(tag="sessions_list", height=-60):
                dpg.add_text(
                    "No active sessions. Create a profile and start a session.",
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
                    dpg.add_table_column(label="Actions")

    def navigate(self, page: str):
        self.app.show_page(page)
        if page in self.app.pages:
            self.app.pages[page].refresh()

    def logout(self):
        self.app.logout()

    def refresh(self):
        try:
            sessions = self.app.api_client.get_sessions()
            self.update_sessions_table(sessions)
        except Exception as e:
            print(f"Error refreshing sessions: {e}")

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
                dpg.add_text(session.get("session_id", "")[:20])
                dpg.add_text(session.get("profile_name", ""))
                dpg.add_text(
                    session.get("status", "unknown"),
                    color=COLORS["success"]
                    if session.get("status") == "active"
                    else COLORS["text_muted"],
                )
                dpg.add_text(session.get("started_at", "")[:19] if session.get("started_at") else "")
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Close",
                        tag=f"close_session_{session.get('session_id')}",
                        small=True,
                        callback=lambda: self.close_session(session.get("session_id")),
                    )

    def close_session(self, session_id: str):
        try:
            self.app.api_client.close_session(session_id)
            self.refresh()
        except Exception as e:
            print(f"Error closing session: {e}")

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)
            self.refresh()

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
