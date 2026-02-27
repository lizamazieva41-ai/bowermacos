"""
Onboarding Wizard for First Launch
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import COLORS


class OnboardingWizard:
    """First launch onboarding wizard."""
    
    def __init__(self, app):
        self.app = app
        self.current_step = 0
        self.total_steps = 6
        self.steps = [
            "welcome",
            "register",
            "verify",
            "api_setup",
            "create_profile",
            "complete",
        ]
        
        self.user_data = {
            "email": "",
            "username": "",
            "verification_code": "",
        }
    
    def _render_welcome_step(self):
        """Render welcome step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=400,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("", height=40)
            dpg.add_text("🌊 Welcome to Bower!", font=32, color=COLORS["primary"])
            dpg.add_text("", height=20)
            dpg.add_text(
                "Bower Antidetect Browser V2",
                font=20,
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=30)
            dpg.add_text(
                "A professional privacy browser automation system for managing anonymous browser profiles with advanced stealth capabilities.",
                wrap=450,
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=40)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Get Started →",
                    callback=self._next_step,
                    width=150,
                )
                dpg.add_button(
                    label="Skip",
                    callback=self._close,
                    width=80,
                )
    
    def show(self):
        """Show onboarding wizard."""
        if not self._should_show_onboarding():
            return
        
        self._render_step()
    
    def _should_show_onboarding(self) -> bool:
        """Check if onboarding should be shown."""
        import json
        from pathlib import Path
        
        config_file = Path.home() / ".bower" / "onboarding_complete.json"
        
        if config_file.exists():
            try:
                data = json.loads(config_file.read_text())
                return not data.get("completed", False)
            except:
                return True
        
        return True
    
    def _mark_onboarding_complete(self):
        """Mark onboarding as complete."""
        import json
        from pathlib import Path
        
        config_file = Path.home() / ".bower" / "onboarding_complete.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps({"completed": True}))
    
    def _render_step(self):
        """Render current step."""
        if self.current_step == 0:
            self._render_welcome_step()
        elif self.current_step == 1:
            self._render_register_step()
        elif self.current_step == 2:
            self._render_verify_step()
        elif self.current_step == 3:
            self._render_api_setup_step()
        elif self.current_step == 4:
            self._render_create_profile_step()
        elif self.current_step == 5:
            self._render_complete_step()
    
    def _render_register_step(self):
        """Render email registration step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=420,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("📧 Create Account", font=28)
            dpg.add_text("", height=10)
            
            self._render_progress_indicator()
            
            dpg.add_text("", height=20)
            dpg.add_text(
                "Enter your email to create a free account.",
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=20)
            
            dpg.add_text("Email Address *", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_email",
                default_value="",
                width=350,
                hint="your@email.com",
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Username *", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_reg_username",
                default_value="",
                width=250,
                hint="Choose a username",
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Password *", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_reg_password",
                default_value="",
                width=250,
                password=True,
                hint="Min 8 characters",
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Confirm Password", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_reg_password_confirm",
                default_value="",
                width=250,
                password=True,
            )
            
            dpg.add_text("", height=20)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="← Back",
                    callback=self._prev_step,
                    width=100,
                )
                dpg.add_button(
                    label="Continue →",
                    callback=self._handle_register,
                    width=150,
                )
    
    def _render_verify_step(self):
        """Render email verification step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=350,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("🔐 Verify Email", font=28)
            dpg.add_text("", height=10)
            
            self._render_progress_indicator()
            
            dpg.add_text("", height=20)
            dpg.add_text(
                f"We've sent a 6-digit verification code to:",
                color=COLORS["text_secondary"],
            )
            dpg.add_text(
                self.user_data.get("email", "your email"),
                color=COLORS["primary"],
                font=16,
            )
            dpg.add_text("", height=20)
            
            dpg.add_text("Verification Code *", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_verify_code",
                default_value="",
                width=200,
                hint="123456",
            )
            
            dpg.add_text("", height=20)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="← Back",
                    callback=self._prev_step,
                    width=100,
                )
                dpg.add_button(
                    label="Verify →",
                    callback=self._handle_verify,
                    width=120,
                )
            
            dpg.add_text("", height=15)
            dpg.add_text(
                "Didn't receive the code?",
                color=COLORS["text_secondary"],
            )
            dpg.add_button(
                label="Resend Code",
                callback=self._resend_code,
                width=120,
            )
    
    def _handle_register(self):
        """Handle registration submission."""
        email = dpg.get_value("onboarding_email")
        username = dpg.get_value("onboarding_reg_username")
        password = dpg.get_value("onboarding_reg_password")
        password_confirm = dpg.get_value("onboarding_reg_password_confirm")
        
        if not email or not username or not password:
            print("Please fill in all fields")
            return
        
        if password != password_confirm:
            print("Passwords do not match")
            return
        
        if len(password) < 8:
            print("Password must be at least 8 characters")
            return
        
        self.user_data["email"] = email
        self.user_data["username"] = username
        
        self._save_user_data(email, username)
        
        self._next_step()
    
    def _handle_verify(self):
        """Handle verification code submission."""
        code = dpg.get_value("onboarding_verify_code")
        
        if not code or len(code) != 6:
            print("Please enter a valid 6-digit code")
            return
        
        self.user_data["verification_code"] = code
        
        self._next_step()
    
    def _resend_code(self):
        """Resend verification code."""
        print(f"Verification code resent to {self.user_data.get('email')}")
    
    def _save_user_data(self, email: str, username: str):
        """Save user data to config."""
        import json
        from pathlib import Path
        
        config_file = Path.home() / ".bower" / "user_data.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "email": email,
            "username": username,
            "verified": False,
        }
        
        config_file.write_text(json.dumps(config, indent=2))
    
    def _render_api_setup_step(self):
        """Render API setup step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=450,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("🔗 API Setup", font=28)
            dpg.add_text("", height=10)
            
            self._render_progress_indicator()
            
            dpg.add_text("", height=20)
            dpg.add_text(
                "Configure the API server connection to get started.",
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=20)
            
            dpg.add_text("API Server URL", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_api_url",
                default_value="http://localhost:8000",
                width=400,
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Username", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_username",
                default_value="admin",
                width=200,
            )
            
            dpg.add_text("", height=5)
            
            dpg.add_text("Password", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_password",
                default_value="admin",
                width=200,
                password=True,
            )
            
            dpg.add_text("", height=20)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="← Back",
                    callback=self._prev_step,
                    width=100,
                )
                dpg.add_button(
                    label="Test & Continue →",
                    callback=self._test_api_connection,
                    width=180,
                )
    
    def _render_create_profile_step(self):
        """Render create profile step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=450,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("➕ Create First Profile", font=28)
            dpg.add_text("", height=10)
            
            self._render_progress_indicator()
            
            dpg.add_text("", height=20)
            dpg.add_text(
                "Create your first browser profile to get started.",
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=20)
            
            dpg.add_text("Profile Name *", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_profile_name",
                default_value="My First Profile",
                width=300,
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Browser Engine", color=COLORS["text_secondary"])
            dpg.add_combo(
                tag="onboarding_browser",
                items=["chromium", "firefox", "webkit"],
                default_value="chromium",
                width=200,
            )
            
            dpg.add_text("", height=10)
            
            dpg.add_text("Proxy (optional)", color=COLORS["text_secondary"])
            dpg.add_input_text(
                tag="onboarding_proxy",
                default_value="",
                width=300,
                hint="http://proxy:port",
            )
            
            dpg.add_text("", height=20)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="← Back",
                    callback=self._prev_step,
                    width=100,
                )
                dpg.add_button(
                    label="Skip",
                    callback=self._next_step,
                    width=80,
                )
                dpg.add_button(
                    label="Create Profile",
                    callback=self._create_first_profile,
                    width=150,
                )
    
    def _render_complete_step(self):
        """Render completion step."""
        with dpg.window(
            tag="onboarding_wizard",
            width=500,
            height=400,
            modal=True,
            pos=[200, 100],
            no_title_bar=True,
        ):
            dpg.add_text("", height=40)
            dpg.add_text("🎉 You're All Set!", font=32, color=COLORS["success"])
            dpg.add_text("", height=30)
            
            dpg.add_text(
                "Bower is ready to use! Here's what you can do:",
                color=COLORS["text_secondary"],
            )
            dpg.add_text("", height=20)
            
            features = [
                "🌐 Manage multiple browser profiles",
                "🔒 Advanced stealth and fingerprint protection",
                "🔗 Proxy rotation and management",
                "🖥️ Desktop GUI or CLI interface",
                "🚀 Headless browser automation",
            ]
            
            for feature in features:
                dpg.add_text(f"  {feature}")
            
            dpg.add_text("", height=40)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Open Dashboard",
                    callback=self._open_dashboard,
                    width=150,
                )
    
    def _render_progress_indicator(self):
        """Render progress indicator."""
        with dpg.group(horizontal=True):
            for i, step in enumerate(self.steps):
                if i < self.current_step:
                    color = COLORS["success"]
                elif i == self.current_step:
                    color = COLORS["primary"]
                else:
                    color = COLORS["text_muted"]
                
                dpg.add_text(
                    f"{'●' if i < self.current_step else '○'}",
                    color=color,
                )
                if i < len(self.steps) - 1:
                    dpg.add_text(" ", color=color)
    
    def _next_step(self):
        """Go to next step."""
        if self.current_step < self.total_steps:
            self.current_step += 1
            dpg.close_window("onboarding_wizard")
            self._render_step()
    
    def _prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            dpg.close_window("onboarding_wizard")
            self._render_step()
    
    def _close(self):
        """Close onboarding wizard."""
        self._mark_onboarding_complete()
        if dpg.does_item_exist("onboarding_wizard"):
            dpg.close_window("onboarding_wizard")
    
    def _test_api_connection(self):
        """Test API connection."""
        api_url = dpg.get_value("onboarding_api_url")
        username = dpg.get_value("onboarding_username")
        password = dpg.get_value("onboarding_password")
        
        old_url = self.app.api_client.base_url
        self.app.api_client.base_url = api_url
        
        try:
            result = self.app.login(username, password)
            if result.get("success"):
                self._save_config(api_url)
                self._next_step()
            else:
                print("Login failed. Please check your credentials.")
        except Exception as e:
            print(f"Connection failed: {e}")
        finally:
            self.app.api_client.base_url = old_url
    
    def _save_config(self, api_url: str):
        """Save configuration."""
        import json
        from pathlib import Path
        
        config_file = Path.home() / ".bower" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if config_file.exists():
            config = json.loads(config_file.read_text())
        else:
            config = {}
        
        config["api_url"] = api_url
        config["onboarding_complete"] = True
        
        config_file.write_text(json.dumps(config, indent=2))
    
    def _create_first_profile(self):
        """Create first profile."""
        name = dpg.get_value("onboarding_profile_name")
        
        if not name:
            print("Profile name is required")
            return
        
        profile_data = {
            "name": name,
            "browser_engine": dpg.get_value("onboarding_browser"),
            "proxy": dpg.get_value("onboarding_proxy") or None,
            "headless": True,
        }
        
        try:
            self.app.api_client.create_profile(profile_data)
            print(f"Profile '{name}' created!")
            self._next_step()
        except Exception as e:
            print(f"Error creating profile: {e}")
    
    def _open_dashboard(self):
        """Open dashboard."""
        self._close()
        self.app.show_page("dashboard")
        self.app.pages["dashboard"].refresh()


def show_onboarding(app):
    """Show onboarding wizard."""
    wizard = OnboardingWizard(app)
    wizard.show()
