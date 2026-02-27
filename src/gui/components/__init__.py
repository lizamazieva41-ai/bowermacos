"""
Reusable GUI Components for Bower Application
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Dict, Any
from src.gui.styles.theme import COLORS


class Button:
    """Reusable button component."""
    
    @staticmethod
    def create(
        label: str,
        callback: Callable,
        width: int = 150,
        height: int = 30,
        tag: Optional[str] = None,
        enabled: bool = True,
        small: bool = False
    ):
        """Create a button."""
        if small:
            width = 60
            height = 20
        
        dpg.add_button(
            label=label,
            callback=callback,
            width=width,
            height=height,
            tag=tag,
            enabled=enabled,
        )


class InputField:
    """Reusable input field component."""
    
    @staticmethod
    def create_text(
        label: str,
        tag: str,
        default_value: str = "",
        width: int = 300,
        hint: str = "",
        password: bool = False,
        readonly: bool = False
    ):
        """Create a text input field."""
        dpg.add_input_text(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            hint=hint,
            password=password,
            readonly=readonly,
        )
    
    @staticmethod
    def create_int(
        label: str,
        tag: str,
        default_value: int = 0,
        width: int = 150,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ):
        """Create an integer input field."""
        dpg.add_input_int(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            min_value=min_value,
            max_value=max_value,
        )
    
    @staticmethod
    def create_float(
        label: str,
        tag: str,
        default_value: float = 0.0,
        width: int = 150,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ):
        """Create a float input field."""
        dpg.add_input_float(
            label=label,
            tag=tag,
            default_value=default_value,
            width=width,
            min_value=min_value,
            max_value=max_value,
        )


class SelectField:
    """Reusable select/combo component."""
    
    @staticmethod
    def create(
        label: str,
        tag: str,
        items: List[str],
        default_value: str = "",
        width: int = 200,
    ):
        """Create a combo/select field."""
        dpg.add_combo(
            label=label,
            tag=tag,
            items=items,
            default_value=default_value,
            width=width,
        )


class Checkbox:
    """Reusable checkbox component."""
    
    @staticmethod
    def create(
        label: str,
        tag: str,
        default_value: bool = False,
    ):
        """Create a checkbox."""
        dpg.add_checkbox(
            label=label,
            tag=tag,
            default_value=default_value,
        )


class Table:
    """Reusable table component."""
    
    @staticmethod
    def create(
        tag: str,
        columns: List[str],
        height: int = 300,
        resizable: bool = True,
    ):
        """Create a table."""
        with dpg.table(
            tag=tag,
            header_row=True,
            resizable=resizable,
            height=height,
        ):
            for col in columns:
                dpg.add_table_column(label=col)
    
    @staticmethod
    def add_row(tag: str, data: List[str], colors: Optional[List[tuple]] = None):
        """Add a row to the table."""
        with dpg.table_row(parent=tag):
            for i, item in enumerate(data):
                color = colors[i] if colors and i < len(colors) else None
                if color:
                    dpg.add_text(item, color=color)
                else:
                    dpg.add_text(item)
    
    @staticmethod
    def clear(tag: str):
        """Clear all rows from the table."""
        for child in dpg.get_item_children(tag)[1]:
            dpg.delete_item(child)


class Card:
    """Reusable card/container component."""
    
    @staticmethod
    def create(
        tag: str,
        width: int = 200,
        height: int = 100,
    ):
        """Create a card container."""
        return dpg.add_child_window(
            tag=tag,
            width=width,
            height=height,
            border=True,
        )


class Modal:
    """Reusable modal dialog component."""
    
    @staticmethod
    def create(
        tag: str,
        label: str,
        width: int = 400,
        height: int = 300,
    ):
        """Create a modal."""
        return dpg.modal(
            tag=tag,
            label=label,
            width=width,
            height=height,
        )
    
    @staticmethod
    def close(tag: str):
        """Close a modal."""
        dpg.close_modal(tag)


class StatCard:
    """Reusable statistic card component."""
    
    @staticmethod
    def create(
        title: str,
        value: str,
        tag: str,
        color: tuple = COLORS["primary"],
        width: int = 200,
        height: int = 100,
    ):
        """Create a stat card."""
        with dpg.child_window(
            tag=f"stat_{tag}",
            width=width,
            height=height,
        ):
            dpg.add_text(title, color=COLORS["text_secondary"], font=12)
            dpg.add_text(value, tag=tag, color=color, font=32)


class StatusIndicator:
    """Reusable status indicator component."""
    
    @staticmethod
    def create(
        tag: str,
        status: str,
    ):
        """Create a status indicator."""
        color = COLORS["success"] if status == "active" else COLORS["danger"]
        dpg.add_text(status, tag=tag, color=color)


class ConfirmDialog:
    """Confirmation dialog component."""
    
    @staticmethod
    def show(
        title: str,
        message: str,
        confirm_callback: Callable,
        cancel_callback: Optional[Callable] = None,
    ):
        """Show a confirmation dialog."""
        tag = f"confirm_{id(message)}"
        
        with dpg.modal(tag=tag, label=title):
            dpg.add_text(message)
            dpg.add_text("", height=10)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Confirm",
                    callback=lambda: [confirm_callback(), dpg.close_modal(tag)],
                )
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: [cancel_callback() if cancel_callback else None, dpg.close_modal(tag)],
                )


class Notification:
    """Toast notification component."""
    
    @staticmethod
    def show(message: str, success: bool = True, duration: int = 3000):
        """Show a notification."""
        color = COLORS["success"] if success else COLORS["danger"]
        
        with dpg.window(
            tag="notification",
            width=300,
            height=50,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            pos=[dpg.get_viewport_width() - 320, 10],
        ):
            dpg.add_text(message, color=color)


class Sidebar:
    """Reusable sidebar navigation component."""
    
    @staticmethod
    def create(
        tag: str,
        width: int = 220,
        app=None,
    ):
        """Create a sidebar with navigation."""
        with dpg.child_window(
            tag=tag,
            width=width,
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
            
            return dpg.add_group()
    
    @staticmethod
    def add_nav_button(
        label: str,
        page: str,
        callback: Callable,
        width: int = 190,
    ):
        """Add a navigation button to sidebar."""
        dpg.add_button(
            label=label,
            width=width,
            callback=callback,
        )


class LoadingSpinner:
    """Loading spinner component."""
    
    @staticmethod
    def create(tag: str):
        """Create a loading spinner."""
        dpg.add_text(
            "Loading...",
            tag=tag,
            color=COLORS["warning"],
        )
    
    @staticmethod
    def hide(tag: str):
        """Hide loading spinner."""
        dpg.hide_item(tag)
    
    @staticmethod
    def show(tag: str):
        """Show loading spinner."""
        dpg.show_item(tag)


class ProgressBar:
    """Progress bar component."""
    
    @staticmethod
    def create(
        tag: str,
        default_value: float = 0.0,
        width: int = 200,
        height: int = 20,
    ):
        """Create a progress bar."""
        dpg.add_progress_bar(
            tag=tag,
            default_value=default_value,
            width=width,
            height=height,
        )
    
    @staticmethod
    def set_value(tag: str, value: float):
        """Set progress bar value (0.0 to 1.0)."""
        dpg.set_value(tag, value)


class Tooltip:
    """Tooltip component."""
    
    @staticmethod
    def create(parent_tag: str, text: str):
        """Create a tooltip for an element."""
        with dpg.tooltip(parent_tag):
            dpg.add_text(text)


class CollapsibleSection:
    """Collapsible section component."""
    
    @staticmethod
    def create(
        label: str,
        default_open: bool = True,
    ):
        """Create a collapsible section."""
        return dpg.collapsing_header(
            label=label,
            default_open=default_open,
        )
