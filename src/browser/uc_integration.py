"""
Undetected ChromeDriver integration module.
Provides advanced anti-detection for Chrome using undetected-chromedriver.
"""

import logging
import platform
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class UCBrowserEngine(Enum):
    """Browser engines supported by undetected-chromedriver."""
    CHROMIUM = "chromium"
    EDGE = "edge"


@dataclass
class UCProfileConfig:
    """Configuration for undetected-chromedriver browser profile."""

    name: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    headless: bool = False
    window_size: str = "1920,1080"
    timezone: Optional[str] = None
    language: str = "en-US"
    platform_name: str = "Win32"
    browser_engine: UCBrowserEngine = UCBrowserEngine.CHROMIUM
    page_load_timeout: int = 30
    undetected_mode: bool = True
    patch_version: bool = True
    anti_cdp: bool = True


class UndetectedChromeDriverManager:
    """Manages undetected-chromedriver browser instances."""

    def __init__(self, max_sessions: int = 10):
        self.sessions: Dict[str, Any] = {}
        self._max_sessions = max_sessions
        self._uc_available = None

    def _check_uc_available(self) -> bool:
        """Check if undetected-chromedriver is available."""
        if self._uc_available is None:
            try:
                import undetected_chromedriver as uc
                self._uc_available = True
            except ImportError:
                self._uc_available = False
                logger.warning(
                    "undetected-chromedriver not installed. "
                    "Install with: pip install undetected-chromedriver"
                )
        return self._uc_available

    def _build_chrome_options(self, config: UCProfileConfig) -> List[str]:
        """Build Chrome arguments."""
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-popup-blocking",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
            "--disable-web-security",
            "--window-size=" + config.window_size,
            "--start-maximized",
        ]

        if config.user_agent:
            args.append(f"--user-agent={config.user_agent}")

        if config.proxy:
            proxy_str = config.proxy
            if config.proxy_username and config.proxy_password:
                proxy_str = f"{config.proxy_username}:{config.proxy_password}@{config.proxy}"
            args.append(f"--proxy-server={proxy_str}")

        args.append(f"--lang={config.language}")

        if config.timezone:
            args.append(f"--time-zone={config.timezone}")

        return args

    def create_driver(self, config: UCProfileConfig):
        """Create a new undetected-chromedriver instance."""
        if not self._check_uc_available():
            raise ImportError(
                "undetected-chromedriver is not installed. "
                "Install with: pip install undetected-chromedriver"
            )

        if len(self.sessions) >= self._max_sessions:
            raise RuntimeError(f"Maximum sessions ({self._max_sessions}) reached")

        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.service import Service

        try:
            options = uc.ChromeOptions()
            
            args = self._build_chrome_options(config)
            for arg in args:
                options.add_argument(arg)

            options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            options.add_experimental_option("useAutomationExtension", False)

            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }
            options.add_experimental_option("prefs", prefs)

            driver = uc.Chrome(
                options=options,
                headless=config.headless,
                patcher_force_close=True if config.patch_version else False,
                use_subprocess=True,
            )

            driver.set_page_load_timeout(config.page_load_timeout)

            if config.undetected_mode:
                self._apply_undetected_patches(driver, config)

            session_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session_info = {
                "session_id": session_id,
                "profile_name": config.name,
                "started_at": datetime.now(),
                "driver": driver,
                "config": config,
                "status": "active",
            }

            self.sessions[session_id] = session_info
            logger.info(f"Created undetected-chromedriver session: {session_id}")
            return session_info

        except Exception as e:
            logger.error(f"Failed to create undetected-chromedriver: {e}")
            raise

    def _apply_undetected_patches(self, driver: Any, config: UCProfileConfig):
        """Apply additional undetected patches."""
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })

            if config.anti_cdp:
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        window.navigator.chrome = true;
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['en-US', 'en']
                        });
                    """
                })

        except Exception as e:
            logger.warning(f"Failed to apply undetected patches: {e}")

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[Dict]:
        """List all active sessions."""
        return list(self.sessions.values())

    def navigate(self, session_id: str, url: str) -> bool:
        """Navigate to URL."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            session["driver"].get(url)
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise

    def click(self, session_id: str, selector: str) -> bool:
        """Click an element."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            element = WebDriverWait(session["driver"], 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return True
        except Exception as e:
            logger.error(f"Click error: {e}")
            raise

    def type_text(self, session_id: str, selector: str, text: str) -> bool:
        """Type text into an element."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            element = WebDriverWait(session["driver"], 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            logger.error(f"Type error: {e}")
            raise

    def screenshot(self, session_id: str, path: str = "screenshot.png") -> bool:
        """Take a screenshot."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            session["driver"].save_screenshot(path)
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise

    def execute_script(self, session_id: str, script: str) -> Any:
        """Execute JavaScript."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session["driver"].execute_script(script)

    def get_page_source(self, session_id: str) -> str:
        """Get page source HTML."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session["driver"].page_source

    def get_title(self, session_id: str) -> str:
        """Get page title."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session["driver"].title

    def get_current_url(self, session_id: str) -> str:
        """Get current URL."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session["driver"].current_url

    def close_session(self, session_id: str) -> bool:
        """Close a session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            session["driver"].quit()
            session["status"] = "closed"
            del self.sessions[session_id]
            logger.info(f"Closed session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            return False

    def close_all(self):
        """Close all sessions."""
        for session_id in list(self.sessions.keys()):
            self.close_session(session_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()


def create_uc_session(config: UCProfileConfig) -> UndetectedChromeDriverManager:
    """Create a new undetected-chromedriver session."""
    manager = UndetectedChromeDriverManager()
    manager.create_driver(config)
    return manager
