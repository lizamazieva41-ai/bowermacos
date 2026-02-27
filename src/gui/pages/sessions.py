"""
Sessions Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class SessionsPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None
        self.view_mode = "list"  # grid or list

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
            )
            dpg.add_text("Antidetect Browser", color=COLORS["text_secondary"])
            dpg.add_separator()
            dpg.add_text(" ")

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
                dpg.add_text("API Status", color=COLORS["text_muted"])
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
            with dpg.group(horizontal=True):
                dpg.add_text("Sessions")
                dpg.add_text("", width=-1)
                
                self.create_view_toggle()
                
                dpg.add_button(
                    label="Refresh",
                    tag="refresh_sessions_btn",
                    callback=self.refresh,
                )
                dpg.add_button(
                    label="Session Actions",
                    tag="session_actions_btn",
                    callback=self.show_session_actions_modal,
                )

            dpg.add_text(" ")

            with dpg.child_window(tag="sessions_list", height=-250):
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

            dpg.add_text(" ")
            dpg.add_text("Session Controls")
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    label="Session ID",
                    tag="action_session_id",
                    width=250,
                    hint="Enter session ID",
                )
                dpg.add_input_text(
                    label="URL / Script",
                    tag="action_input",
                    width=400,
                    hint="https://example.com or JavaScript",
                )

            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Navigate",
                    tag="navigate_btn",
                    callback=self.do_navigate,
                )
                dpg.add_button(
                    label="Screenshot",
                    tag="screenshot_btn",
                    callback=self.do_screenshot,
                )
                dpg.add_button(
                    label="Execute JS",
                    tag="execute_btn",
                    callback=self.do_execute,
                )
                dpg.add_button(
                    label="Click",
                    tag="click_btn",
                    callback=self.show_click_modal,
                )
                dpg.add_button(
                    label="Type Text",
                    tag="type_btn",
                    callback=self.show_type_modal,
                )

            dpg.add_text(" ")
            dpg.add_text("Console Output")
            dpg.add_text(" ")
            with dpg.child_window(tag="console_output", height=150):
                dpg.add_text(
                    "Console output will appear here...",
                    tag="console_text",
                    color=COLORS["text_muted"],
                )

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
                tag="sessions_view_grid",
                width=35,
                height=30,
                callback=lambda: self.set_view_mode("grid"),
            )
            list_btn = dpg.add_button(
                label="☰",
                tag="sessions_view_list",
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
        
        if dpg.does_item_exist("sessions_view_grid"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, grid_color)
            dpg.bind_item_theme("sessions_view_grid", theme)
        
        if dpg.does_item_exist("sessions_view_list"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, list_color)
            dpg.bind_item_theme("sessions_view_list", theme)

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

    def show_session_actions_modal(self):
        session_id = dpg.get_value("action_session_id")
        if not session_id:
            print("Please enter a session ID")
            return
        
        try:
            session = self.app.api_client.get_session(session_id)
            if session:
                print(f"Session: {session.get('session_id')}, Status: {session.get('status')}")
            else:
                print("Session not found")
        except Exception as e:
            print(f"Error: {e}")

    def do_navigate(self):
        session_id = dpg.get_value("action_session_id")
        url = dpg.get_value("action_input")
        
        if not session_id or not url:
            print("Please enter session ID and URL")
            return
        
        try:
            self.app.api_client.navigate(session_id, url)
            self.update_console(f"Navigated to: {url}")
        except Exception as e:
            self.update_console(f"Error: {e}")

    def do_screenshot(self):
        import datetime
        session_id = dpg.get_value("action_session_id")
        
        if not session_id:
            print("Please enter session ID")
            return
        
        try:
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.app.api_client.screenshot(session_id, filename)
            self.update_console(f"Screenshot saved: {filename}")
        except Exception as e:
            self.update_console(f"Error: {e}")

    def do_execute(self):
        session_id = dpg.get_value("action_session_id")
        script = dpg.get_value("action_input")
        
        if not session_id or not script:
            print("Please enter session ID and script")
            return
        
        try:
            result = self.app.api_client.execute_script(session_id, script)
            self.update_console(f"Result: {result}")
        except Exception as e:
            self.update_console(f"Error: {e}")

    def show_click_modal(self):
        with dpg.modal(tag="click_modal", label="Click Element"):
            dpg.add_input_text(
                label="Selector",
                tag="click_selector",
                width=300,
                hint="#button-id or .class-name",
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Click",
                    callback=self.do_click,
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("click_modal"),
                )

    def do_click(self):
        session_id = dpg.get_value("action_session_id")
        selector = dpg.get_value("click_selector")
        
        if not session_id or not selector:
            print("Please enter session ID and selector")
            return
        
        try:
            self.app.api_client.click(session_id, selector)
            dpg.close_modal("click_modal")
            self.update_console(f"Clicked: {selector}")
        except Exception as e:
            self.update_console(f"Error: {e}")

    def show_type_modal(self):
        with dpg.modal(tag="type_modal", label="Type Text"):
            dpg.add_input_text(
                label="Selector",
                tag="type_selector",
                width=300,
                hint="#input-id",
            )
            dpg.add_input_text(
                label="Text",
                tag="type_text",
                width=300,
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Type",
                    callback=self.do_type,
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("type_modal"),
                )

    def do_type(self):
        session_id = dpg.get_value("action_session_id")
        selector = dpg.get_value("type_selector")
        text = dpg.get_value("type_text")
        
        if not session_id or not selector or not text:
            print("Please enter session ID, selector, and text")
            return
        
        try:
            self.app.api_client.type_text(session_id, selector, text)
            dpg.close_modal("type_modal")
            self.update_console(f"Typed: {text} into {selector}")
        except Exception as e:
            self.update_console(f"Error: {e}")

    def update_console(self, message: str):
        if dpg.does_item_exist("console_text"):
            current = dpg.get_value("console_text")
            if "Console output will appear here..." in current:
                current = ""
            new_text = f"{current}\n{message}"[-1000:]
            dpg.set_value("console_text", new_text)

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)
            self.refresh()

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
