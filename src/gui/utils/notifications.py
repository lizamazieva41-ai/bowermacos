"""
Notification System for GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional
from enum import Enum
from datetime import datetime
from src.gui.styles.theme import COLORS


class NotificationType(Enum):
    """Notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationManager:
    """Manager for GUI notifications/toasts."""
    
    def __init__(self):
        self.notifications = []
        self._notification_window = None
        self._max_notifications = 5
    
    def show(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        duration: int = 3000,
        callback: Optional[Callable] = None,
    ):
        """Show a notification."""
        notification = {
            "id": f"notif_{len(self.notifications)}_{datetime.now().timestamp()}",
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now(),
            "callback": callback,
            "duration": duration,
        }
        
        self.notifications.append(notification)
        
        if len(self.notifications) > self._max_notifications:
            self.notifications.pop(0)
        
        self._render_notification(notification)
    
    def _render_notification(self, notification: dict):
        """Render a single notification."""
        color = self._get_color(notification["type"])
        
        if dpg.does_item_exist("notification_container"):
            pass
        else:
            with dpg.window(
                tag="notification_container",
                width=350,
                height=0,
                no_title_bar=True,
                no_resize=True,
                no_move=True,
                always_on_top=True,
                pos=[dpg.get_viewport_width() - 370, 10],
            ):
                dpg.add_text("")
        
        y_offset = len(self.notifications) * 60
        
        with dpg.window(
            tag=notification["id"],
            width=340,
            height=50,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            pos=[dpg.get_viewport_width() - 350, 10 + (len(self.notifications) - 1) * 55],
        ):
            dpg.add_text(
                f"[{notification['type'].value.upper()}] {notification['message']}",
                color=color,
            )
        
        if notification["callback"]:
            notification["callback"]()
    
    def _get_color(self, notification_type: NotificationType) -> tuple:
        """Get color for notification type."""
        colors = {
            NotificationType.INFO: COLORS["primary"],
            NotificationType.SUCCESS: COLORS["success"],
            NotificationType.WARNING: COLORS["warning"],
            NotificationType.ERROR: COLORS["danger"],
        }
        return colors.get(notification_type, COLORS["text_primary"])
    
    def clear(self):
        """Clear all notifications."""
        for notif in self.notifications:
            if dpg.does_item_exist(notif["id"]):
                dpg.delete_item(notif["id"])
        self.notifications.clear()
        
        if dpg.does_item_exist("notification_container"):
            dpg.delete_item("notification_container")
    
    def info(self, message: str, callback: Optional[Callable] = None):
        """Show info notification."""
        self.show(message, NotificationType.INFO, callback=callback)
    
    def success(self, message: str, callback: Optional[Callable] = None):
        """Show success notification."""
        self.show(message, NotificationType.SUCCESS, callback=callback)
    
    def warning(self, message: str, callback: Optional[Callable] = None):
        """Show warning notification."""
        self.show(message, NotificationType.WARNING, callback=callback)
    
    def error(self, message: str, callback: Optional[Callable] = None):
        """Show error notification."""
        self.show(message, NotificationType.ERROR, callback=callback)


notification_manager = NotificationManager()


def show_info(message: str):
    """Show info message."""
    notification_manager.info(message)


def show_success(message: str):
    """Show success message."""
    notification_manager.success(message)


def show_warning(message: str):
    """Show warning message."""
    notification_manager.warning(message)


def show_error(message: str):
    """Show error message."""
    notification_manager.error(message)
