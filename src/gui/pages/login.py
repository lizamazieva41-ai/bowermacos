"""
Login Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class LoginPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None
        self.username_input = None
        self.password_input = None
        self.api_key_input = None
        self.error_text = None
        self.login_mode = "credentials"

    def create(self):
        with dpg.window(
            label="Login",
            tag="login_window",
            width=450,
            height=400,
            no_resize=True,
            no_move=True,
            no_title_bar=True,
            center=True,
        ):
            self.window_id = "login_window"

            dpg.add_text(
                "Bower Antidetect Browser",
                color=COLORS["primary"],
                font=24,
            )
            dpg.add_text("", height=20)

            dpg.add_text("Login to your account", color=COLORS["text_secondary"])

            with dpg.group(tag="credentials_form"):
                dpg.add_text("", height=10)
                dpg.add_input_text(
                    label="Username",
                    tag="login_username",
                    width=300,
                    hint="Enter username",
                )
                dpg.add_input_text(
                    label="Password",
                    tag="login_password",
                    width=300,
                    password=True,
                    hint="Enter password",
                )
                dpg.add_text("", height=5)
                dpg.add_button(
                    label="Login",
                    tag="login_btn",
                    width=300,
                    callback=self.login,
                )

            with dpg.group(tag="api_key_form", show=False):
                dpg.add_text("", height=10)
                dpg.add_input_text(
                    label="API Key",
                    tag="login_api_key",
                    width=300,
                    hint="Enter API key",
                )
                dpg.add_text("", height=5)
                dpg.add_button(
                    label="Login with API Key",
                    tag="login_api_btn",
                    width=300,
                    callback=self.login_with_api_key,
                )

            dpg.add_text("", height=10)
            dpg.add_button(
                label="Use API Key instead",
                tag="switch_login_mode",
                callback=self.toggle_login_mode,
            )

            dpg.add_text(
                "",
                tag="login_error",
                color=COLORS["danger"],
            )

    def toggle_login_mode(self):
        if self.login_mode == "credentials":
            self.login_mode = "api_key"
            dpg.hide_item("credentials_form")
            dpg.show_item("api_key_form")
        else:
            self.login_mode = "credentials"
            dpg.hide_item("api_key_form")
            dpg.show_item("credentials_form")

    def login(self):
        username = dpg.get_value("login_username")
        password = dpg.get_value("login_password")

        if not username or not password:
            dpg.set_value("login_error", "Please enter username and password")
            return

        try:
            result = self.app.api_client.login(username, password)
            if result.get("success"):
                token = result.get("data", {}).get("access_token")
                if token:
                    self.app.login(token)
            else:
                dpg.set_value("login_error", result.get("message", "Login failed"))
        except Exception as e:
            dpg.set_value("login_error", str(e))

    def login_with_api_key(self):
        api_key = dpg.get_value("login_api_key")

        if not api_key:
            dpg.set_value("login_error", "Please enter API key")
            return

        try:
            if self.app.api_client.login_with_api_key(api_key):
                self.app.login(api_key)
            else:
                dpg.set_value("login_error", "Invalid API key")
        except Exception as e:
            dpg.set_value("login_error", str(e))

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
