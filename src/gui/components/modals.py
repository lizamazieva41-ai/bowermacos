"""
Modal and Dialog Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any
from src.gui.styles.theme import COLORS


class Modal:
    """Modal dialog component."""
    
    @staticmethod
    def create(
        tag: str,
        label: str,
        width: int = 500,
        height: int = 400,
        modal: bool = True,
    ) -> str:
        """Create a modal dialog."""
        modal_tag = dpg.add_window(
            tag=tag,
            label=label,
            width=width,
            height=height,
            modal=modal,
            no_title_bar=False,
            no_resize=True,
            no_move=False,
            pos=[200, 100],
        )
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvWindow):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COLORS.get("bg_secondary", (30, 41, 59)))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, COLORS.get("bg_primary", (15, 23, 42)))
        
        dpg.bind_item_theme(modal_tag, theme)
        
        return str(modal_tag)
    
    @staticmethod
    def create_form(
        tag: str,
        title: str,
        fields: List[dict],
        on_submit: Callable,
        on_cancel: Optional[Callable] = None,
        submit_label: str = "Submit",
        cancel_label: str = "Cancel",
        width: int = 450,
    ) -> str:
        """Create a modal with form fields."""
        with dpg.modal(tag=tag, label=title, width=width):
            for field in fields:
                field_type = field.get("type", "text")
                
                if field_type == "text":
                    dpg.add_input_text(
                        label=field.get("label", ""),
                        tag=field.get("tag"),
                        default_value=field.get("default", ""),
                        width=field.get("width", 350),
                        hint=field.get("hint", ""),
                        password=field.get("password", False),
                    )
                elif field_type == "combo":
                    dpg.add_combo(
                        label=field.get("label", ""),
                        tag=field.get("tag"),
                        items=field.get("items", []),
                        default_value=field.get("default", ""),
                        width=field.get("width", 350),
                    )
                elif field_type == "checkbox":
                    dpg.add_checkbox(
                        label=field.get("label", ""),
                        tag=field.get("tag"),
                        default_value=field.get("default", False),
                    )
                
                dpg.add_text(" ")
            
            dpg.add_separator()
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label=submit_label,
                    callback=on_submit,
                    width=120,
                )
                dpg.add_button(
                    label=cancel_label,
                    callback=lambda: dpg.close_modal(tag) if not on_cancel else on_cancel(),
                    width=100,
                )
        
        return str(tag)


class ConfirmDialog:
    """Confirmation dialog component."""
    
    @staticmethod
    def show(
        title: str,
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        confirm_variant: str = "danger",
    ) -> str:
        """Show a confirmation dialog."""
        tag = f"confirm_{id(message)}"
        
        with dpg.modal(tag=tag, label=title, width=400, height=150):
            dpg.add_text(message, wrap=350)
            dpg.add_text(" ")
            
            with dpg.group(horizontal=True):
                variant_colors = {
                    "danger": COLORS.get("danger", (239, 68, 68)),
                    "primary": COLORS.get("primary", (59, 130, 246)),
                    "success": COLORS.get("success", (34, 197, 94)),
                }
                
                with dpg.theme() as confirm_theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, variant_colors.get(confirm_variant))
                
                dpg.add_button(
                    label=confirm_label,
                    callback=lambda: [on_confirm(), dpg.close_modal(tag)],
                    width=100,
                )
                dpg.add_button(
                    label=cancel_label,
                    callback=lambda: [on_cancel() if on_cancel else None, dpg.close_modal(tag)],
                    width=80,
                )
        
        return str(tag)
    
    @staticmethod
    def show_delete(
        item_name: str,
        on_confirm: Callable,
    ) -> str:
        """Show a delete confirmation dialog."""
        return ConfirmDialog.show(
            title="Confirm Delete",
            message=f"Are you sure you want to delete '{item_name}'? This action cannot be undone.",
            on_confirm=on_confirm,
            confirm_variant="danger",
        )


class Drawer:
    """Slide-in drawer component."""
    
    @staticmethod
    def create(
        tag: str,
        title: str,
        width: int = 400,
        position: str = "right",
    ) -> str:
        """Create a drawer."""
        viewport_width = dpg.get_viewport_width()
        
        if position == "right":
            x_pos = viewport_width - width - 20
        else:
            x_pos = 20
        
        drawer_tag = dpg.add_window(
            tag=tag,
            label=title,
            width=width,
            height=dpg.get_viewport_height() - 100,
            no_title_bar=False,
            no_resize=True,
            no_move=True,
            pos=[x_pos, 50],
            modal=False,
        )
        
        return str(drawer_tag)


class Alert:
    """Alert/Message box component."""
    
    @staticmethod
    def show(
        message: str,
        alert_type: str = "info",
        duration: int = 3000,
    ) -> str:
        """Show an alert message."""
        colors = {
            "info": COLORS.get("primary", (59, 130, 246)),
            "success": COLORS.get("success", (34, 197, 94)),
            "warning": COLORS.get("warning", (234, 179, 8)),
            "error": COLORS.get("danger", (239, 68, 68)),
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
        }
        
        color = colors.get(alert_type, colors["info"])
        icon = icons.get(alert_type, icons["info"])
        
        tag = f"alert_{id(message)}"
        
        with dpg.window(
            tag=tag,
            width=350,
            height=50,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            pos=[dpg.get_viewport_width() - 370, 10],
            always_on_top=True,
        ):
            dpg.add_text(f"{icon}  {message}", color=color)
        
        return str(tag)


class Tooltip:
    """Tooltip component."""
    
    @staticmethod
    def create(parent_tag: str, text: str, delay: int = 0):
        """Create a tooltip for an element."""
        with dpg.tooltip(parent_tag):
            dpg.add_text(text, wrap=200)


class Popover:
    """Popover menu component."""
    
    @staticmethod
    def create(
        tag: str,
        trigger_tag: str,
        items: List[dict],
    ) -> str:
        """Create a popover menu."""
        with dpg.popup(trigger_tag, tag=tag, mousebutton=dpg.mvMouseButton_Left):
            for item in items:
                if item.get("separator"):
                    dpg.add_separator()
                else:
                    dpg.add_menu_item(
                        label=item.get("label", ""),
                        callback=item.get("callback"),
                        enabled=item.get("enabled", True),
                    )
        
        return str(tag)


class ContextMenu:
    """Context menu component."""
    
    @staticmethod
    def create(
        tag: str,
        items: List[dict],
    ) -> str:
        """Create a context menu."""
        with dpg.menu(tag=tag, parent=tag):
            for item in items:
                if item.get("separator"):
                    dpg.add_separator()
                elif item.get("submenu"):
                    with dpg.menu(label=item.get("label", "")):
                        for subitem in item.get("items", []):
                            dpg.add_menu_item(
                                label=subitem.get("label", ""),
                                callback=subitem.get("callback"),
                            )
                else:
                    dpg.add_menu_item(
                        label=item.get("label", ""),
                        callback=item.get("callback"),
                        enabled=item.get("enabled", True),
                    )
        
        return str(tag)
