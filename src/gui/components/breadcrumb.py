"""
Breadcrumb navigation component for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import List, Callable, Optional
from src.gui.styles.theme import COLORS


class BreadcrumbItem:
    """Single breadcrumb item."""
    
    def __init__(self, label: str, href: str = None, callback: Callable = None):
        self.label = label
        self.href = href
        self.callback = callback


class Breadcrumb:
    """Breadcrumb navigation component."""
    
    def __init__(self):
        self.items = []
        self.separator = "/"
        self.separator_icon = "›"
    
    def add_item(self, label: str, href: str = None, callback: Callable = None) -> "Breadcrumb":
        """Add breadcrumb item."""
        self.items.append(BreadcrumbItem(label, href, callback))
        return self
    
    def set_separator(self, separator: str) -> "Breadcrumb":
        """Set separator."""
        self.separator = separator
        return self
    
    def set_separator_icon(self, icon: str) -> "Breadcrumb":
        """Set separator icon."""
        self.separator_icon = icon
        return self
    
    def create(self, tag: str = "breadcrumb") -> str:
        """Create breadcrumb UI."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            for i, item in enumerate(self.items):
                if i > 0:
                    dpg.add_text(
                        self.separator_icon,
                        color=COLORS["text_muted"],
                        font=12,
                    )
                
                if item.callback:
                    dpg.add_text(
                        item.label,
                        color=COLORS["primary"],
                        callback=item.callback,
                    )
                elif item.href:
                    dpg.add_text(item.label, color=COLORS["primary"])
                else:
                    dpg.add_text(
                        item.label,
                        color=COLORS["text_secondary"],
                    )
        
        return container_tag
    
    @staticmethod
    def create_simple(
        items: List[dict],
        tag: str = "breadcrumb"
    ) -> str:
        """Create a simple breadcrumb from list of dicts."""
        bc = Breadcrumb()
        
        for item in items:
            bc.add_item(
                label=item.get("label", ""),
                href=item.get("href"),
                callback=item.get("callback"),
            )
        
        return bc.create(tag)
    
    @staticmethod
    def create_from_path(
        path: str,
        on_click: Callable = None,
        tag: str = "breadcrumb"
    ) -> str:
        """Create breadcrumb from path string."""
        parts = path.strip("/").split("/")
        bc = Breadcrumb()
        
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            
            if is_last:
                bc.add_item(label=part.title())
            else:
                bc.add_item(label=part)
        
        return bc.create(tag)


class BreadcrumbHelper:
    """Breadcrumb helper functions."""
    
    @staticmethod
    def create_dashboard() -> str:
        """Create breadcrumb for dashboard."""
        return Breadcrumb.create_simple([
            {"label": "Home", "href": "/"},
            {"label": "Dashboard"},
        ])
    
    @staticmethod
    def create_profile(profile_name: str) -> str:
        """Create breadcrumb for profile page."""
        return Breadcrumb.create_simple([
            {"label": "Home", "href": "/"},
            {"label": "Profiles", "href": "/profiles"},
            {"label": profile_name},
        ])
    
    @staticmethod
    def create_session(session_id: str) -> str:
        """Create breadcrumb for session page."""
        return Breadcrumb.create_simple([
            {"label": "Home", "href": "/"},
            {"label": "Sessions", "href": "/sessions"},
            {"label": session_id[:8] + "..."},
        ])
    
    @staticmethod
    def create_settings() -> str:
        """Create breadcrumb for settings."""
        return Breadcrumb.create_simple([
            {"label": "Home", "href": "/"},
            {"label": "Settings"},
        ])
