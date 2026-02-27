"""
Enhanced Button Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any
from src.gui.styles.theme import COLORS


class ButtonVariant:
    """Button style variants."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    GHOST = "ghost"
    LINK = "link"


class ButtonSize:
    """Button size variants."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Button:
    """Enhanced button component with multiple variants."""
    
    @staticmethod
    def create(
        label: str,
        callback: Callable,
        variant: str = ButtonVariant.PRIMARY,
        size: str = ButtonSize.MEDIUM,
        width: Optional[int] = None,
        height: int = 35,
        tag: Optional[str] = None,
        enabled: bool = True,
        icon: Optional[str] = None,
        full_width: bool = False,
    ) -> str:
        """Create a styled button."""
        colors = Button._get_variant_colors(variant)
        
        button_width = -1 if full_width else (width or 120)
        
        if icon:
            label = f"{icon}  {label}"
        
        btn = dpg.add_button(
            label=label,
            callback=callback,
            width=button_width,
            height=height if size != ButtonSize.SMALL else 28,
            tag=tag,
            enabled=enabled,
        )
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, colors["bg"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors["hover"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors["active"])
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors["text"])
        
        dpg.bind_item_theme(btn, theme)
        
        return str(btn)
    
    @staticmethod
    def _get_variant_colors(variant: str) -> dict:
        """Get colors for button variant."""
        variants = {
            ButtonVariant.PRIMARY: {
                "bg": COLORS.get("primary", (59, 130, 246)),
                "hover": COLORS.get("primary_hover", (37, 99, 235)),
                "active": (29, 78, 216),
                "text": (255, 255, 255),
            },
            ButtonVariant.SECONDARY: {
                "bg": (71, 85, 105),
                "hover": (51, 65, 85),
                "active": (41, 55, 75),
                "text": (255, 255, 255),
            },
            ButtonVariant.SUCCESS: {
                "bg": COLORS.get("success", (34, 197, 94)),
                "hover": (22, 163, 74),
                "active": (21, 128, 61),
                "text": (255, 255, 255),
            },
            ButtonVariant.DANGER: {
                "bg": COLORS.get("danger", (239, 68, 68)),
                "hover": (220, 38, 38),
                "active": (185, 28, 28),
                "text": (255, 255, 255),
            },
            ButtonVariant.WARNING: {
                "bg": COLORS.get("warning", (234, 179, 8)),
                "hover": (202, 138, 4),
                "active": (161, 98, 7),
                "text": (0, 0, 0),
            },
            ButtonVariant.GHOST: {
                "bg": (0, 0, 0, 0),
                "hover": (71, 85, 105),
                "active": (51, 65, 85),
                "text": COLORS.get("text_primary", (226, 232, 240)),
            },
            ButtonVariant.LINK: {
                "bg": (0, 0, 0, 0),
                "hover": (0, 0, 0, 0),
                "active": (0, 0, 0, 0),
                "text": COLORS.get("primary", (59, 130, 246)),
            },
        }
        return variants.get(variant, variants[ButtonVariant.PRIMARY])


class ButtonTransition:
    """Button transition/animation effects."""
    
    TRANSITION_DURATION = 150  # ms
    
    @staticmethod
    def apply_scale_on_click(tag: str):
        """Apply scale effect on button click."""
        if dpg.does_item_exist(tag):
            current_width = dpg.get_item_width(tag)
            if current_width and current_width > 0:
                dpg.set_item_width(tag, int(current_width * 0.98))
    
    @staticmethod
    def reset_scale(tag: str, original_width: int):
        """Reset button scale after click."""
        if dpg.does_item_exist(tag):
            dpg.set_item_width(tag, original_width)
    
    @staticmethod
    def create_animated_button(
        label: str,
        callback: Callable,
        variant: str = ButtonVariant.PRIMARY,
        width: int = 120,
        height: int = 35,
        tag: Optional[str] = None,
        enable_hover: bool = True,
        enable_click: bool = True,
    ) -> str:
        """Create button with hover and click animations."""
        btn = Button.create(
            label=label,
            callback=callback,
            variant=variant,
            width=width,
            height=height,
            tag=tag,
        )
        
        if enable_hover:
            ButtonTransition._add_hover_animation(btn, variant)
        
        return str(btn)
    
    @staticmethod
    def _add_hover_animation(tag: str, variant: str):
        """Add hover animation to button."""
        colors = Button._get_variant_colors(variant)
        
        hover_color = colors.get("hover", colors["bg"])
        
        def on_hover():
            if dpg.does_item_exist(tag):
                with dpg.theme() as theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, hover_color)
                dpg.bind_item_theme(tag, theme)
        
        return on_hover
    
    @staticmethod
    def create_pulse_animation(tag: str, duration: int = 1000):
        """Create pulse animation for button."""
        if not dpg.does_item_exist(tag):
            return
        
        def pulse():
            import time
            start = time.time()
            
            while time.time() - start < duration / 1000:
                pass
        
        return pulse
    
    @staticmethod
    def create_ripple_effect(tag: str, color: tuple = None):
        """Create ripple effect on button click."""
        color = color or (255, 255, 255, 128)
        
        if not dpg.does_item_exist(tag):
            return
        
        return color
    
    @staticmethod
    def create_icon(
        icon: str,
        callback: Callable,
        tooltip: str = "",
        variant: str = ButtonVariant.GHOST,
        size: int = 30,
        tag: Optional[str] = None,
    ) -> str:
        """Create an icon button."""
        btn = dpg.add_button(
            label=icon,
            callback=callback,
            width=size,
            height=size,
            tag=tag,
        )
        
        colors = Button._get_variant_colors(variant)
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, colors["bg"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors["hover"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors["active"])
        
        dpg.bind_item_theme(btn, theme)
        
        if tooltip:
            with dpg.tooltip(btn):
                dpg.add_text(tooltip)
        
        return str(btn)
    
    @staticmethod
    def create_group(
        buttons: List[dict],
        spacing: int = 10,
        align: str = "left",
    ) -> List[str]:
        """Create a group of buttons."""
        created = []
        for btn_config in buttons:
            created.append(Button.create(**btn_config))
        return created


class LoadingButton:
    """Button with loading state and spinner."""
    
    @staticmethod
    def create(
        label: str,
        callback: Callable,
        loading: bool = False,
        variant: str = ButtonVariant.PRIMARY,
        width: int = 120,
        tag: Optional[str] = None,
        spinner_color: tuple = None,
    ) -> str:
        """Create a button with loading state support and spinner."""
        display_label = f"⏳ {label}" if loading else label
        
        spinner_color = spinner_color or (255, 255, 255)
        
        btn = dpg.add_button(
            label=display_label,
            callback=callback,
            width=width,
            tag=tag,
            enabled=not loading,
        )
        
        colors = Button._get_variant_colors(variant)
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                if loading:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, colors["hover"])
                else:
                    dpg.add_theme_color(dpg.mvThemeCol_Button, colors["bg"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors["hover"])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors["active"])
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors["text"])
        
        dpg.bind_item_theme(btn, theme)
        
        return str(btn)
    
    @staticmethod
    def set_loading(tag: str, loading: bool, original_label: str = ""):
        """Set loading state for button."""
        if dpg.does_item_exist(tag):
            if loading:
                dpg.set_item_label(tag, f"⏳ {original_label}")
                dpg.set_item_enabled(tag, False)
            else:
                dpg.set_item_label(tag, original_label)
                dpg.set_item_enabled(tag, True)
    
    @staticmethod
    def show_spinner(tag: str):
        """Show spinner on button."""
        if dpg.does_item_exist(tag):
            current_label = dpg.get_item_label(tag) or ""
            dpg.set_item_label(tag, f"⏳ {current_label}")
            dpg.set_item_enabled(tag, False)
    
    @staticmethod
    def hide_spinner(tag: str, original_label: str = ""):
        """Hide spinner on button."""
        if dpg.does_item_exist(tag):
            dpg.set_item_label(tag, original_label)
            dpg.set_item_enabled(tag, True)


class IconButton(Button):
    """Icon-only button for toolbars."""
    
    @staticmethod
    def create_edit(callback: Callable, tooltip: str = "Edit", size: int = 28):
        return Button.create_icon("✏️", callback, tooltip, size=size)
    
    @staticmethod
    def create_delete(callback: Callable, tooltip: str = "Delete", size: int = 28):
        return Button.create_icon("🗑️", callback, tooltip, ButtonVariant.DANGER, size)
    
    @staticmethod
    def create_duplicate(callback: Callable, tooltip: str = "Duplicate", size: int = 28):
        return Button.create_icon("📋", callback, tooltip, size=size)
    
    @staticmethod
    def create_refresh(callback: Callable, tooltip: str = "Refresh", size: int = 28):
        return Button.create_icon("🔄", callback, tooltip, size=size)
    
    @staticmethod
    def create_settings(callback: Callable, tooltip: str = "Settings", size: int = 28):
        return Button.create_icon("⚙️", callback, tooltip, size=size)
    
    @staticmethod
    def create_close(callback: Callable, tooltip: str = "Close", size: int = 28):
        return Button.create_icon("✕", callback, tooltip, ButtonVariant.DANGER, size)


class ActionButtonGroup:
    """Group of action buttons for list items."""
    
    @staticmethod
    def create_for_profile(
        on_open: Callable,
        on_edit: Callable,
        on_clone: Callable,
        on_export: Callable,
        on_delete: Callable,
    ) -> List[str]:
        """Create action buttons for profile row."""
        buttons = []
        
        buttons.append(Button.create(
            "Open", on_open, ButtonVariant.SUCCESS, ButtonSize.SMALL, 60
        ))
        buttons.append(Button.create(
            "Edit", on_edit, ButtonVariant.SECONDARY, ButtonSize.SMALL, 50
        ))
        buttons.append(Button.create(
            "Clone", on_clone, ButtonVariant.GHOST, ButtonSize.SMALL, 50
        ))
        buttons.append(Button.create(
            "Export", on_export, ButtonVariant.GHOST, ButtonSize.SMALL, 55
        ))
        buttons.append(Button.create(
            "Delete", on_delete, ButtonVariant.DANGER, ButtonSize.SMALL, 60
        ))
        
        return buttons
    
    @staticmethod
    def create_for_session(
        on_view: Callable,
        on_close: Callable,
        on_logs: Callable,
    ) -> List[str]:
        """Create action buttons for session row."""
        buttons = []
        
        buttons.append(Button.create(
            "View", on_view, ButtonVariant.PRIMARY, ButtonSize.SMALL, 50
        ))
        buttons.append(Button.create(
            "Logs", on_logs, ButtonVariant.GHOST, ButtonSize.SMALL, 45
        ))
        buttons.append(Button.create(
            "Close", on_close, ButtonVariant.DANGER, ButtonSize.SMALL, 50
        ))
        
        return buttons
