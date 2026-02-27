"""
Error Dialogs Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS
from typing import Callable, Optional, List


class ErrorType:
    """Error types."""
    CONNECTION = "connection"
    SESSION_CRASH = "session_crash"
    AUTH = "auth"
    PROXY = "proxy"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorDialog:
    """Error dialog component."""
    
    @staticmethod
    def show(
        title: str,
        message: str,
        error_type: str = ErrorType.UNKNOWN,
        details: str = "",
        actions: List[dict] = None,
    ):
        """Show an error dialog."""
        tag = f"error_dialog_{error_type}"
        
        width = 500
        height = 300 + (50 if details else 0)
        
        with dpg.window(
            tag=tag,
            label=title,
            width=width,
            height=height,
            modal=True,
            pos=[150, 100],
        ):
            icon = ErrorDialog._get_icon(error_type)
            color = ErrorDialog._get_color(error_type)
            
            dpg.add_text(f"{icon} {title}", color=color)
            dpg.add_text(" ")
            
            dpg.add_text(message, wrap=450, color=COLORS["text_secondary"])
            
            if details:
                dpg.add_text(" ")
                dpg.add_text("Details:", color=COLORS["text_muted"])
                dpg.add_text(details, wrap=450, color=COLORS["text_muted"])
            
            dpg.add_text(" ")
            dpg.add_separator()
            dpg.add_text(" ")
            
            if actions:
                with dpg.group(horizontal=True):
                    for action in actions:
                        dpg.add_button(
                            label=action.get("label", "OK"),
                            callback=action.get("callback"),
                            width=action.get("width", 120),
                        )
            else:
                dpg.add_button(
                    label="OK",
                    callback=lambda: dpg.close_modal(tag),
                    width=100,
                )
    
    @staticmethod
    def _get_icon(error_type: str) -> str:
        icons = {
            ErrorType.CONNECTION: "🔌",
            ErrorType.SESSION_CRASH: "💥",
            ErrorType.AUTH: "🔐",
            ErrorType.PROXY: "🔗",
            ErrorType.VALIDATION: "⚠️",
            ErrorType.UNKNOWN: "❌",
        }
        return icons.get(error_type, "❌")
    
    @staticmethod
    def _get_color(error_type: str) -> tuple:
        colors = {
            ErrorType.CONNECTION: COLORS.get("warning"),
            ErrorType.SESSION_CRASH: COLORS.get("danger"),
            ErrorType.AUTH: COLORS.get("warning"),
            ErrorType.PROXY: COLORS.get("warning"),
            ErrorType.VALIDATION: COLORS.get("warning"),
            ErrorType.UNKNOWN: COLORS.get("danger"),
        }
        return colors.get(error_type, COLORS.get("danger"))


class ConnectionErrorDialog:
    """Connection error dialog with retry options."""
    
    @staticmethod
    def show(
        on_retry: Callable = None,
        on_use_proxy: Callable = None,
        on_continue_without_proxy: Callable = None,
    ):
        """Show connection error dialog."""
        tag = "connection_error_dialog"
        
        with dpg.window(
            tag=tag,
            label="Connection Error",
            width=500,
            height=350,
            modal=True,
            pos=[150, 100],
        ):
            dpg.add_text("🔌 Connection Failed", color=COLORS.get("warning"))
            dpg.add_text(" ")
            
            dpg.add_text(
                "Unable to connect to the API server. Please check your connection and try again.",
                wrap=450,
                color=COLORS["text_secondary"],
            )
            
            dpg.add_text(" ")
            dpg.add_text("Options:")
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="🔄 Retry",
                    callback=on_retry if on_retry else lambda: dpg.close_modal(tag),
                    width=120,
                )
                dpg.add_button(
                    label="🔗 Use Different Proxy",
                    callback=on_use_proxy if on_use_proxy else lambda: dpg.close_modal(tag),
                    width=180,
                )
                dpg.add_button(
                    label="Continue Without Proxy",
                    callback=on_continue_without_proxy if on_continue_without_proxy else lambda: dpg.close_modal(tag),
                    width=180,
                )
            
            dpg.add_text(" ")
            dpg.add_text(
                "Tip: Check if the API server is running at the configured URL.",
                color=COLORS["text_muted"],
            )


class SessionCrashDialog:
    """Session crash dialog with options."""
    
    @staticmethod
    def show(
        crash_details: str = "",
        on_view_log: Callable = None,
        on_return_dashboard: Callable = None,
        on_restart_session: Callable = None,
    ):
        """Show session crash dialog."""
        tag = "session_crash_dialog"
        
        with dpg.window(
            tag=tag,
            label="Session Crashed",
            width=550,
            height=400,
            modal=True,
            pos=[150, 100],
        ):
            dpg.add_text("💥 Session Crashed", color=COLORS.get("danger"))
            dpg.add_text(" ")
            
            dpg.add_text(
                "The browser session has crashed unexpectedly.",
                color=COLORS["text_secondary"],
            )
            
            if crash_details:
                dpg.add_text(" ")
                dpg.add_text("Crash Details:", color=COLORS["text_muted"])
                with dpg.child_window(height=100):
                    dpg.add_text(crash_details, color=COLORS["text_muted"])
            
            dpg.add_text(" ")
            dpg.add_separator()
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                if on_view_log:
                    dpg.add_button(
                        label="📋 View Logs",
                        callback=on_view_log,
                        width=120,
                    )
                
                dpg.add_button(
                    label="🏠 Return to Dashboard",
                    callback=on_return_dashboard if on_return_dashboard else lambda: dpg.close_modal(tag),
                    width=180,
                )
                
                dpg.add_button(
                    label="🔄 Restart Session",
                    callback=on_restart_session if on_restart_session else lambda: dpg.close_modal(tag),
                    width=150,
                )


class AuthErrorDialog:
    """Authentication error dialog."""
    
    @staticmethod
    def show(
        message: str = "Authentication failed",
        on_retry: Callable = None,
        on_logout: Callable = None,
    ):
        """Show authentication error dialog."""
        tag = "auth_error_dialog"
        
        with dpg.window(
            tag=tag,
            label="Authentication Error",
            width=450,
            height=280,
            modal=True,
            pos=[200, 150],
        ):
            dpg.add_text("🔐 Auth Error", color=COLORS.get("warning"))
            dpg.add_text(" ")
            
            dpg.add_text(message, wrap=400, color=COLORS["text_secondary"])
            
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Try Again",
                    callback=on_retry if on_retry else lambda: dpg.close_modal(tag),
                    width=120,
                )
                dpg.add_button(
                    label="Logout",
                    callback=on_logout if on_logout else lambda: dpg.close_modal(tag),
                    width=100,
                )


class ProxyErrorDialog:
    """Proxy error dialog."""
    
    @staticmethod
    def show(
        proxy_url: str = "",
        on_test: Callable = None,
        on_change_proxy: Callable = None,
        on_continue_without: Callable = None,
    ):
        """Show proxy error dialog."""
        tag = "proxy_error_dialog"
        
        with dpg.window(
            tag=tag,
            label="Proxy Error",
            width=500,
            height=320,
            modal=True,
            pos=[150, 100],
        ):
            dpg.add_text("🔗 Proxy Error", color=COLORS.get("warning"))
            dpg.add_text(" ")
            
            dpg.add_text(
                f"The proxy '{proxy_url}' is not responding or invalid.",
                wrap=450,
                color=COLORS["text_secondary"],
            )
            
            dpg.add_text(" ")
            dpg.add_text("Would you like to:")
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="🧪 Test Again",
                    callback=on_test if on_test else lambda: dpg.close_modal(tag),
                    width=120,
                )
                dpg.add_button(
                    label="📝 Change Proxy",
                    callback=on_change_proxy if on_change_proxy else lambda: dpg.close_modal(tag),
                    width=140,
                )
                dpg.add_button(
                    label="Continue Without",
                    callback=on_continue_without if on_continue_without else lambda: dpg.close_modal(tag),
                    width=150,
                )


class ConfirmDialog:
    """Confirmation dialog."""
    
    @staticmethod
    def show(
        title: str,
        message: str,
        on_confirm: Callable,
        on_cancel: Callable = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        danger: bool = False,
    ):
        """Show confirmation dialog."""
        tag = f"confirm_dialog_{title.lower().replace(' ', '_')}"
        
        with dpg.window(
            tag=tag,
            label=title,
            width=450,
            height=200,
            modal=True,
            pos=[200, 150],
        ):
            dpg.add_text(message, wrap=400, color=COLORS["text_secondary"])
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                btn_color = COLORS.get("danger") if danger else COLORS.get("primary")
                
                with dpg.theme() as theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, btn_color)
                
                dpg.add_button(
                    label=confirm_label,
                    callback=lambda: [on_confirm(), dpg.close_modal(tag)],
                    width=120,
                )
                dpg.add_button(
                    label=cancel_label,
                    callback=lambda: [on_cancel() if on_cancel else None, dpg.close_modal(tag)],
                    width=100,
                )


class LoadingDialog:
    """Loading dialog component."""
    
    @staticmethod
    def show(message: str = "Loading..."):
        """Show loading dialog."""
        tag = "loading_dialog"
        
        with dpg.window(
            tag=tag,
            width=300,
            height=100,
            modal=True,
            no_title_bar=True,
            pos=[300, 200],
        ):
            with dpg.group():
                dpg.add_text("⏳")
                dpg.add_text(message)
    
    @staticmethod
    def hide():
        """Hide loading dialog."""
        if dpg.does_item_exist("loading_dialog"):
            dpg.close_window("loading_dialog")


class ToastManager:
    """Toast notification manager."""
    
    def __init__(self):
        self.toasts = []
        self.max_toasts = 5
    
    def show(self, message: str, toast_type: str = "info", duration: int = 3000):
        """Show a toast notification."""
        if len(self.toasts) >= self.max_toasts:
            oldest = self.toasts.pop(0)
            if dpg.does_item_exist(oldest):
                dpg.delete_item(oldest)
        
        colors = {
            "info": COLORS.get("primary"),
            "success": COLORS.get("success"),
            "warning": COLORS.get("warning"),
            "error": COLORS.get("danger"),
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
        }
        
        color = colors.get(toast_type, COLORS.get("primary"))
        icon = icons.get(toast_type, "ℹ️")
        
        toast_id = f"toast_{len(self.toasts)}"
        
        with dpg.window(
            tag=toast_id,
            width=350,
            height=50,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            pos=[dpg.get_viewport_width() - 370, 10 + len(self.toasts) * 55],
        ):
            dpg.add_text(f"{icon} {message}", color=color)
        
        self.toasts.append(toast_id)
        
        import threading
        timer = threading.Timer(duration / 1000, lambda: self._remove_toast(toast_id))
        timer.start()
    
    def _remove_toast(self, toast_id: str):
        """Remove a toast."""
        if dpg.does_item_exist(toast_id):
            dpg.delete_item(toast_id)
        if toast_id in self.toasts:
            self.toasts.remove(toast_id)


toast_manager = ToastManager()
