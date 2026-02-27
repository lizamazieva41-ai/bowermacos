"""
Bower Antidetect Browser - Python GUI Application
Main entry point using DearPyGui - With full navigation and API integration
"""

import dearpygui.dearpygui as dpg
from src.gui.styles.theme import setup_theme, COLORS

current_page = "dashboard"
api_client = None


def get_api_client():
    """Get or create API client."""
    global api_client
    if api_client is None:
        from src.gui.utils.api_client import GUIClient
        api_client = GUIClient(base_url="http://localhost:8000")
    return api_client


def refresh_dashboard():
    """Refresh dashboard with API data."""
    client = get_api_client()
    try:
        # Get stats
        stats = client.get("/api/v1/stats")
        dpg.set_value("stat_sessions", f"Active Sessions: {stats.get('sessions', 0)}")
        dpg.set_value("stat_profiles", f"Profiles: {stats.get('profiles', 0)}")
        dpg.set_value("stat_proxies", f"Proxies: {stats.get('proxies', 0)}")
    except Exception as e:
        print(f"Failed to refresh stats: {e}")


def show_dashboard():
    """Show dashboard page."""
    global current_page
    current_page = "dashboard"
    dpg.delete_item("main_content", children_only=True)
    
    with dpg.group(parent="main_content"):
        dpg.add_text("Dashboard", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_text("Overview and statistics", color=COLORS.get("text_secondary", (148, 163, 184)))
        dpg.add_text(" ")
        
        # Stats cards
        with dpg.group(horizontal=True):
            dpg.add_button(label="Active Sessions: 0", tag="stat_sessions", width=150, callback=refresh_dashboard)
            dpg.add_button(label="Profiles: 0", tag="stat_profiles", width=150, callback=refresh_dashboard)
            dpg.add_button(label="Proxies: 0", tag="stat_proxies", width=150, callback=refresh_dashboard)
        
        dpg.add_text(" ")
        dpg.add_button(label="Refresh Stats", callback=refresh_dashboard)


def create_profile_dialog():
    """Show create profile dialog."""
    # Delete old dialog if exists
    if dpg.does_item_exist("create_profile_dialog"):
        dpg.delete_item("create_profile_dialog")
    
    with dpg.window(
        tag="create_profile_dialog",
        label="Create New Profile",
        width=450,
        height=500,
        pos=(500, 150),
    ):
        dpg.add_input_text(label="Profile Name", tag="new_profile_name", width=350)
        dpg.add_text(" ")
        
        # Browser Engine
        dpg.add_text("Browser Engine:", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_combo(
            tag="new_profile_browser_engine",
            items=["chromium", "firefox", "webkit"],
            default_value="chromium",
            width=350,
        )
        dpg.add_text(" ")
        
        # Resolution
        dpg.add_text("Resolution:", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_combo(
            tag="new_profile_resolution",
            items=["1920x1080", "1366x768", "1536x864", "1440x900", "2560x1440", "1280x720"],
            default_value="1920x1080",
            width=350,
        )
        dpg.add_text(" ")
        
        # Timezone
        dpg.add_text("Timezone:", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_combo(
            tag="new_profile_timezone",
            items=["UTC", "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore"],
            default_value="UTC",
            width=350,
        )
        dpg.add_text(" ")
        
        # Language
        dpg.add_text("Language:", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_combo(
            tag="new_profile_language",
            items=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "ja-JP", "ko-KR", "zh-CN"],
            default_value="en-US",
            width=350,
        )
        dpg.add_text(" ")
        
        # Headless
        dpg.add_checkbox(tag="new_profile_headless", label="Headless Mode", default_value=True)
        dpg.add_text(" ")
        
        # User Agent (optional)
        dpg.add_text("Custom User Agent (optional):", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_input_text(tag="new_profile_ua", width=350, hint="Auto-generate if empty")
        dpg.add_text(" ")
        
        # Proxy (optional)
        dpg.add_text("Proxy (optional):", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_input_text(tag="new_profile_proxy", width=350, hint="http://proxy:port")
        dpg.add_text(" ")
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Create Profile", callback=do_create_profile)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("create_profile_dialog"))


def do_create_profile():
    """Actually create the profile."""
    name = dpg.get_value("new_profile_name")
    if not name:
        print("Please enter a profile name")
        return
    
    browser_engine = dpg.get_value("new_profile_browser_engine")
    resolution = dpg.get_value("new_profile_resolution")
    timezone = dpg.get_value("new_profile_timezone")
    language = dpg.get_value("new_profile_language")
    headless = dpg.get_value("new_profile_headless")
    ua = dpg.get_value("new_profile_ua")
    proxy = dpg.get_value("new_profile_proxy")
    
    client = get_api_client()
    try:
        profile_data = {
            "name": name,
            "browser_engine": browser_engine,
            "resolution": resolution,
            "timezone": timezone,
            "language": language,
            "headless": headless,
        }
        
        if ua:
            profile_data["user_agent"] = ua
        if proxy:
            profile_data["proxy"] = proxy
        
        result = client.post("/api/v1/profiles", profile_data)
        dpg.delete_item("create_profile_dialog")
        show_profiles()  # Refresh
        print(f"Profile '{name}' created successfully!")
    except Exception as e:
        print(f"Failed to create profile: {e}")


def show_profiles():
    """Show profiles page."""
    global current_page
    current_page = "profiles"
    dpg.delete_item("main_content", children_only=True)
    
    with dpg.group(parent="main_content"):
        dpg.add_text("Profiles", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_text("Manage browser profiles", color=COLORS.get("text_secondary", (148, 163, 184)))
        dpg.add_text(" ")
        
        # Load profiles from API
        client = get_api_client()
        try:
            profiles = client.get("/api/v1/profiles")
            profile_list = profiles.get("profiles", [])
            
            if profile_list:
                dpg.add_text(f"Total: {len(profile_list)} profiles", color=COLORS.get("text_secondary", (148, 163, 184)))
                dpg.add_text(" ")
                
                for p in profile_list:
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"• {p.get('name', 'Unnamed')}", color=COLORS.get("text", (226, 232, 240)))
            else:
                dpg.add_text("No profiles yet. Create one to get started.", color=COLORS.get("text_muted", (100, 116, 139)))
        except Exception as e:
            dpg.add_text(f"No profiles (API: {str(e)[:50]})", color=COLORS.get("text_muted", (100, 116, 139)))
        
        dpg.add_text(" ")
        dpg.add_button(label="+ Create Profile", callback=create_profile_dialog)


def add_proxy_dialog():
    """Show add proxy dialog."""
    with dpg.window(
        tag="add_proxy_dialog",
        label="Add Proxy",
        width=400,
        height=250,
        pos=(500, 200),
    ):
        dpg.add_input_text(label="Proxy URL", tag="new_proxy_url", width=300, hint="http://proxy:port")
        dpg.add_text(" ")
        dpg.add_input_text(label="Username (optional)", tag="new_proxy_user", width=300)
        dpg.add_text(" ")
        dpg.add_input_text(label="Password (optional)", tag="new_proxy_pass", width=300, password=True)
        dpg.add_text(" ")
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Add", callback=do_add_proxy)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("add_proxy_dialog"))


def do_add_proxy():
    """Actually add the proxy."""
    url = dpg.get_value("new_proxy_url")
    if not url:
        return
    
    username = dpg.get_value("new_proxy_user")
    password = dpg.get_value("new_proxy_pass")
    
    client = get_api_client()
    try:
        proxy_data = {
            "url": url,
            "username": username if username else None,
            "password": password if password else None,
        }
        client.post("/api/v1/proxies", proxy_data)
        dpg.delete_item("add_proxy_dialog")
        show_proxies()
    except Exception as e:
        print(f"Failed to add proxy: {e}")


def show_proxies():
    """Show proxies page."""
    global current_page
    current_page = "proxies"
    dpg.delete_item("main_content", children_only=True)
    
    with dpg.group(parent="main_content"):
        dpg.add_text("Proxies", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_text("Manage proxy servers", color=COLORS.get("text_secondary", (148, 163, 184)))
        dpg.add_text(" ")
        
        client = get_api_client()
        try:
            proxies = client.get("/api/v1/proxies")
            proxy_list = proxies.get("proxies", [])
            
            if proxy_list:
                dpg.add_text(f"Total: {len(proxy_list)} proxies", color=COLORS.get("text_secondary", (148, 163, 184)))
                dpg.add_text(" ")
                
                for p in proxy_list:
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"• {p.get('url', 'Unknown')}", color=COLORS.get("text", (226, 232, 240)))
            else:
                dpg.add_text("No proxies configured.", color=COLORS.get("text_muted", (100, 116, 139)))
        except Exception as e:
            dpg.add_text(f"No proxies (API: {str(e)[:50]})", color=COLORS.get("text_muted", (100, 116, 139)))
        
        dpg.add_text(" ")
        dpg.add_button(label="+ Add Proxy", callback=add_proxy_dialog)


def show_sessions():
    """Show sessions page."""
    global current_page
    current_page = "sessions"
    dpg.delete_item("main_content", children_only=True)
    
    with dpg.group(parent="main_content"):
        dpg.add_text("Sessions", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_text("Monitor active browser sessions", color=COLORS.get("text_secondary", (148, 163, 184)))
        dpg.add_text(" ")
        
        client = get_api_client()
        try:
            sessions = client.get("/api/v1/sessions")
            session_list = sessions.get("sessions", [])
            
            if session_list:
                dpg.add_text(f"Active: {len(session_list)} sessions", color=COLORS.get("text_secondary", (148, 163, 184)))
            else:
                dpg.add_text("No active sessions.", color=COLORS.get("text_muted", (100, 116, 139)))
        except Exception as e:
            dpg.add_text(f"No sessions (API: {str(e)[:50]})", color=COLORS.get("text_muted", (100, 116, 139)))


def show_settings():
    """Show settings page."""
    global current_page
    current_page = "settings"
    dpg.delete_item("main_content", children_only=True)
    
    with dpg.group(parent="main_content"):
        dpg.add_text("Settings", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_text("Application configuration", color=COLORS.get("text_secondary", (148, 163, 184)))
        dpg.add_text(" ")
        
        dpg.add_text("API Configuration:", color=COLORS.get("text", (226, 232, 240)))
        dpg.add_input_text(label="API URL", tag="api_url", default_value="http://localhost:8000", width=300)
        dpg.add_text(" ")
        
        dpg.add_button(label="Save Settings", callback=lambda: dpg.add_text("Settings saved!", color=COLORS.get("success", (34, 197, 94))))


def check_api_connection(retries=10, delay=1):
    """Check API connection with retries."""
    import time
    for i in range(retries):
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:8000/health")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    return True
        except:
            pass
        if i < retries - 1:
            time.sleep(delay)
    return False


def main():
    dpg.create_context()
    dpg.create_viewport(
        title="Bower Antidetect Browser",
        width=1400,
        height=900,
        min_width=1024,
        min_height=700,
        resizable=True,
    )

    try:
        setup_theme()
    except Exception as e:
        print(f"Theme setup warning: {e}")

    api_connected = check_api_connection()
    print(f"API Connected: {api_connected}")

    with dpg.window(
        tag="main_window",
        label="Bower Antidetect Browser",
        width=dpg.get_viewport_width(),
        height=dpg.get_viewport_height(),
        no_title_bar=True,
        no_resize=True,
        no_move=True,
    ):
        with dpg.group(horizontal=True):
            with dpg.child_window(tag="sidebar", width=220, border=False):
                dpg.add_text("Bower", color=COLORS.get("primary", (59, 130, 246)))
                dpg.add_text("Antidetect Browser", color=COLORS.get("text_secondary", (148, 163, 184)))
                dpg.add_separator()
                dpg.add_text(" ")

                # Navigation buttons with callbacks
                dpg.add_button(label="Dashboard", width=190, callback=show_dashboard)
                dpg.add_button(label="Profiles", width=190, callback=show_profiles)
                dpg.add_button(label="Sessions", width=190, callback=show_sessions)
                dpg.add_button(label="Proxies", width=190, callback=show_proxies)
                dpg.add_button(label="Settings", width=190, callback=show_settings)

                dpg.add_text(" ")
                dpg.add_text("API Status:", color=COLORS.get("text_secondary", (148, 163, 184)))
                dpg.add_text("Connected" if api_connected else "Disconnected", 
                           color=COLORS.get("success", (34, 197, 94)) if api_connected else COLORS.get("danger", (239, 68, 68)))

            with dpg.child_window(tag="main_content", width=-1, border=False):
                pass

    dpg.set_viewport_vsync(True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    # Show initial page
    show_dashboard()

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == "__main__":
    main()
