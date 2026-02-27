"""
Profiles Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class ProfilesPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None

    def create(self):
        with dpg.window(
            tag="profiles_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "profiles_window"

            with dpg.group(horizontal=True):
                self.create_sidebar()
                self.create_main_content()

    def create_sidebar(self):
        with dpg.child_window(
            tag="profiles_sidebar",
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
            )
            dpg.add_button(
                label="Sessions",
                width=190,
                callback=lambda: self.navigate("sessions"),
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
            tag="profiles_content",
            width=-1,
            height=-1,
            border=False,
        ):
            dpg.add_text("Profiles")
            dpg.add_text(
                "Manage your browser profiles",
                color=COLORS["text_secondary"],
            )
            dpg.add_separator()
            dpg.add_text(" ")

            dpg.add_button(
                label="Create New Profile",
                tag="create_profile_btn",
                callback=self.show_create_modal,
            )
            dpg.add_button(
                label="Import Profile",
                tag="import_profile_btn",
                callback=self.show_import_modal,
            )
            dpg.add_button(
                label="Refresh",
                tag="refresh_profiles_btn",
                callback=self.refresh,
            )

            dpg.add_text(" ")

            with dpg.child_window(tag="profiles_list", height=-60):
                dpg.add_text(
                    "No profiles yet. Create your first profile to get started.",
                    tag="no_profiles_text",
                    color=COLORS["text_muted"],
                )
                with dpg.table(
                    tag="profiles_table",
                    header_row=True,
                    resizable=True,
                    show=False,
                ):
                    dpg.add_table_column(label="ID")
                    dpg.add_table_column(label="Name")
                    dpg.add_table_column(label="Browser")
                    dpg.add_table_column(label="Resolution")
                    dpg.add_table_column(label="Proxy")
                    dpg.add_table_column(label="Actions")

    def show_create_modal(self):
        with dpg.modal(tag="create_profile_modal", label="Create New Profile"):
            dpg.add_input_text(
                label="Profile Name",
                tag="new_profile_name",
                width=300,
            )
            dpg.add_combo(
                label="Browser Engine",
                tag="new_profile_browser",
                items=["chromium", "firefox", "webkit"],
                default_value="chromium",
                width=300,
            )
            dpg.add_input_text(
                label="User Agent (optional)",
                tag="new_profile_ua",
                width=300,
            )
            dpg.add_input_text(
                label="Proxy (optional)",
                tag="new_profile_proxy",
                width=300,
                hint="http://proxy:port",
            )
            dpg.add_combo(
                label="Resolution",
                tag="new_profile_resolution",
                items=["1920x1080", "1366x768", "1280x720", "2560x1440"],
                default_value="1920x1080",
                width=300,
            )
            dpg.add_input_text(
                label="Timezone (optional)",
                tag="new_profile_timezone",
                width=300,
                hint="America/New_York",
            )
            dpg.add_input_text(
                label="Language (optional)",
                tag="new_profile_language",
                width=300,
                hint="en-US",
            )
            dpg.add_checkbox(
                label="Headless Mode",
                tag="new_profile_headless",
                default_value=True,
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Create",
                    callback=self.create_profile,
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("create_profile_modal"),
                )

    def create_profile(self):
        name = dpg.get_value("new_profile_name")
        if not name:
            return

        profile_data = {
            "name": name,
            "browser_engine": dpg.get_value("new_profile_browser"),
            "user_agent": dpg.get_value("new_profile_ua") or None,
            "proxy": dpg.get_value("new_profile_proxy") or None,
            "resolution": dpg.get_value("new_profile_resolution"),
            "timezone": dpg.get_value("new_profile_timezone") or None,
            "language": dpg.get_value("new_profile_language") or None,
            "headless": dpg.get_value("new_profile_headless"),
        }

        try:
            self.app.api_client.create_profile(profile_data)
            dpg.close_modal("create_profile_modal")
            self.refresh()
        except Exception as e:
            print(f"Error creating profile: {e}")

    def navigate(self, page: str):
        self.app.show_page(page)
        if page in self.app.pages:
            self.app.pages[page].refresh()

    def logout(self):
        self.app.logout()

    def refresh(self):
        try:
            profiles = self.app.api_client.get_profiles()
            self.update_profiles_table(profiles)
        except Exception as e:
            print(f"Error refreshing profiles: {e}")

    def update_profiles_table(self, profiles):
        table = "profiles_table"
        no_profiles = "no_profiles_text"

        if not profiles:
            dpg.hide_item(table)
            dpg.show_item(no_profiles)
            return

        dpg.show_item(table)
        dpg.hide_item(no_profiles)

        for child in dpg.get_item_children(table)[1]:
            dpg.delete_item(child)

        for profile in profiles:
            with dpg.table_row(parent=table):
                dpg.add_text(str(profile.get("id", "")))
                dpg.add_text(profile.get("name", ""))
                dpg.add_text(profile.get("browser_engine", "chromium"))
                dpg.add_text(profile.get("resolution", "1920x1080"))
                dpg.add_text(profile.get("proxy", "-")[:30] if profile.get("proxy") else "-")
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Open",
                        tag=f"open_profile_{profile.get('id')}",
                        small=True,
                        callback=lambda: self.start_session(profile.get("id")),
                    )
                    dpg.add_button(
                        label="Clone",
                        tag=f"clone_profile_{profile.get('id')}",
                        small=True,
                        callback=lambda: self.show_clone_modal(profile),
                    )
                    dpg.add_button(
                        label="Export",
                        tag=f"export_profile_{profile.get('id')}",
                        small=True,
                        callback=lambda: self.export_profile(profile.get("id")),
                    )
                    dpg.add_button(
                        label="Edit",
                        tag=f"edit_profile_{profile.get('id')}",
                        small=True,
                        callback=lambda: self.show_edit_modal(profile),
                    )
                    dpg.add_button(
                        label="Delete",
                        tag=f"delete_profile_{profile.get('id')}",
                        small=True,
                        callback=lambda: self.delete_profile(profile.get("id")),
                    )

    def start_session(self, profile_id: int):
        try:
            self.app.api_client.create_session(profile_id)
            self.app.show_page("sessions")
            self.app.pages["sessions"].refresh()
        except Exception as e:
            print(f"Error starting session: {e}")

    def show_edit_modal(self, profile):
        with dpg.modal(tag="edit_profile_modal", label="Edit Profile"):
            dpg.add_input_text(
                label="Profile Name",
                tag="edit_profile_name",
                width=300,
                default_value=profile.get("name", ""),
            )
            dpg.add_combo(
                label="Browser Engine",
                tag="edit_profile_browser",
                items=["chromium", "firefox", "webkit"],
                default_value=profile.get("browser_engine", "chromium"),
                width=300,
            )
            dpg.add_input_text(
                label="User Agent (optional)",
                tag="edit_profile_ua",
                width=300,
                default_value=profile.get("user_agent", ""),
            )
            dpg.add_input_text(
                label="Proxy (optional)",
                tag="edit_profile_proxy",
                width=300,
                default_value=profile.get("proxy", ""),
            )
            dpg.add_combo(
                label="Resolution",
                tag="edit_profile_resolution",
                items=["1920x1080", "1366x768", "1280x720", "2560x1440"],
                default_value=profile.get("resolution", "1920x1080"),
                width=300,
            )
            dpg.add_input_text(
                label="Timezone (optional)",
                tag="edit_profile_timezone",
                width=300,
                default_value=profile.get("timezone", ""),
            )
            dpg.add_input_text(
                label="Language (optional)",
                tag="edit_profile_language",
                width=300,
                default_value=profile.get("language", ""),
            )
            dpg.add_checkbox(
                label="Headless Mode",
                tag="edit_profile_headless",
                default_value=profile.get("headless", True),
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save Changes",
                    callback=lambda: self.update_profile(profile.get("id")),
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("edit_profile_modal"),
                )

    def update_profile(self, profile_id: int):
        profile_data = {
            "name": dpg.get_value("edit_profile_name"),
            "browser_engine": dpg.get_value("edit_profile_browser"),
            "user_agent": dpg.get_value("edit_profile_ua") or None,
            "proxy": dpg.get_value("edit_profile_proxy") or None,
            "resolution": dpg.get_value("edit_profile_resolution"),
            "timezone": dpg.get_value("edit_profile_timezone") or None,
            "language": dpg.get_value("edit_profile_language") or None,
            "headless": dpg.get_value("edit_profile_headless"),
        }

        try:
            self.app.api_client.update_profile(profile_id, profile_data)
            dpg.close_modal("edit_profile_modal")
            self.refresh()
        except Exception as e:
            print(f"Error updating profile: {e}")

    def delete_profile(self, profile_id: int):
        try:
            self.app.api_client.delete_profile(profile_id)
            self.refresh()
        except Exception as e:
            print(f"Error deleting profile: {e}")

    def show_import_modal(self):
        with dpg.modal(tag="import_profile_modal", label="Import Profile"):
            dpg.add_input_text(
                label="Profile JSON",
                tag="import_profile_json",
                width=400,
                height=200,
            )
            dpg.add_text(" ")
            dpg.add_text("Paste profile JSON data above", color=COLORS["text_muted"])
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Import",
                    callback=self.import_profile,
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("import_profile_modal"),
                )

    def import_profile(self):
        import json
        json_str = dpg.get_value("import_profile_json")
        if not json_str:
            return
        
        try:
            profile_data = json.loads(json_str)
            self.app.api_client.import_profile(profile_data)
            dpg.close_modal("import_profile_modal")
            self.refresh()
            print("Profile imported successfully!")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
        except Exception as e:
            print(f"Error importing profile: {e}")

    def export_profile(self, profile_id: int):
        try:
            result = self.app.api_client.export_profile(profile_id)
            if result:
                import json
                import datetime
                filename = f"profile_{profile_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Profile exported to: {filename}")
        except Exception as e:
            print(f"Error exporting profile: {e}")

    def show_clone_modal(self, profile):
        with dpg.modal(tag="clone_profile_modal", label="Clone Profile"):
            dpg.add_input_text(
                label="New Profile Name",
                tag="clone_profile_name",
                width=300,
                default_value=f"{profile.get('name', 'profile')}_clone",
            )
            dpg.add_text(" ")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Clone",
                    callback=lambda: self.clone_profile(profile.get("id")),
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.close_modal("clone_profile_modal"),
                )

    def clone_profile(self, profile_id: int):
        new_name = dpg.get_value("clone_profile_name")
        if not new_name:
            return
        
        try:
            self.app.api_client.clone_profile(profile_id, new_name)
            dpg.close_modal("clone_profile_modal")
            self.refresh()
            print(f"Profile cloned as: {new_name}")
        except Exception as e:
            print(f"Error cloning profile: {e}")

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)
            self.refresh()

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
