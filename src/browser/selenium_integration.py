"""
Selenium WebDriver integration module.
Provides stealth capabilities for Selenium-based browser automation.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BrowserEngine(Enum):
    """Supported browser engines."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    EDGE = "edge"


@dataclass
class SeleniumProfileConfig:
    """Configuration for Selenium browser profile."""

    name: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    headless: bool = True
    window_size: str = "1920,1080"
    timezone: Optional[str] = None
    language: str = "en-US"
    platform: str = "WINDOWS"
    browser_engine: BrowserEngine = BrowserEngine.CHROMIUM
    page_load_timeout: int = 30
    implicit_wait: int = 10


@dataclass
class SeleniumSession:
    """Represents an active Selenium session."""

    session_id: str
    profile_name: str
    started_at: datetime
    driver: Any
    config: SeleniumProfileConfig
    status: str = "active"


class SeleniumStealthOptions:
    """Creates stealth options for Selenium WebDriver."""

    CHROME_ARGS = [
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
        "--disable-features=IsolateOrigins,site-per-process",
        "--window-size=1920,1080",
        "--start-maximized",
        "--disable-blink-features",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-hang-monitor",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--no-crash-upload",
        "--no-pings",
        "--password-store=basic",
        "--use-mock-keychain",
    ]

    FIREFOX_ARGS = [
        "--headless",
    ]

    def __init__(self, config: SeleniumProfileConfig):
        self.config = config
        self.options = None

    def _get_chrome_options(self) -> Any:
        """Get configured Chrome options for Selenium."""
        try:
            from selenium.webdriver.chrome.options import Options
        except ImportError:
            logger.warning("Selenium not installed. Install with: pip install selenium")
            return None

        options = Options()

        if self.config.headless:
            options.add_argument("--headless=new")

        for arg in self.CHROME_ARGS:
            options.add_argument(arg)

        options.add_argument(f"--window-size={self.config.window_size}")

        if self.config.user_agent:
            options.add_argument(f"--user-agent={self.config.user_agent}")

        if self.config.proxy:
            proxy_str = self.config.proxy
            if self.config.proxy_username and self.config.proxy_password:
                proxy_str = f"{self.config.proxy_username}:{self.config.proxy_password}@{self.config.proxy}"
            options.add_argument(f"--proxy-server={proxy_str}")

        options.add_argument(f"--lang={self.config.language}")

        if self.config.timezone:
            options.add_argument(f"--time-zone={self.config.timezone}")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.geolocation": 2,
        }
        options.add_experimental_option("prefs", prefs)

        return options

    def _get_firefox_options(self) -> Any:
        """Get configured Firefox options for Selenium."""
        try:
            from selenium.webdriver.firefox.options import Options
        except ImportError:
            logger.warning("Selenium not installed. Install with: pip install selenium")
            return None

        options = Options()

        if self.config.headless:
            options.add_argument("--headless")

        if self.config.user_agent:
            options.set_preference("general.useragent.override", self.config.user_agent)

        if self.config.proxy:
            proxy_str = self.config.proxy
            if self.config.proxy_username and self.config.proxy_password:
                proxy_str = f"{self.config.proxy_username}:{self.config.proxy_password}@{self.config.proxy}"
            options.set_preference("network.proxy.http", self.config.proxy.split(":")[0] if ":" in self.config.proxy else self.config.proxy)
            options.set_preference("network.proxy.http_port", int(self.config.proxy.split(":")[-1]) if ":" in self.config.proxy else 80)
            options.set_preference("network.proxy.ssl", self.config.proxy.split(":")[0] if ":" in self.config.proxy else self.config.proxy)
            options.set_preference("network.proxy.ssl_port", int(self.config.proxy.split(":")[-1]) if ":" in self.config.proxy else 80)
            options.set_preference("network.proxy.type", 1)

        options.set_preference("intl.accept_languages", self.config.language)
        options.set_preference("geo.enabled", False)
        options.set_preference("media.navigator.streams.fake", True)
        options.set_preference("media.navigator.permission.disabled", True)

        return options

    def get_options(self) -> Any:
        """Get browser-specific options."""
        if self.config.browser_engine == BrowserEngine.CHROMIUM or self.config.browser_engine == BrowserEngine.EDGE:
            return self._get_chrome_options()
        elif self.config.browser_engine == BrowserEngine.FIREFOX:
            return self._get_firefox_options()
        return self._get_chrome_options()

    def get_stealth_js(self) -> List[str]:
        """Get JavaScript stealth scripts to inject."""
        from src.browser.stealth import get_combined_stealth_script

        scripts = [
            get_combined_stealth_script(timezone=self.config.timezone or "UTC"),
        ]
        return scripts


