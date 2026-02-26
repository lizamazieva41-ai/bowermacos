"""
Browser Manager - Core module for managing headless browser instances.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)


@dataclass
class ProfileConfig:
    """Configuration for a browser profile."""
    name: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timezone: Optional[str] = None
    language: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None
    extra_http_headers: Optional[Dict[str, str]] = None


@dataclass
class BrowserSession:
    """Represents an active browser session."""
    session_id: str
    profile_name: str
    started_at: datetime
    browser: Browser
    context: BrowserContext
    page: Page
    status: str = "active"


class BrowserManager:
    """Manages browser lifecycle with stealth capabilities."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.sessions: Dict[str, BrowserSession] = {}
        self.data_dir = data_dir or Path("./data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._max_sessions = 50

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """Initialize Playwright and browser."""
        logger.info("Starting browser manager...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ]
        )
        logger.info("Browser started successfully")

    async def stop(self):
        """Stop all sessions and cleanup."""
        logger.info("Stopping browser manager...")
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser manager stopped")

    def _build_launch_options(self, config: ProfileConfig) -> Dict[str, Any]:
        """Build browser context launch options."""
        options: Dict[str, Any] = {
            "viewport": {"width": config.viewport_width, "height": config.viewport_height},
            "ignore_https_errors": True,
        }

        if config.proxy:
            options["proxy"] = {
                "server": config.proxy,
                "username": config.proxy_username,
                "password": config.proxy_password,
            }

        if config.user_agent:
            options["user_agent"] = config.user_agent

        if config.timezone:
            options["timezone_id"] = config.timezone

        if config.language:
            options["locale"] = config.language
            options["languages"] = [config.language]

        if config.geolocation:
            options["geolocation"] = config.geolocation
            options["permissions"] = ["geolocation"]

        if config.extra_http_headers:
            options["extra_http_headers"] = config.extra_http_headers

        return options

    async def create_session(self, config: ProfileConfig) -> BrowserSession:
        """Create a new browser session with stealth capabilities."""
        if len(self.sessions) >= self._max_sessions:
            raise RuntimeError(f"Maximum sessions ({self._max_sessions}) reached")

        session_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        context_options = self._build_launch_options(config)
        context = await self.browser.new_context(**context_options)

        await self._apply_stealth(context)

        page = await context.new_page()

        session = BrowserSession(
            session_id=session_id,
            profile_name=config.name,
            started_at=datetime.now(),
            browser=self.browser,
            context=context,
            page=page,
        )

        self.sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        return session

    async def _apply_stealth(self, context: BrowserContext):
        """Apply stealth modifications to prevent detection."""
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            window.chrome = { runtime: {} };

            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1080
            });
        """)

    async def close_session(self, session_id: str) -> bool:
        """Close a browser session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        try:
            await session.page.close()
            await session.context.close()
            del self.sessions[session_id]
            logger.info(f"Closed session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            return False

    async def navigate(self, session_id: str, url: str, timeout: int = 30000) -> bool:
        """Navigate to a URL."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            await session.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise

    async def click(self, session_id: str, selector: str, timeout: int = 5000) -> bool:
        """Click an element."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            await session.page.click(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Click error: {e}")
            raise

    async def type_text(self, session_id: str, selector: str, text: str, timeout: int = 5000) -> bool:
        """Type text into an element."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            await session.page.fill(selector, text, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Type error: {e}")
            raise

    async def screenshot(self, session_id: str, path: str, full_page: bool = False) -> bool:
        """Take a screenshot."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            await session.page.screenshot(path=path, full_page=full_page)
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise

    async def execute_script(self, session_id: str, script: str) -> Any:
        """Execute JavaScript in the page."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return await session.page.evaluate(script)

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[BrowserSession]:
        """List all active sessions."""
        return list(self.sessions.values())
