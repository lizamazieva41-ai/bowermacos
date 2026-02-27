"""
Card Components for Bower GUI
"""

import dearpygui.dearpygui as dpg
from typing import Callable, Optional, List, Any
from src.gui.styles.theme import COLORS


class Card:
    """Card component."""
    
    @staticmethod
    def create(
        tag: str,
        width: int = 200,
        height: int = 120,
        border: bool = True,
        shadow: bool = False,
    ) -> str:
        """Create a card container."""
        card_tag = dpg.add_child_window(
            tag=tag,
            width=width,
            height=height,
            border=border,
        )
        
        if shadow:
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvChildWindow):
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLORS.get("bg_card", (30, 41, 59)))
        
        return str(card_tag)
    
    @staticmethod
    def create_with_header(
        tag: str,
        title: str,
        subtitle: str = "",
        width: int = 200,
        height: int = 120,
        action_button: Optional[dict] = None,
    ) -> str:
        """Create a card with header."""
        with dpg.child_window(tag=tag, width=width, height=height):
            with dpg.group():
                dpg.add_text(title)
                if subtitle:
                    dpg.add_text(subtitle, color=COLORS.get("text_secondary"))
                dpg.add_separator()
                
                if action_button:
                    dpg.add_button(
                        label=action_button.get("label", ""),
                        callback=action_button.get("callback"),
                        width=-1,
                    )
        
        return str(tag)


class StatCard:
    """Statistics card component."""
    
    @staticmethod
    def create(
        title: str,
        value: str,
        tag: str,
        "",
        color: icon: str = tuple = None,
        width: int = 180,
        height: int = 100,
        on_click: Optional[Callable] = None,
    ) -> str:
        """Create a statistics card."""
        color = color or COLORS.get("primary", (59, 130, 246))
        
        with dpg.child_window(
            tag=f"stat_card_{tag}",
            width=width,
            height=height,
        ):
            with dpg.group():
                dpg.add_text(title, color=COLORS.get("text_secondary"))
                dpg.add_text(" ")
                
                with dpg.group(horizontal=True):
                    if icon:
                        dpg.add_text(icon)
                    dpg.add_text(value, tag=tag, color=color)
        
        if on_click:
            dpg.set_item_callback(f"stat_card_{tag}", on_click)
        
        return str(f"stat_card_{tag}")
    
    @staticmethod
    def create_grid(cards: List[dict]) -> List[str]:
        """Create a grid of stat cards."""
        created = []
        
        with dpg.group(horizontal=True):
            for card in cards:
                created.append(StatCard.create(**card))
        
        return created


class ProfileCard:
    """Profile card component."""
    
    @staticmethod
    def create(
        profile: dict,
        on_open: Callable,
        on_edit: Callable,
        on_delete: Callable,
        width: int = 250,
        height: int = 160,
    ) -> str:
        """Create a profile card."""
        profile_id = profile.get("id")
        profile_name = profile.get("name", "Unnamed")
        browser = profile.get("browser_engine", "chromium")
        proxy = profile.get("proxy", "No proxy")
        
        card_tag = f"profile_card_{profile_id}"
        
        with dpg.child_window(
            tag=card_tag,
            width=width,
            height=height,
        ):
            with dpg.group():
                dpg.add_text(profile_name)
                dpg.add_text(" ")
                
                dpg.add_text(f"Browser: {browser}", color=COLORS.get("text_secondary"))
                dpg.add_text(f"Proxy: {proxy[:30]}..." if len(proxy) > 30 else f"Proxy: {proxy}", 
                           color=COLORS.get("text_secondary"))
                dpg.add_text(f"Resolution: {profile.get('resolution', '1920x1080')}", 
                           color=COLORS.get("text_secondary"))
                
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Open",
                        callback=lambda: on_open(profile_id),
                        width=60,
                    )
                    dpg.add_button(
                        label="Edit",
                        callback=lambda: on_edit(profile),
                        width=50,
                    )
                    dpg.add_button(
                        label="Delete",
                        callback=lambda: on_delete(profile_id),
                        width=60,
                        color=COLORS.get("danger"),
                    )
        
        return str(card_tag)
    
    @staticmethod
    def create_grid(profiles: List[dict], callbacks: dict) -> List[str]:
        """Create a grid of profile cards."""
        cards = []
        
        with dpg.group(horizontal=True):
            for profile in profiles:
                cards.append(ProfileCard.create(
                    profile,
                    callbacks.get("on_open"),
                    callbacks.get("on_edit"),
                    callbacks.get("on_delete"),
                ))
        
        return cards