class SeleniumBrowserManager:
    """Manages Selenium browser instances with stealth capabilities."""

    def __init__(self, max_sessions: int = 10):
        self.sessions: Dict[str, SeleniumSession] = {}
        self._max_sessions = max_sessions

    def create_driver(self, config: SeleniumProfileConfig) -> Any:
        """Create a new Selenium WebDriver with stealth options."""
        if len(self.sessions) >= self._max_sessions:
            raise RuntimeError(f"Maximum sessions ({self._max_sessions}) reached")

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.firefox.service import Service as FirefoxService
        except ImportError:
            logger.error("Selenium not installed. Install with: pip install selenium")
            raise ImportError("selenium package not installed")

        stealth_options = SeleniumStealthOptions(config)
        browser_options = stealth_options.get_options()

        if not browser_options:
            raise RuntimeError("Failed to create browser options")

        try:
            if config.browser_engine == BrowserEngine.CHROMIUM:
                driver = webdriver.Chrome(options=browser_options)
            elif config.browser_engine == BrowserEngine.EDGE:
                driver = webdriver.Edge(options=browser_options)
            elif config.browser_engine == BrowserEngine.FIREFOX:
                driver = webdriver.Firefox(options=browser_options)
            else:
                driver = webdriver.Chrome(options=browser_options)

            driver.set_page_load_timeout(config.page_load_timeout)
            driver.implicitly_wait(config.implicit_wait)

        except Exception as e:
            logger.error(f"Failed to create browser driver: {e}")
            raise

        stealth_scripts = stealth_options.get_stealth_js()
        for script in stealth_scripts:
            try:
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument", {"source": script}
                )
            except Exception as e:
                logger.warning(f"Failed to inject stealth script: {e}")

        session_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = SeleniumSession(
            session_id=session_id,
            profile_name=config.name,
            started_at=datetime.now(),
            driver=driver,
            config=config,
        )

        self.sessions[session_id] = session
        logger.info(f"Created Selenium session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[SeleniumSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[SeleniumSession]:
        """List all active sessions."""
        return list(self.sessions.values())

    def navigate(self, session_id: str, url: str) -> bool:
        """Navigate to URL."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            session.driver.get(url)
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
            element = WebDriverWait(session.driver, 10).until(
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
            element = WebDriverWait(session.driver, 10).until(
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
            session.driver.save_screenshot(path)
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise

    def execute_script(self, session_id: str, script: str) -> Any:
        """Execute JavaScript."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.driver.execute_script(script)

    def get_page_source(self, session_id: str) -> str:
        """Get page source HTML."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.driver.page_source

    def get_title(self, session_id: str) -> str:
        """Get page title."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.driver.title

    def get_current_url(self, session_id: str) -> str:
        """Get current URL."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.driver.current_url

    def close_session(self, session_id: str) -> bool:
        """Close a session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            session.driver.quit()
            session.status = "closed"
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


def create_selenium_session(config: SeleniumProfileConfig) -> SeleniumBrowserManager:
    """Create a new Selenium browser session."""
    manager = SeleniumBrowserManager()
    manager.create_driver(config)
    return manager
