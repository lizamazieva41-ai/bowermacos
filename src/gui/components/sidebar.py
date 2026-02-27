"""
Collapsible Sidebar Component for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class SidebarState:
    """Sidebar state constants."""
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"


class CollapsibleSidebar:
    """Collapsible sidebar navigation component."""
    
    def __init__(
        self,
        app,
        expanded_width: int = 220,
        collapsed_width: int = 64,
    ):
        self.app = app
        self.expanded_width = expanded_width
        self.collapsed_width = collapsed_width
        self.is_collapsed = False
        
        self.nav_items = [
            {"id": "dashboard", "label": "Dashboard", "icon": "📊"},
            {"id": "profiles", "label": "Profiles", "icon": "👤"},
            {"id": "sessions", "label": "Sessions", "icon": "🌐"},
            {"id": "proxies", "label": "Proxies", "icon": "🔗"},
            {"id": "settings", "label": "Settings", "icon": "⚙️"},
        ]
    
    def create(
        self,
        tag: str,
        current_page: str,
        on_navigate: callable,
    ) -> str:
        """Create collapsible sidebar."""
        width = self.collapsed_width if self.is_collapsed else self.expanded_width
        
        sidebar_tag = f"{tag}_sidebar"
        
        with dpg.child_window(
            tag=sidebar_tag,
            width=width,
            height=-1,
            border=False,
        ):
            self._render_header()
            dpg.add_separator()
            self._render_nav(current_page, on_navigate)
            dpg.add_spacer()
            dpg.add_separator()
            self._render_footer(on_navigate)
        
        return str(sidebar_tag)
    
    def _render_header(self):
        """Render sidebar header."""
        if not self.is_collapsed:
            dpg.add_text(
                "Bower",
                color=COLORS["primary"],
                font=28,
            )
            dpg.add_text("Antidetect Browser", color=COLORS["text_secondary"], font=14)
        else:
            dpg.add_text("B", color=COLORS["primary"], font=24)
        
        dpg.add_separator()
        dpg.add_text("", height=10)
    
    def _render_nav(self, current_page: str, on_navigate: callable):
        """Render navigation items."""
        for item in self.nav_items:
            is_active = current_page == item["id"]
            self._render_nav_item(item, is_active, on_navigate)
    
    def _render_nav_item(self, item: dict, is_active: bool, on_navigate: callable):
        """Render a single navigation item."""
        icon = item["icon"]
        label = item["label"]
        page_id = item["id"]
        
        if self.is_collapsed:
            btn = dpg.add_button(
                label=icon,
                tag=f"nav_{page_id}",
                width=44,
                height=40,
                callback=lambda p=page_id: on_navigate(p),
            )
            
            if is_active:
                with dpg.theme() as theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS.get("primary"))
                dpg.bind_item_theme(btn, theme)
            
            with dpg.tooltip(btn):
                dpg.add_text(label)
        else:
            btn = dpg.add_button(
                label=f"{icon}  {label}",
                tag=f"nav_{page_id}",
                width=190,
                callback=lambda p=page_id: on_navigate(p),
            )
            
            if is_active:
                with dpg.theme() as theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS.get("primary"))
                dpg.bind_item_theme(btn, theme)
    
    def _render_footer(self, on_navigate: callable):
        """Render sidebar footer."""
        if not self.is_collapsed:
            with dpg.group():
                dpg.add_text("API Status", color=COLORS["text_muted"], font=12)
                dpg.add_text("Connected", tag="sidebar_api_status", color=COLORS["success"])
            
            dpg.add_button(
                label="Logout",
                tag="sidebar_logout",
                width=190,
                callback=lambda: on_navigate("logout"),
            )
        else:
            btn = dpg.add_button(
                label="↩",
                tag="sidebar_logout",
                width=44,
                height=30,
                callback=lambda: on_navigate("logout"),
            )
            
            with dpg.tooltip(btn):
                dpg.add_text("Logout")
    
    def toggle(self):
        """Toggle sidebar collapsed state."""
        self.is_collapsed = not self.is_collapsed
    
    def collapse(self):
        """Collapse sidebar."""
        self.is_collapsed = True
    
    def expand(self):
        """Expand sidebar."""
        self.is_collapsed = False
    
    def get_width(self) -> int:
        """Get current sidebar width."""
        return self.collapsed_width if self.is_collapsed else self.expanded_width


class SidebarManager:
    """Manages sidebar state across the application."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.sidebar = None
    
    def initialize(self, app):
        """Initialize sidebar manager."""
        self.sidebar = CollapsibleSidebar(app)
        return self.sidebar
    
    def get_sidebar(self) -> CollapsibleSidebar:
        """Get sidebar instance."""
        return self.sidebar
    
    def toggle(self):
        """Toggle sidebar."""
        if self.sidebar:
            self.sidebar.toggle()
    
    def get_width(self) -> int:
        """Get sidebar width."""
        return self.sidebar.get_width() if self.sidebar else 220


sidebar_manager = SidebarManager()
