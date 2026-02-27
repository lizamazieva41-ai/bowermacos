"""
View Toggle Component for Grid/List View
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class ViewMode:
    """View mode constants."""
    GRID = "grid"
    LIST = "list"


class ViewToggle:
    """Toggle between grid and list view."""
    
    def __init__(self, current_mode: str = ViewMode.GRID):
        self.mode = current_mode
    
    def create(
        self,
        tag: str,
        on_change: callable = None,
    ) -> str:
        """Create view toggle buttons."""
        container_tag = f"{tag}_view_toggle"
        
        with dpg.group(horizontal=True, tag=container_tag):
            grid_btn = dpg.add_button(
                label="▦",
                tag=f"{tag}_grid_btn",
                width=35,
                height=30,
                callback=lambda: self._set_mode(ViewMode.GRID, on_change),
            )
            
            list_btn = dpg.add_button(
                label="☰",
                tag=f"{tag}_list_btn",
                width=35,
                height=30,
                callback=lambda: self._set_mode(ViewMode.LIST, on_change),
            )
        
        self._update_button_states(tag)
        
        return container_tag
    
    def _set_mode(self, mode: str, callback: callable = None):
        """Set view mode."""
        self.mode = mode
        
        if callback:
            callback(mode)
    
    def _update_button_states(self, tag: str):
        """Update button appearance based on current mode."""
        grid_color = COLORS.get("primary") if self.mode == ViewMode.GRID else (100, 100, 100)
        list_color = COLORS.get("primary") if self.mode == ViewMode.LIST else (100, 100, 100)
        
        if dpg.does_item_exist(f"{tag}_grid_btn"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, grid_color)
            dpg.bind_item_theme(f"{tag}_grid_btn", theme)
        
        if dpg.does_item_exist(f"{tag}_list_btn"):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, list_color)
            dpg.bind_item_theme(f"{tag}_list_btn", theme)


class ViewToggleManager:
    """Manages view toggle state for different pages."""
    
    _instances = {}
    
    @classmethod
    def get(cls, page_name: str) -> ViewToggle:
        """Get or create view toggle for a page."""
        if page_name not in cls._instances:
            cls._instances[page_name] = ViewToggle()
        return cls._instances[page_name]
    
    @classmethod
    def reset(cls, page_name: str):
        """Reset view toggle for a page."""
        if page_name in cls._instances:
            del cls._instances[page_name]


class GridListView:
    """Combined grid and list view container."""
    
    def __init__(self, tag: str):
        self.tag = tag
        self.grid_items = []
        self.list_items = []
        self.view_mode = ViewMode.GRID
        self.columns = 3
    
    def set_items(self, items: list):
        """Set items to display."""
        self.grid_items = items
        self.list_items = items
    
    def render_grid(self):
        """Render items in grid view."""
        cols = self.columns
        for i in range(0, len(self.grid_items), cols):
            with dpg.group(horizontal=True):
                for item in self.grid_items[i:i+cols]:
                    yield item
    
    def render_list(self):
        """Render items in list view."""
        for item in self.list_items:
            yield item
    
    def set_columns(self, columns: int):
        """Set number of columns for grid view."""
        self.columns = columns


class ProfileGridCard:
    """Profile card for grid view."""
    
    @staticmethod
    def render(profile: dict, callbacks: dict, width: int = 250):
        """Render a profile card for grid view."""
        profile_id = profile.get("id")
        name = profile.get("name", "Unnamed")
        browser = profile.get("browser_engine", "chromium")
        
        with dpg.child_window(
            tag=f"profile_card_grid_{profile_id}",
            width=width,
            height=140,
        ):
            with dpg.group():
                dpg.add_text(name, font=16)
                dpg.add_text("", height=5)
                
                dpg.add_text(f"Browser: {browser}", color=COLORS["text_secondary"], font=12)
                dpg.add_text(f"Resolution: {profile.get('resolution', '1920x1080')}", 
                           color=COLORS["text_secondary"], font=12)
                
                proxy = profile.get("proxy", "No proxy")
                dpg.add_text(f"Proxy: {proxy[:25]}..." if len(proxy) > 25 else f"Proxy: {proxy}", 
                           color=COLORS["text_secondary"], font=12)
                
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    if callbacks.get("on_open"):
                        dpg.add_button(
                            label="Open",
                            callback=lambda: callbacks["on_open"](profile_id),
                            width=60,
                        )
                    if callbacks.get("on_edit"):
                        dpg.add_button(
                            label="Edit",
                            callback=lambda: callbacks["on_edit"](profile),
                            width=50,
                        )
                    if callbacks.get("on_delete"):
                        dpg.add_button(
                            label="Del",
                            callback=lambda: callbacks["on_delete"](profile_id),
                            width=45,
                            color=COLORS.get("danger"),
                        )


class SessionGridCard:
    """Session card for grid view."""
    
    @staticmethod
    def render(session: dict, callbacks: dict, width: int = 280):
        """Render a session card for grid view."""
        session_id = session.get("session_id", "")
        profile_name = session.get("profile_name", "Unknown")
        status = session.get("status", "unknown")
        
        status_color = (
            COLORS.get("success") if status == "active" 
            else COLORS.get("danger") if status == "error"
            else COLORS["text_muted"]
        )
        
        with dpg.child_window(
            tag=f"session_card_grid_{session_id[:8]}",
            width=width,
            height=120,
        ):
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Session: {session_id[:20]}...", font=14)
                    dpg.add_text(f"● {status}", color=status_color)
                
                dpg.add_text("", height=5)
                dpg.add_text(f"Profile: {profile_name}", color=COLORS["text_secondary"], font=12)
                dpg.add_text(f"Started: {session.get('started_at', '')[:19]}", 
                           color=COLORS["text_secondary"], font=12)
                
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    if callbacks.get("on_view"):
                        dpg.add_button(
                            label="View",
                            callback=lambda: callbacks["on_view"](session_id),
                            width=55,
                        )
                    if callbacks.get("on_logs"):
                        dpg.add_button(
                            label="Logs",
                            callback=lambda: callbacks["on_logs"](session_id),
                            width=50,
                        )
                    if callbacks.get("on_close"):
                        dpg.add_button(
                            label="Close",
                            callback=lambda: callbacks["on_close"](session_id),
                            width=60,
                            color=COLORS.get("danger"),
                        )


class ViewToggleHelper:
    """Helper functions for view toggle."""
    
    @staticmethod
    def create_toggle_button(
        tag: str,
        current_mode: str,
        callback: callable = None,
    ) -> str:
        """Create a simple toggle button."""
        toggle = ViewToggle(current_mode)
        return toggle.create(tag, callback)
    
    @staticmethod
    def render_grid_view(items: list, render_func: callable, columns: int = 3):
        """Render items in grid layout."""
        for i in range(0, len(items), columns):
            with dpg.group(horizontal=True):
                for item in items[i:i+columns]:
                    render_func(item)
    
    @staticmethod
    def render_list_view(items: list, render_func: callable):
        """Render items in list layout."""
        for item in items:
            render_func(item)
