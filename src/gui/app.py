"""
Bower GUI Application - Main Application Class
"""

import dearpygui.dearpygui as dpg

from src.gui.pages.login import LoginPage
from src.gui.pages.dashboard import DashboardPage
from src.gui.pages.profiles import ProfilesPage
from src.gui.pages.sessions import SessionsPage
from src.gui.pages.proxies import ProxiesPage
from src.gui.pages.settings import SettingsPage
from src.gui.utils.api_client import GUIClient
from src.gui.utils.websocket_client import RealTimeManager, rt_manager
from src.gui.utils.notifications import NotificationManager, notification_manager


class BowerApp:
    def __init__(self):
        self.api_client = GUIClient()
        self.current_page = "login"
        self.is_authenticated = False
        self.auth_token = ""
        
        self.rt_manager = RealTimeManager()
        self.notification_manager = NotificationManager()
        
        self.auto_refresh_enabled = True
        self.auto_refresh_interval = 30
        self._last_refresh = 0
        
        self.sidebar_collapsed = False
        self.sidebar_width = 220
        self.sidebar_collapsed_width = 64
        
        self.pages = {}
        self.sidebar_id = None

    def setup(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 41, 59))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (30, 41, 59))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 41, 59))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (51, 65, 85))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (59, 130, 246))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHover, (37, 99, 235))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (226, 232, 240))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (51, 65, 85))
                dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (51, 65, 85))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (30, 41, 59))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (51, 65, 85))

        dpg.bind_theme(global_theme)

        self.pages["login"] = LoginPage(self)
        self.pages["dashboard"] = DashboardPage(self)
        self.pages["profiles"] = ProfilesPage(self)
        self.pages["sessions"] = SessionsPage(self)
        self.pages["proxies"] = ProxiesPage(self)
        self.pages["settings"] = SettingsPage(self)

        for page in self.pages.values():
            page.create()

    def show_page(self, page_name: str):
        for name, page in self.pages.items():
            if name == page_name:
                page.show()
            else:
                page.hide()

    def login(self, token: str):
        self.auth_token = token
        self.is_authenticated = True
        self.current_page = "dashboard"
        self.api_client.set_token(token)
        self.show_page("dashboard")
        self.pages["dashboard"].refresh()
        self.notification_manager.success("Logged in successfully!")

    def logout(self):
        self.rt_manager.disconnect_all()
        self.notification_manager.clear()
        self.auth_token = ""
        self.is_authenticated = False
        self.current_page = "login"
        self.api_client.clear_token()
        self.show_page("login")

    def run(self):
        self.show_page("login")
        while dpg.is_dearpygui_running():
            self.update()
            dpg.render_dearpygui_frame()
            import time
            time.sleep(0.016)

    def update(self):
        if self.current_page == "dashboard":
            self.pages["dashboard"].update()
        
        if self.auto_refresh_enabled:
            self._check_auto_refresh()

    def _check_auto_refresh(self):
        import time
        current_time = time.time()
        
        if current_time - self._last_refresh >= self.auto_refresh_interval:
            self._last_refresh = current_time
            
            if self.is_authenticated:
                try:
                    health = self.api_client.get_health()
                    
                    if self.current_page == "dashboard":
                        self.pages["dashboard"].refresh()
                    elif self.current_page == "sessions":
                        self.pages["sessions"].refresh()
                        
                except Exception as e:
                    pass

    def connect_session_realtime(self, session_id: str):
        """Connect to session for real-time updates."""
        return self.rt_manager.connect_session(session_id)

    def disconnect_session_realtime(self, session_id: str):
        """Disconnect from session real-time updates."""
        self.rt_manager.disconnect_session(session_id)

    def show_notification(self, message: str, type: str = "info"):
        """Show notification."""
        if type == "success":
            self.notification_manager.success(message)
        elif type == "error":
            self.notification_manager.error(message)
        elif type == "warning":
            self.notification_manager.warning(message)
        else:
            self.notification_manager.info(message)

    def set_auto_refresh(self, enabled: bool, interval: int = 30):
        """Set auto-refresh settings."""
        self.auto_refresh_enabled = enabled
        self.auto_refresh_interval = interval
    
    def toggle_sidebar(self):
        """Toggle sidebar collapsed state."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        
        for page in self.pages.values():
            if hasattr(page, 'toggle_sidebar'):
                page.toggle_sidebar()
    
    def get_sidebar_width(self) -> int:
        """Get current sidebar width."""
        return self.sidebar_collapsed_width if self.sidebar_collapsed else self.sidebar_width

    def cleanup(self):
        self.rt_manager.disconnect_all()
        self.notification_manager.clear()
        self.api_client.close()
