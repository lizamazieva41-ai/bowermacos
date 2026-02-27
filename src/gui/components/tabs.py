"""
Tabs component for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Dict
from src.gui.styles.theme import COLORS


class Tab:
    """Single tab item."""
    
    def __init__(self, id: str, label: str, icon: str = None):
        self.id = id
        self.label = label
        self.icon = icon


class Tabs:
    """Tabs component."""
    
    def __init__(self, tabs: List[Dict] = None):
        self.tabs = [Tab(**t) if isinstance(t, dict) else t for t in (tabs or [])]
        self.active_tab = None
        self.on_change: Optional[Callable] = None
    
    def add_tab(self, id: str, label: str, icon: str = None) -> "Tabs":
        """Add a tab."""
        self.tabs.append(Tab(id, label, icon))
        return self
    
    def set_active(self, tab_id: str):
        """Set active tab."""
        self.active_tab = tab_id
        if self.on_change:
            self.on_change(tab_id)
    
    def set_on_change(self, callback: Callable):
        """Set tab change callback."""
        self.on_change = callback
    
    def create(self, tag: str = "tabs") -> str:
        """Create tabs UI."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            for tab in self.tabs:
                is_active = tab.id == self.active_tab
                
                btn = dpg.add_button(
                    label=f"{tab.icon + ' ' if tab.icon else ''}{tab.label}",
                    tag=f"{tag}_{tab.id}",
                    width=-1,
                    callback=lambda t=tab.id: self.set_active(t),
                )
                
                if is_active:
                    with dpg.theme() as theme:
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["primary"])
                    dpg.bind_item_theme(btn, theme)
        
        return container_tag
    
    @staticmethod
    def create_horizontal(
        tabs: List[Dict],
        active: str = None,
        on_change: Callable = None,
        tag: str = "tabs",
    ) -> str:
        """Create horizontal tabs."""
        t = Tabs(tabs)
        t.active_tab = active or (tabs[0]["id"] if tabs else None)
        t.on_change = on_change
        return t.create(tag)


class TabPanel:
    """Tab panel with content."""
    
    def __init__(self):
        self.panels = {}
        self.active_panel = None
    
    def add_panel(self, id: str, content_callback: Callable):
        """Add a panel."""
        self.panels[id] = content_callback
    
    def set_active(self, panel_id: str):
        """Set active panel."""
        self.active_panel = panel_id
    
    def render(self):
        """Render active panel."""
        if self.active_panel and self.active_panel in self.panels:
            self.panels[self.active_panel]()


class TabContainer:
    """Complete tab container with tabs and panels."""
    
    def __init__(self, tabs: List[Dict] = None):
        self.tabs_component = Tabs(tabs)
        self.tab_panels = TabPanel()
    
    def add_panel(self, tab_id: str, content_callback: Callable):
        """Add panel content for a tab."""
        self.tab_panels.add_panel(tab_id, content_callback)
    
    def create(self, tag: str = "tab_container") -> str:
        """Create tab container."""
        container_tag = f"{tag}_container"
        
        self.tabs_component.create(tag)
        
        dpg.add_separator()
        
        self.tab_panels.render()
        
        return container_tag


class VerticalTabs:
    """Vertical tabs component."""
    
    def __init__(self, tabs: List[Dict] = None):
        self.tabs = tabs or []
        self.active_tab = None
        self.on_change: Optional[Callable] = None
    
    def create(self, tag: str = "vertical_tabs") -> str:
        """Create vertical tabs."""
        container_tag = f"{tag}_container"
        
        with dpg.group(horizontal=True, tag=container_tag):
            with dpg.child_window(width=200, tag=f"{tag}_sidebar"):
                for tab in self.tabs:
                    is_active = tab.get("id") == self.active_tab
                    
                    btn = dpg.add_button(
                        label=tab.get("label", ""),
                        tag=f"{tag}_{tab.get('id')}",
                        width=-1,
                        callback=lambda t=tab.get("id"): self._on_tab_click(t),
                    )
                    
                    if is_active:
                        with dpg.theme() as theme:
                            with dpg.theme_component(dpg.mvButton):
                                dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["primary"])
                        dpg.bind_item_theme(btn, theme)
            
            with dpg.child_window(tag=f"{tag}_content", width=-1):
                pass
        
        return container_tag
    
    def _on_tab_click(self, tab_id: str):
        """Handle tab click."""
        self.active_tab = tab_id
        if self.on_change:
            self.on_change(tab_id)


class TabHelper:
    """Tab helper functions."""
    
    @staticmethod
    def create_settings_tabs() -> List[Dict]:
        """Create settings tabs."""
        return [
            {"id": "general", "label": "General", "icon": "⚙️"},
            {"id": "appearance", "label": "Appearance", "icon": "🎨"},
            {"id": "account", "label": "Account", "icon": "👤"},
            {"id": "advanced", "label": "Advanced", "icon": "🔧"},
        ]
    
    @staticmethod
    def create_profile_tabs() -> List[Dict]:
        """Create profile editor tabs."""
        return [
            {"id": "basic", "label": "Basic", "icon": "📋"},
            {"id": "browser", "label": "Browser", "icon": "🌐"},
            {"id": "proxy", "label": "Proxy", "icon": "🔗"},
            {"id": "advanced", "label": "Advanced", "icon": "⚡"},
        ]
