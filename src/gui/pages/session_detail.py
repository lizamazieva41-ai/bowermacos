"""
Session Detail Modal for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class SessionDetailModal:
    """Modal for displaying session details with real-time updates."""
    
    def __init__(self, app):
        self.app = app
        self.session_id = None
        self.ws_client = None
        self.console_logs = []
    
    def show(self, session_id: str):
        """Show session detail modal."""
        self.session_id = session_id
        self.console_logs = []
        
        try:
            session = self.app.api_client.get_session(session_id)
            if not session:
                print(f"Session {session_id} not found")
                return
            
            self._render_modal(session)
            self._connect_websocket(session_id)
            
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def _connect_websocket(self, session_id: str):
        """Connect to WebSocket for real-time updates."""
        try:
            if hasattr(self.app, 'rt_manager'):
                self.ws_client = self.app.rt_manager.connect_session(session_id)
                self.ws_client.on("console", self._on_console_message)
                self.ws_client.on("session_update", self._on_session_update)
                print(f"WebSocket connected for session {session_id}")
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
    
    def _on_console_message(self, data: dict):
        """Handle console message from WebSocket."""
        log_type = data.get("type", "log")
        message = data.get("message", "")
        timestamp = data.get("timestamp", "")
        
        log_entry = f"[{timestamp}] {log_type}: {message}"
        self.console_logs.append(log_entry)
        
        if len(self.console_logs) > 100:
            self.console_logs = self.console_logs[-100:]
        
        self._update_console_display()
    
    def _on_session_update(self, data: dict):
        """Handle session update from WebSocket."""
        self._update_resource_display(data)
    
    def _update_console_display(self):
        """Update console display with new logs."""
        if dpg.does_item_exist("session_console_output"):
            console_text = "\n".join(self.console_logs[-50:])
            dpg.set_value("session_console_output", console_text)
    
    def _update_resource_display(self, data: dict):
        """Update resource usage display."""
        if dpg.does_item_exist("session_cpu_bar"):
            cpu = data.get("cpu_percent", 0)
            dpg.set_value("session_cpu_bar", cpu / 100)
        
        if dpg.does_item_exist("session_memory_bar"):
            memory = data.get("memory_mb", 0)
            memory_percent = min(memory / 500 * 100, 100)
            dpg.set_value("session_memory_bar", memory_percent / 100)
    
    def disconnect(self):
        """Disconnect WebSocket when modal closes."""
        if self.session_id and hasattr(self.app, 'rt_manager'):
            self.app.rt_manager.disconnect_session(self.session_id)
    
    def show(self, session_id: str):
        """Show session detail modal."""
        try:
            session = self.app.api_client.get_session(session_id)
            if not session:
                print(f"Session {session_id} not found")
                return
            
            self._render_modal(session)
            
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def _render_modal(self, session: dict):
        """Render the session detail modal."""
        session_id = session.get("session_id", "")
        
        with dpg.window(
            tag="session_detail_modal",
            label=f"Session: {session_id[:20]}...",
            width=600,
            height=500,
            modal=True,
            pos=[150, 100],
        ):
            with dpg.group(horizontal=True):
                self._render_session_info(session)
                self._render_session_stats(session)
            
            dpg.add_separator()
            
            dpg.add_text("Resource Usage")
            self._render_resource_usage(session)
            
            dpg.add_separator()
            
            dpg.add_text("Fingerprint Status")
            self._render_fingerprint_status(session)
            
            dpg.add_separator()
            
            dpg.add_text("Console Output (Real-time)")
            dpg.add_text(" ")
            with dpg.child_window(tag="console_window", height=150):
                dpg.add_input_text(
                    tag="session_console_output",
                    default_value="",
                    multiline=True,
                    readonly=True,
                    width=-1,
                    height=-1,
                )
            
            dpg.add_separator()
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Close Session",
                    callback=lambda: self._close_session(session_id),
                    width=150,
                    color=COLORS.get("danger"),
                )
                dpg.add_button(
                    label="Clear Console",
                    callback=self._clear_console,
                    width=120,
                )
                dpg.add_button(
                    label="Refresh",
                    callback=lambda: self.show(session_id),
                    width=100,
                )
                dpg.add_button(
                    label="Close",
                    callback=lambda: [self.disconnect(), dpg.close_modal("session_detail_modal")],
                    width=80,
                )
    
    def _clear_console(self):
        """Clear console logs."""
        self.console_logs = []
        if dpg.does_item_exist("session_console_output"):
            dpg.set_value("session_console_output", "")
    
    def _render_session_info(self, session: dict):
        """Render basic session info."""
        with dpg.child_window(width=280, height=180):
            dpg.add_text("Session Information")
            dpg.add_separator()
            
            dpg.add_text("Session ID:", color=COLORS["text_secondary"])
            dpg.add_text(session.get("session_id", "")[:30])
            
            dpg.add_text(" ")
            dpg.add_text("Profile:", color=COLORS["text_secondary"])
            dpg.add_text(session.get("profile_name", "Unknown"))
            
            dpg.add_text(" ")
            dpg.add_text("Status:", color=COLORS["text_secondary"])
            status = session.get("status", "unknown")
            status_color = (
                COLORS.get("success") if status == "active"
                else COLORS.get("danger") if status == "error"
                else COLORS["text_muted"]
            )
            dpg.add_text(status.capitalize(), color=status_color)
            
            dpg.add_text(" ")
            dpg.add_text("Started:", color=COLORS["text_secondary"])
            dpg.add_text(session.get("started_at", "")[:19])
    
    def _render_session_stats(self, session: dict):
        """Render session statistics."""
        with dpg.child_window(width=280, height=180):
            dpg.add_text("Statistics")
            dpg.add_separator()
            
            dpg.add_text("URL:", color=COLORS["text_secondary"])
            url = session.get("current_url", "N/A")
            dpg.add_text(url[:40] + "..." if len(url) > 40 else url)
            
            dpg.add_text(" ")
            dpg.add_text("Page Title:", color=COLORS["text_secondary"])
            dpg.add_text(session.get("page_title", "N/A")[:40])
            
            dpg.add_text(" ")
            dpg.add_text("User Agent:", color=COLORS["text_secondary"])
            ua = session.get("user_agent", "N/A")
            dpg.add_text(ua[:35] + "..." if len(ua) > 35 else ua)
            
            dpg.add_text(" ")
            dpg.add_text("Browser:", color=COLORS["text_secondary"])
            dpg.add_text(session.get("browser_engine", "chromium"))
    
    def _render_resource_usage(self, session: dict):
        """Render resource usage bars."""
        resource_usage = session.get("resource_usage", {})
        
        cpu_percent = resource_usage.get("cpu_percent", 0)
        memory_mb = resource_usage.get("memory_mb", 0)
        
        dpg.add_text("CPU Usage:", color=COLORS["text_secondary"])
        with dpg.progress_bar(
            tag="session_cpu_bar",
            default_value=cpu_percent / 100,
            width=-1,
            height=15,
        ):
            dpg.add_text(f"{cpu_percent}%")
        
        dpg.add_text(" ")
        dpg.add_text("Memory Usage:", color=COLORS["text_secondary"])
        
        memory_percent = min(memory_mb / 500 * 100, 100)
        with dpg.progress_bar(
            tag="session_memory_bar",
            default_value=memory_percent / 100,
            width=-1,
            height=15,
        ):
            dpg.add_text(f"{memory_mb} MB")
    
    def _render_fingerprint_status(self, session: dict):
        """Render fingerprint protection status."""
        stealth_settings = session.get("stealth_settings", {})
        
        items = [
            ("Canvas Protection", stealth_settings.get("canvas", True)),
            ("WebGL Protection", stealth_settings.get("webgl", True)),
            ("WebRTC Protection", stealth_settings.get("webrtc", True)),
            ("Audio Protection", stealth_settings.get("audio", True)),
            ("Font Protection", stealth_settings.get("fonts", True)),
            ("Hide WebDriver", stealth_settings.get("hide_webdriver", True)),
        ]
        
        with dpg.group(horizontal=True):
            for label, enabled in items:
                color = COLORS.get("success") if enabled else COLORS.get("danger")
                icon = "✓" if enabled else "✗"
                dpg.add_text(f"{icon} {label}", color=color)
    
    def _close_session(self, session_id: str):
        """Close the session."""
        try:
            self.app.api_client.close_session(session_id)
            dpg.close_modal("session_detail_modal")
            
            if hasattr(self.app, 'pages') and 'sessions' in self.app.pages:
                self.app.pages['sessions'].refresh()
                
            print(f"Session {session_id} closed")
            
        except Exception as e:
            print(f"Error closing session: {e}")


def show_session_detail(app, session_id: str):
    """Helper function to show session detail."""
    modal = SessionDetailModal(app)
    modal.show(session_id)
