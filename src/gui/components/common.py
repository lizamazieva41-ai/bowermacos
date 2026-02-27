"""
Common UI Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any
from src.gui.styles.theme import COLORS


class Badge:
    """Status badge component."""
    
    @staticmethod
    def create(
        label: str,
        variant: str = "default",
        size: str = "medium",
    ) -> str:
        """Create a status badge."""
        colors = {
            "default": (100, 116, 139),
            "success": (34, 197, 94),
            "warning": (234, 179, 8),
            "danger": (239, 68, 68),
            "info": (59, 130, 246),
            "primary": (99, 102, 241),
        }
        
        color = colors.get(variant, colors["default"])
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, color)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        
        badge = dpg.add_button(
            label=label,
            enabled=False,
            width=-1,
        )
        
        dpg.bind_item_theme(badge, theme)
        
        return str(badge)
    
    @staticmethod
    def create_status(status: str) -> str:
        """Create a status badge based on status string."""
        variants = {
            "active": "success",
            "running": "success",
            "healthy": "success",
            "inactive": "default",
            "stopped": "danger",
            "error": "danger",
            "unhealthy": "danger",
            "warning": "warning",
            "pending": "warning",
        }
        
        variant = variants.get(status.lower(), "default")
        return Badge.create(status.capitalize(), variant)


class ProgressBar:
    """Progress bar component."""
    
    @staticmethod
    def create(
        tag: str,
        value: float = 0.0,
        width: int = 200,
        height: int = 20,
        show_label: bool = True,
        color: tuple = None,
    ) -> str:
        """Create a progress bar."""
        color = color or COLORS.get("primary", (59, 130, 246))
        
        progress = dpg.add_progress_bar(
            tag=tag,
            default_value=value,
            width=width,
            height=height,
            overlay=f"{int(value * 100)}%" if show_label else "",
        )
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvProgressBar):
                dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, color)
        
        dpg.bind_item_theme(progress, theme)
        
        return str(progress)
    
    @staticmethod
    def set_value(tag: str, value: float):
        """Update progress bar value."""
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, value)


class Spinner:
    """Loading spinner component."""
    
    @staticmethod
    def create(
        tag: str,
        size: int = 30,
    ) -> str:
        """Create a loading spinner."""
        spinner_tag = f"spinner_{tag}"
        
        dpg.add_text(
            "Loading...",
            tag=spinner_tag,
            color=COLORS.get("warning"),
        )
        
        return str(spinner_tag)
    
    @staticmethod
    def show(tag: str):
        """Show spinner."""
        if dpg.does_item_exist(f"spinner_{tag}"):
            dpg.show_item(f"spinner_{tag}")
    
    @staticmethod
    def hide(tag: str):
        """Hide spinner."""
        if dpg.does_item_exist(f"spinner_{tag}"):
            dpg.hide_item(f"spinner_{tag}")


class EmptyState:
    """Empty state component."""
    
    @staticmethod
    def create(
        title: str,
        description: str,
        icon: str = "📭",
        action_label: str = "",
        action_callback: Optional[Callable] = None,
    ) -> str:
        """Create an empty state."""
        tag = f"empty_{title.lower().replace(' ', '_')}"
        
        with dpg.group(horizontal=False):
            dpg.add_text(icon, font=48)
            dpg.add_text("", height=10)
            dpg.add_text(title, font=18)
            dpg.add_text(description, color=COLORS.get("text_secondary"))
            
            if action_label and action_callback:
                dpg.add_text("", height=15)
                dpg.add_button(
                    label=action_label,
                    callback=action_callback,
                    width=150,
                )
        
        return str(tag)


class Separator:
    """Separator component."""
    
    @staticmethod
    def create_horizontal(margin: int = 10):
        """Create horizontal separator."""
        dpg.add_separator()
    
    @staticmethod
    def create_vertical(height: int = 20):
        """Create vertical separator."""
        dpg.add_text("|")


class Spacer:
    """Spacer component."""
    
    @staticmethod
    def create(height: int = 10, width: int = 0):
        """Create a spacer."""
        if width > 0:
            dpg.add_text("", width=width)
        else:
            dpg.add_text("", height=height)


class Label:
    """Label component."""
    
    @staticmethod
    def create(
        text: str,
        size: str = "medium",
        color: str = "default",
    ) -> str:
        """Create a styled label."""
        colors = {
            "default": COLORS.get("text_primary"),
            "secondary": COLORS.get("text_secondary"),
            "muted": COLORS.get("text_muted"),
            "primary": COLORS.get("primary"),
            "success": COLORS.get("success"),
            "warning": COLORS.get("warning"),
            "danger": COLORS.get("danger"),
        }
        
        fonts = {
            "small": 12,
            "medium": 14,
            "large": 16,
            "xlarge": 18,
            "title": 24,
        }
        
        font = fonts.get(size, 14)
        text_color = colors.get(color, COLORS.get("text_primary"))
        
        label = dpg.add_text(text, color=text_color, font=font)
        
        return str(label)
    
    @staticmethod
    def create_required(label: str) -> str:
        """Create a label with required indicator."""
        return Label.create(f"{label} *", color="danger")


class Divider:
    """Divider component."""
    
    @staticmethod
    def create():
        """Create a divider."""
        dpg.add_separator()


class Icon:
    """Icon component."""
    
    @staticmethod
    def create(icon: str, size: int = 20, color: tuple = None) -> str:
        """Create an icon."""
        icon_label = dpg.add_text(icon, font=size)
        
        if color:
            dpg.configure_item(icon_label, color=color)
        
        return str(icon_label)


class Avatar:
    """Avatar component."""
    
    @staticmethod
    def create(
        name: str,
        size: int = 40,
        color: tuple = None,
    ) -> str:
        """Create an avatar with initials."""
        initials = "".join([c[0].upper() for c in name.split()[:2]])
        color = color or COLORS.get("primary", (59, 130, 246))
        
        avatar = dpg.add_button(
            label=initials,
            width=size,
            height=size,
        )
        
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, color)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
        
        dpg.bind_item_theme(avatar, theme)
        
        return str(avatar)


class Divider:
    """Loading overlay component."""
    
    @staticmethod
    def create_loading(tag: str, message: str = "Loading..."):
        """Create a loading overlay."""
        overlay_tag = f"loading_overlay_{tag}"
        
        with dpg.window(
            tag=overlay_tag,
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            modal=True,
        ):
            with dpg.group():
                dpg.add_text("⏳", font=48)
                dpg.add_text(message)
        
        return str(overlay_tag)
    
    @staticmethod
    def hide_loading(tag: str):
        """Hide loading overlay."""
        if dpg.does_item_exist(f"loading_overlay_{tag}"):
            dpg.delete_item(f"loading_overlay_{tag}")