class SessionCard:
    """Session card component."""
    
    @staticmethod
    def create(
        session: dict,
        on_view: Callable,
        on_close: Callable,
        on_logs: Callable,
        width: int = 300,
        height: int = 140,
    ) -> str:
        """Create a session card."""
        session_id = session.get("session_id", "")
        profile_name = session.get("profile_name", "Unknown")
        status = session.get("status", "unknown")
        started_at = session.get("started_at", "")[:19]
        
        card_tag = f"session_card_{session_id[:8]}"
        
        status_color = (
            COLORS.get("success") if status == "active" 
            else COLORS.get("danger") if status == "error"
            else COLORS.get("text_muted")
        )
        
        with dpg.child_window(
            tag=card_tag,
            width=width,
            height=height,
        ):
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Session: {session_id[:16]}...")
                    dpg.add_text(f"● {status}", color=status_color)
                
                dpg.add_text(" ")
                dpg.add_text(f"Profile: {profile_name}", color=COLORS.get("text_secondary"))
                dpg.add_text(f"Started: {started_at}", color=COLORS.get("text_secondary"))
                
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="View",
                        callback=lambda: on_view(session_id),
                        width=60,
                    )
                    dpg.add_button(
                        label="Logs",
                        callback=lambda: on_logs(session_id),
                        width=50,
                    )
                    dpg.add_button(
                        label="Close",
                        callback=lambda: on_close(session_id),
                        width=60,
                        color=COLORS.get("danger"),
                    )
        
        return str(card_tag)


class ProxyCard:
    """Proxy card component."""
    
    @staticmethod
    def create(
        proxy: dict,
        on_test: Callable,
        on_edit: Callable,
        on_delete: Callable,
        width: int = 280,
        height: int = 120,
    ) -> str:
        """Create a proxy card."""
        proxy_id = proxy.get("id")
        name = proxy.get("name", "Unnamed")
        proxy_type = proxy.get("proxy_type", "http")
        host = proxy.get("host", "")
        port = proxy.get("port", 0)
        health = proxy.get("health_status", "unknown")
        
        card_tag = f"proxy_card_{proxy_id}"
        
        health_color = (
            COLORS.get("success") if health == "healthy"
            else COLORS.get("danger") if health == "unhealthy"
            else COLORS.get("text_muted")
        )
        
        with dpg.child_window(
            tag=card_tag,
            width=width,
            height=height,
        ):
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text(name)
                    dpg.add_text(f"● {health}", color=health_color)
                
                dpg.add_text(f"{proxy_type}://{host}:{port}", color=COLORS.get("text_secondary"))
                
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Test",
                        callback=lambda: on_test(proxy_id),
                        width=50,
                    )
                    dpg.add_button(
                        label="Edit",
                        callback=lambda: on_edit(proxy),
                        width=50,
                    )
                    dpg.add_button(
                        label="Delete",
                        callback=lambda: on_delete(proxy_id),
                        width=60,
                        color=COLORS.get("danger"),
                    )
        
        return str(card_tag)


class QuickActionCard:
    """Quick action card for dashboard."""
    
    @staticmethod
    def create(
        title: str,
        description: str,
        icon: str,
        callback: Callable,
        color: tuple = None,
        width: int = 200,
        height: int = 100,
    ) -> str:
        """Create a quick action card."""
        color = color or COLORS.get("primary", (59, 130, 246))
        
        card_tag = f"quick_action_{title.lower().replace(' ', '_')}"
        
        with dpg.child_window(
            tag=card_tag,
            width=width,
            height=height,
        ):
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text(icon)
                    dpg.add_text(title)
                
                dpg.add_text(description, color=COLORS.get("text_secondary"))
                dpg.add_text(" ")
                dpg.add_button(
                    label="Go",
                    callback=callback,
                    width=60,
                )
        
        return str(card_tag)
