"""
Tabbed Profile Editor for Bower GUI
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class ProfileEditorTab:
    """Profile editor tabs."""
    BASIC = "basic"
    BROWSER = "browser"
    DISPLAY = "display"
    NETWORK = "network"
    SECURITY = "security"
    ADVANCED = "advanced"


class ProfileEditor:
    """Tabbed profile editor modal."""
    
    def __init__(self, app, mode: str = "create"):
        self.app = app
        self.mode = mode
        self.current_step = 0
        self.total_steps = 5
        self.current_tab = ProfileEditorTab.BASIC
        self.profile_data = {}
        
        self.steps = [
            {"id": "basic", "label": "Basic Info", "icon": "📋"},
            {"id": "browser", "label": "Browser", "icon": "🌐"},
            {"id": "proxy", "label": "Proxy", "icon": "🔗"},
            {"id": "advanced", "label": "Advanced", "icon": "⚡"},
            {"id": "review", "label": "Review", "icon": "✅"},
        ]
    
    def show_create_modal(self):
        """Show create profile modal with tabs."""
        with dpg.window(
            tag="profile_editor_modal",
            label="Create New Profile",
            width=700,
            height=600,
            modal=True,
            pos=[100, 50],
        ):
            self._create_editor_content()
    
    def show_edit_modal(self, profile: dict):
        """Show edit profile modal with tabs."""
        self.profile_data = profile
        
        with dpg.window(
            tag="profile_editor_modal",
            label=f"Edit Profile: {profile.get('name', '')}",
            width=700,
            height=600,
            modal=True,
            pos=[100, 50],
        ):
            self._create_editor_content(profile)
    
    def _create_editor_content(self, profile: dict = None):
        """Create wizard editor content."""
        profile = profile or {}
        
        self._render_progress_bar()
        
        with dpg.group(horizontal=True):
            self._create_wizard_sidebar()
            self._create_wizard_content(profile)
        
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            if self.current_step > 0:
                dpg.add_button(
                    label="← Back",
                    callback=self._prev_step,
                    width=100,
                )
            
            dpg.add_text("", width=-1)
            
            if self.current_step < self.total_steps - 1:
                dpg.add_button(
                    label="Next →",
                    callback=self._next_step,
                    width=100,
                )
            else:
                if self.mode == "create":
                    dpg.add_button(
                        label="Create Profile",
                        callback=lambda: self._save_profile(profile.get("id")),
                        width=150,
                    )
                else:
                    dpg.add_button(
                        label="Save Changes",
                        callback=lambda: self._save_profile(profile.get("id")),
                        width=150,
                    )
            
            dpg.add_button(
                label="Cancel",
                callback=lambda: dpg.close_modal("profile_editor_modal"),
                width=100,
            )
    
    def _render_progress_bar(self):
        """Render progress bar for wizard."""
        dpg.add_text(f"Step {self.current_step + 1} of {self.total_steps}")
        dpg.add_text(" ")
        
        progress = (self.current_step + 1) / self.total_steps
        with dpg.progress_bar(
            tag="wizard_progress",
            default_value=progress,
            width=-1,
            height=10,
        ):
            dpg.add_text(f"{int(progress * 100)}%")
        
        dpg.add_text(" ")
    
    def _create_wizard_sidebar(self):
        """Create wizard step sidebar."""
        with dpg.child_window(width=180, height=450):
            for i, step in enumerate(self.steps):
                is_active = i == self.current_step
                is_completed = i < self.current_step
                
                if is_active:
                    dpg.add_button(
                        label=f"{step['icon']} {step['label']}",
                        width=-1,
                    )
                elif is_completed:
                    dpg.add_button(
                        label=f"✓ {step['label']}",
                        callback=lambda idx=i: self._go_to_step(idx),
                        width=-1,
                    )
                else:
                    dpg.add_button(
                        label=f"  {step['label']}",
                        callback=lambda idx=i: self._go_to_step(idx),
                        width=-1,
                    )
    
    def _create_wizard_content(self, profile: dict):
        """Create content for current wizard step."""
        step_id = self.steps[self.current_step]["id"]
        
        with dpg.child_window(width=480, height=450):
            if step_id == "basic":
                self._render_basic_step(profile)
            elif step_id == "browser":
                self._render_browser_step(profile)
            elif step_id == "proxy":
                self._render_proxy_step(profile)
            elif step_id == "advanced":
                self._render_advanced_step(profile)
            elif step_id == "review":
                self._render_review_step(profile)
    
    def _render_basic_step(self, profile: dict):
        """Render Basic Info step."""
        dpg.add_text("📋 Basic Information")
        dpg.add_text(" ")
        
        dpg.add_text("Profile Name *", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_profile_name",
            default_value=profile.get("name", ""),
            width=400,
            hint="Enter profile name",
        )
        dpg.add_text(" ")
        
        dpg.add_text("Description", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_profile_description",
            default_value=profile.get("description", ""),
            width=400,
            height=60,
            hint="Optional description",
            multiline=True,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Use Case", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_profile_use_case",
            items=["general", "social_media", "automation", "scraping", "testing"],
            default_value=profile.get("use_case", "general"),
            width=200,
        )
    
    def _render_browser_step(self, profile: dict):
        """Render Browser step."""
        dpg.add_text("🌐 Browser Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Browser Engine", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_browser_engine",
            items=["chromium", "firefox", "webkit"],
            default_value=profile.get("browser_engine", "chromium"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("User Agent", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_user_agent",
            default_value=profile.get("user_agent", ""),
            width=400,
            height=40,
            hint="Leave empty for auto-generated",
            multiline=True,
        )
        dpg.add_text(" ")
        
        dpg.add_checkbox(
            tag="wizard_headless",
            label="Run in Headless Mode",
            default_value=profile.get("headless", True),
        )
    
    def _render_proxy_step(self, profile: dict):
        """Render Proxy step."""
        dpg.add_text("🔗 Proxy Configuration")
        dpg.add_text(" ")
        
        dpg.add_text("Proxy URL", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_proxy",
            default_value=profile.get("proxy", ""),
            width=400,
            hint="http://proxy:port or socks5://proxy:port",
        )
        dpg.add_text(" ")
        
        dpg.add_text("Proxy Type", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_proxy_type",
            items=["http", "https", "socks5"],
            default_value="http",
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Username (optional)", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_proxy_username",
            default_value=profile.get("proxy_username", ""),
            width=300,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Password (optional)", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="wizard_proxy_password",
            default_value=profile.get("proxy_password", ""),
            width=300,
            password=True,
        )
    
    def _render_advanced_step(self, profile: dict):
        """Render Advanced step."""
        dpg.add_text("⚡ Advanced Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Resolution", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_resolution",
            items=["1920x1080", "1366x768", "1280x720", "2560x1440", "Random"],
            default_value=profile.get("resolution", "1920x1080"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Timezone", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_timezone",
            items=["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo", "System"],
            default_value=profile.get("timezone", "System"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Language", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="wizard_language",
            items=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "System"],
            default_value=profile.get("language", "en-US"),
            width=200,
        )
        
        dpg.add_text(" ")
        
        dpg.add_checkbox(
            tag="wizard_stealth_canvas",
            label="Canvas Fingerprint Protection",
            default_value=profile.get("stealth_canvas", True),
        )
        
        dpg.add_checkbox(
            tag="wizard_stealth_webrtc",
            label="WebRTC Protection",
            default_value=profile.get("stealth_webrtc", True),
        )
    
    def _render_review_step(self, profile: dict):
        """Render Review step."""
        dpg.add_text("✅ Review & Create")
        dpg.add_text(" ")
        
        name = dpg.get_value("wizard_profile_name") or profile.get("name", "Unnamed")
        browser = dpg.get_value("wizard_browser_engine") or profile.get("browser_engine", "chromium")
        proxy = dpg.get_value("wizard_proxy") or profile.get("proxy", "None")
        headless = dpg.get_value("wizard_headless")
        
        dpg.add_text("Profile Summary")
        dpg.add_text(" ")
        
        dpg.add_text(f"Name: {name}", color=COLORS["text_secondary"])
        dpg.add_text(f"Browser: {browser}", color=COLORS["text_secondary"])
        dpg.add_text(f"Headless: {'Yes' if headless else 'No'}", color=COLORS["text_secondary"])
        dpg.add_text(f"Proxy: {proxy[:50]}..." if len(proxy) > 50 else f"Proxy: {proxy}", color=COLORS["text_secondary"])
        
        dpg.add_text(" ")
        dpg.add_text("✓ All settings configured", color=COLORS["success"])
    
    def _next_step(self):
        """Go to next wizard step."""
        if self.current_step < self.total_steps - 1:
            self._collect_step_data()
            self.current_step += 1
            dpg.close_window("profile_editor_modal")
            
            if self.mode == "create":
                self.show_create_modal()
            else:
                self.show_edit_modal(self.profile_data)
    
    def _prev_step(self):
        """Go to previous wizard step."""
        if self.current_step > 0:
            self.current_step -= 1
            dpg.close_window("profile_editor_modal")
            
            if self.mode == "create":
                self.show_create_modal()
            else:
                self.show_edit_modal(self.profile_data)
    
    def _go_to_step(self, step: int):
        """Go to specific wizard step."""
        if 0 <= step < self.total_steps:
            self._collect_step_data()
            self.current_step = step
            dpg.close_window("profile_editor_modal")
            
            if self.mode == "create":
                self.show_create_modal()
            else:
                self.show_edit_modal(self.profile_data)
    
    def _collect_step_data(self):
        """Collect data from current step."""
        step_id = self.steps[self.current_step]["id"]
        
        if step_id == "basic":
            self.profile_data["name"] = dpg.get_value("wizard_profile_name")
            self.profile_data["description"] = dpg.get_value("wizard_profile_description")
            self.profile_data["use_case"] = dpg.get_value("wizard_profile_use_case")
        elif step_id == "browser":
            self.profile_data["browser_engine"] = dpg.get_value("wizard_browser_engine")
            self.profile_data["user_agent"] = dpg.get_value("wizard_user_agent")
            self.profile_data["headless"] = dpg.get_value("wizard_headless")
        elif step_id == "proxy":
            self.profile_data["proxy"] = dpg.get_value("wizard_proxy")
            self.profile_data["proxy_username"] = dpg.get_value("wizard_proxy_username")
            self.profile_data["proxy_password"] = dpg.get_value("wizard_proxy_password")
        elif step_id == "advanced":
            self.profile_data["resolution"] = dpg.get_value("wizard_resolution")
            self.profile_data["timezone"] = dpg.get_value("wizard_timezone")
            self.profile_data["language"] = dpg.get_value("wizard_language")
            self.profile_data["stealth_canvas"] = dpg.get_value("wizard_stealth_canvas")
            self.profile_data["stealth_webrtc"] = dpg.get_value("wizard_stealth_webrtc")

    def _create_tab_sidebar(self):
        """Create tab sidebar."""
        with dpg.child_window(
            tag="editor_tabs_sidebar",
            width=180,
            height=480,
        ):
            dpg.add_text("Settings")
            dpg.add_separator()
            
            tabs = [
                (ProfileEditorTab.BASIC, "📋 Basic Info"),
                (ProfileEditorTab.BROWSER, "🌐 Browser"),
                (ProfileEditorTab.DISPLAY, "🖥 Display"),
                (ProfileEditorTab.NETWORK, "🔗 Network"),
                (ProfileEditorTab.SECURITY, "🔒 Security"),
                (ProfileEditorTab.ADVANCED, "⚡ Advanced"),
            ]
            
            for tab_id, tab_label in tabs:
                is_active = self.current_tab == tab_id
                
                if is_active:
                    dpg.add_button(
                        label=tab_label,
                        callback=lambda t=tab_id: self._switch_tab(t),
                        width=-1,
                    )
                else:
                    dpg.add_button(
                        label=tab_label,
                        callback=lambda t=tab_id: self._switch_tab(t),
                        width=-1,
                    )
    
    def _create_tab_content(self, profile: dict):
        """Create content for current tab."""
        with dpg.child_window(
            tag="editor_tab_content",
            width=480,
            height=480,
        ):
            if self.current_tab == ProfileEditorTab.BASIC:
                self._render_basic_tab(profile)
            elif self.current_tab == ProfileEditorTab.BROWSER:
                self._render_browser_tab(profile)
            elif self.current_tab == ProfileEditorTab.DISPLAY:
                self._render_display_tab(profile)
            elif self.current_tab == ProfileEditorTab.NETWORK:
                self._render_network_tab(profile)
            elif self.current_tab == ProfileEditorTab.SECURITY:
                self._render_security_tab(profile)
            elif self.current_tab == ProfileEditorTab.ADVANCED:
                self._render_advanced_tab(profile)
    
    def _render_basic_tab(self, profile: dict):
        """Render Basic Info tab."""
        dpg.add_text("Basic Information")
        dpg.add_text(" ")
        
        dpg.add_text("Profile Name *", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_name",
            default_value=profile.get("name", ""),
            width=400,
            hint="Enter profile name",
        )
        dpg.add_text(" ")
        
        dpg.add_text("Description", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_description",
            default_value=profile.get("description", ""),
            width=400,
            height=60,
            hint="Optional description",
            multiline=True,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Use Case", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_use_case",
            items=["general", "social_media", "automation", "scraping", "testing"],
            default_value=profile.get("use_case", "general"),
            width=200,
        )
    
    def _render_browser_tab(self, profile: dict):
        """Render Browser tab."""
        dpg.add_text("Browser Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Browser Engine", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_browser_engine",
            items=["chromium", "firefox", "webkit"],
            default_value=profile.get("browser_engine", "chromium"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("User Agent", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_user_agent",
            default_value=profile.get("user_agent", ""),
            width=400,
            height=40,
            hint="Leave empty for auto-generated",
            multiline=True,
        )
        dpg.add_text(" ")
        
        dpg.add_checkbox(
            tag="profile_headless",
            label="Run in Headless Mode",
            default_value=profile.get("headless", True),
        )
    
    def _render_display_tab(self, profile: dict):
        """Render Display tab."""
        dpg.add_text("Display Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Resolution", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_resolution",
            items=["1920x1080", "1366x768", "1280x720", "2560x1440", "3840x2160", "Random"],
            default_value=profile.get("resolution", "1920x1080"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Timezone", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_timezone",
            items=[
                "America/New_York",
                "America/Los_Angeles",
                "America/Chicago",
                "Europe/London",
                "Europe/Paris",
                "Asia/Tokyo",
                "Asia/Shanghai",
                "Australia/Sydney",
                "System",
            ],
            default_value=profile.get("timezone", "System"),
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Language", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_language",
            items=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "zh-CN", "ja-JP", "System"],
            default_value=profile.get("language", "en-US"),
            width=200,
        )
    
    def _render_network_tab(self, profile: dict):
        """Render Network tab (Proxy)."""
        dpg.add_text("Network Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Proxy", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_proxy",
            default_value=profile.get("proxy", ""),
            width=400,
            hint="http://proxy:port or socks5://proxy:port",
        )
        dpg.add_text(" ")
        
        dpg.add_text("Proxy Type", color=COLORS["text_secondary"])
        dpg.add_combo(
            tag="profile_proxy_type",
            items=["http", "https", "socks5"],
            default_value="http",
            width=200,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Proxy Username", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_proxy_username",
            default_value=profile.get("proxy_username", ""),
            width=300,
        )
        dpg.add_text(" ")
        
        dpg.add_text("Proxy Password", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_proxy_password",
            default_value=profile.get("proxy_password", ""),
            width=300,
            password=True,
        )
    
    def _render_security_tab(self, profile: dict):
        """Render Security tab."""
        dpg.add_text("Security & Stealth Settings")
        dpg.add_text(" ")
        
        dpg.add_text("Fingerprint Protection", color=COLORS["text_secondary"])
        
        dpg.add_checkbox(
            tag="profile_stealth_canvas",
            label="Canvas Fingerprint Protection",
            default_value=profile.get("stealth_canvas", True),
        )
        
        dpg.add_checkbox(
            tag="profile_stealth_webgl",
            label="WebGL Fingerprint Protection",
            default_value=profile.get("stealth_webgl", True),
        )
        
        dpg.add_checkbox(
            tag="profile_stealth_webrtc",
            label="WebRTC Protection (Prevent IP Leak)",
            default_value=profile.get("stealth_webrtc", True),
        )
        
        dpg.add_checkbox(
            tag="profile_stealth_audio",
            label="Audio Fingerprint Protection",
            default_value=profile.get("stealth_audio", True),
        )
        
        dpg.add_checkbox(
            tag="profile_stealth_fonts",
            label="Font Fingerprint Protection",
            default_value=profile.get("stealth_fonts", True),
        )
        
        dpg.add_text(" ")
        
        dpg.add_checkbox(
            tag="profile_hide_webdriver",
            label="Hide navigator.webdriver",
            default_value=profile.get("hide_webdriver", True),
        )
        
        dpg.add_checkbox(
            tag="profile_randomize_screen",
            label="Randomize Screen Properties",
            default_value=profile.get("randomize_screen", False),
        )
    
    def _render_advanced_tab(self, profile: dict):
        """Render Advanced tab."""
        dpg.add_text("Advanced Settings")
        dpg.add_text(" ")
        
        dpg.add_checkbox(
            tag="profile_hardware_acceleration",
            label="Enable Hardware Acceleration",
            default_value=profile.get("hardware_acceleration", True),
        )
        
        dpg.add_checkbox(
            tag="profile_auto_update",
            label="Auto Update Browser",
            default_value=profile.get("auto_update", True),
        )
        
        dpg.add_text(" ")
        
        dpg.add_text("Custom Launch Arguments", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_custom_args",
            default_value=profile.get("custom_args", ""),
            width=400,
            height=60,
            hint="--arg1 --arg2=value",
            multiline=True,
        )
        
        dpg.add_text(" ")
        
        dpg.add_text("Custom JavaScript", color=COLORS["text_secondary"])
        dpg.add_input_text(
            tag="profile_custom_js",
            default_value=profile.get("custom_js", ""),
            width=400,
            height=60,
            hint="// Custom JavaScript to inject",
            multiline=True,
        )
    
    def _switch_tab(self, tab_id: str):
        """Switch to a different tab."""
        self.current_tab = tab_id
        dpg.close_window("profile_editor_modal")
        
        if self.mode == "create":
            self.show_create_modal()
        else:
            self.show_edit_modal(self.profile_data)
    
    def _save_profile(self, profile_id: int = None):
        """Save profile data."""
        name = dpg.get_value("profile_name")
        
        if not name:
            print("Profile name is required!")
            return
        
        profile_data = {
            "name": name,
            "description": dpg.get_value("profile_description"),
            "use_case": dpg.get_value("profile_use_case"),
            "browser_engine": dpg.get_value("profile_browser_engine"),
            "user_agent": dpg.get_value("profile_user_agent") or None,
            "headless": dpg.get_value("profile_headless"),
            "resolution": dpg.get_value("profile_resolution"),
            "timezone": dpg.get_value("profile_timezone"),
            "language": dpg.get_value("profile_language"),
            "proxy": dpg.get_value("profile_proxy") or None,
            "proxy_username": dpg.get_value("profile_proxy_username") or None,
            "proxy_password": dpg.get_value("profile_proxy_password") or None,
            "stealth_canvas": dpg.get_value("profile_stealth_canvas"),
            "stealth_webgl": dpg.get_value("profile_stealth_webgl"),
            "stealth_webrtc": dpg.get_value("profile_stealth_webrtc"),
            "stealth_audio": dpg.get_value("profile_stealth_audio"),
            "stealth_fonts": dpg.get_value("profile_stealth_fonts"),
            "hide_webdriver": dpg.get_value("profile_hide_webdriver"),
            "randomize_screen": dpg.get_value("profile_randomize_screen"),
            "hardware_acceleration": dpg.get_value("profile_hardware_acceleration"),
            "auto_update": dpg.get_value("profile_auto_update"),
            "custom_args": dpg.get_value("profile_custom_args") or None,
            "custom_js": dpg.get_value("profile_custom_js") or None,
        }
        
        try:
            if profile_id:
                self.app.api_client.update_profile(profile_id, profile_data)
                print(f"Profile {profile_id} updated!")
            else:
                self.app.api_client.create_profile(profile_data)
                print("Profile created!")
            
            dpg.close_modal("profile_editor_modal")
            
            if hasattr(self.app, 'pages') and 'profiles' in self.app.pages:
                self.app.pages['profiles'].refresh()
                
        except Exception as e:
            print(f"Error saving profile: {e}")


def show_profile_editor(app, profile: dict = None, mode: str = "create"):
    """Helper function to show profile editor."""
    editor = ProfileEditor(app, mode)
    if profile:
        editor.show_edit_modal(profile)
    else:
        editor.show_create_modal()
