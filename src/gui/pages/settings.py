"""
Settings Page for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS
import json
from pathlib import Path


class SettingsPage:
    def __init__(self, app):
        self.app = app
        self.window_id = None
        self.config_file = Path.home() / ".bower" / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                pass
        return self._default_config()

    def _default_config(self) -> dict:
        return {
            "api_url": "http://localhost:8000",
            "default_browser": "chromium",
            "default_resolution": "1920x1080",
            "default_headless": True,
            "auto_refresh_interval": 30,
            "theme": "dark",
        }

    def _save_config(self, config: dict):
        self.config_file.write_text(json.dumps(config, indent=2))

    def create(self):
        with dpg.window(
            tag="settings_window",
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
        ):
            self.window_id = "settings_window"

            with dpg.group(horizontal=True):
                self.create_sidebar()
                self.create_main_content()

    def create_sidebar(self):
        with dpg.child_window(
            tag="settings_sidebar",
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
            tag="settings_content",
            width=-1,
            height=-1,
            border=False,
        ):
            dpg.add_text("Settings", font=28)
            dpg.add_text(
                "Configure application settings",
                color=COLORS["text_secondary"],
            )
            dpg.add_separator()
            dpg.add_text("", height=15)

            with dpg.collapsing_header(label="API Configuration", default_open=True):
                dpg.add_text("API Server URL", color=COLORS["text_secondary"], font=12)
                dpg.add_input_text(
                    tag="api_url",
                    default_value="http://localhost:8000",
                    width=300,
                )
                dpg.add_text("", height=10)
                dpg.add_button(
                    label="Test Connection",
                    tag="test_connection_btn",
                    callback=self.test_connection,
                )

            dpg.add_text("", height=15)

            with dpg.collapsing_header(label="Browser Settings", default_open=True):
                dpg.add_text("Default Browser Engine", color=COLORS["text_secondary"], font=12)
                dpg.add_combo(
                    tag="default_browser",
                    items=["chromium", "firefox", "webkit"],
                    default_value="chromium",
                    width=200,
                )
                dpg.add_text("", height=10)
                dpg.add_text("Default Resolution", color=COLORS["text_secondary"], font=12)
                dpg.add_combo(
                    tag="default_resolution",
                    items=["1920x1080", "1366x768", "1280x720", "2560x1440"],
                    default_value="1920x1080",
                    width=200,
                )
                dpg.add_text("", height=10)
                dpg.add_checkbox(
                    tag="default_headless",
                    label="Default Headless Mode",
                    default_value=True,
                )

            dpg.add_text("", height=15)

            with dpg.collapsing_header(label="Auto Refresh", default_open=True):
                dpg.add_text("Auto Refresh Interval (seconds)", color=COLORS["text_secondary"], font=12)
                dpg.add_input_int(
                    tag="auto_refresh_interval",
                    default_value=30,
                    width=100,
                    min_value=5,
                    max_value=300,
                )
                dpg.add_text("", height=5)
                dpg.add_checkbox(
                    tag="enable_auto_refresh",
                    label="Enable Auto Refresh",
                    default_value=True,
                )

            dpg.add_text("", height=15)

            with dpg.collapsing_header(label="Save Settings", default_open=True):
                dpg.add_button(
                    label="Save Settings",
                    tag="save_settings_btn",
                    callback=self.save_settings,
                    width=150,
                )
                dpg.add_button(
                    label="Reset to Defaults",
                    tag="reset_settings_btn",
                    callback=self.reset_settings,
                    width=150,
                )

            dpg.add_text("", height=15)

            with dpg.collapsing_header(label="About", default_open=True):
                dpg.add_text("Bower Antidetect Browser", color=COLORS["primary"], font=16)
                dpg.add_text("Version 1.0.0", color=COLORS["text_secondary"])
                dpg.add_text("", height=5)
                dpg.add_text(
                    "A professional privacy browser with anti-detection capabilities.",
                    color=COLORS["text_secondary"],
                )

    def test_connection(self):
        api_url = dpg.get_value("api_url")
        old_base_url = self.app.api_client.base_url
        self.app.api_client.base_url = api_url

        try:
            health = self.app.api_client.get_health()
            if health.get("status") == "healthy":
                dpg.set_value("api_status", "Connected")
        except Exception as e:
            dpg.set_value("api_status", "Disconnected")
        finally:
            self.app.api_client.base_url = old_base_url

    def save_settings(self):
        config = {
            "api_url": dpg.get_value("api_url"),
            "default_browser": dpg.get_value("default_browser"),
            "default_resolution": dpg.get_value("default_resolution"),
            "default_headless": dpg.get_value("default_headless"),
            "auto_refresh_interval": dpg.get_value("auto_refresh_interval"),
            "enable_auto_refresh": dpg.get_value("enable_auto_refresh"),
            "theme": "dark",
        }
        self._save_config(config)
        self.app.api_client.base_url = config["api_url"]
        print("Settings saved successfully!")

    def reset_settings(self):
        config = self._default_config()
        dpg.set_value("api_url", config["api_url"])
        dpg.set_value("default_browser", config["default_browser"])
        dpg.set_value("default_resolution", config["default_resolution"])
        dpg.set_value("default_headless", config["default_headless"])
        dpg.set_value("auto_refresh_interval", config["auto_refresh_interval"])
        dpg.set_value("enable_auto_refresh", True)
        print("Settings reset to defaults!")

    def load_settings(self):
        config = self._load_config()
        dpg.set_value("api_url", config.get("api_url", "http://localhost:8000"))
        dpg.set_value("default_browser", config.get("default_browser", "chromium"))
        dpg.set_value("default_resolution", config.get("default_resolution", "1920x1080"))
        dpg.set_value("default_headless", config.get("default_headless", True))
        dpg.set_value("auto_refresh_interval", config.get("auto_refresh_interval", 30))
        dpg.set_value("enable_auto_refresh", config.get("enable_auto_refresh", True))

    def navigate(self, page: str):
        self.app.show_page(page)
        if page in self.app.pages:
            self.app.pages[page].refresh()

    def logout(self):
        self.app.logout()

    def show(self):
        if self.window_id:
            dpg.show_item(self.window_id)

    def hide(self):
        if self.window_id:
            dpg.hide_item(self.window_id)
