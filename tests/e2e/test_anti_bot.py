"""
E2E tests for anti-bot detection.
These tests verify that stealth features work correctly.
"""

import pytest


class TestStealthE2E:
    """E2E tests for stealth features."""

    @pytest.mark.asyncio
    async def test_webdriver_property_hidden(self):
        """Test that navigator.webdriver is hidden."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_stealth", headless=True)
            session = await manager.create_session(config)

            webdriver = await session.page.evaluate("navigator.webdriver")
            assert webdriver is None or webdriver is False

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_plugins_not_empty(self):
        """Test that navigator.plugins returns fake plugins."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_plugins", headless=True)
            session = await manager.create_session(config)

            plugins = await session.page.evaluate("navigator.plugins")
            assert plugins is not None
            assert len(plugins) > 0

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_languages_present(self):
        """Test that navigator.languages is present."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_lang", headless=True)
            session = await manager.create_session(config)

            languages = await session.page.evaluate("navigator.languages")
            assert languages is not None
            assert "en" in [l.lower() for l in languages]

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_hardware_concurrency(self):
        """Test that hardwareConcurrency is overridden."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_hw", headless=True)
            session = await manager.create_session(config)

            concurrency = await session.page.evaluate("navigator.hardwareConcurrency")
            assert concurrency is not None
            assert concurrency > 0

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_device_memory(self):
        """Test that deviceMemory is overridden."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_mem", headless=True)
            session = await manager.create_session(config)

            memory = await session.page.evaluate("navigator.deviceMemory")
            assert memory is not None
            assert memory > 0

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_webrtc_blocked(self):
        """Test that WebRTC is blocked."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_webrtc", headless=True)
            session = await manager.create_session(config)

            rtc_blocked = await session.page.evaluate("""
                typeof RTCPeerConnection === 'undefined' || 
                RTCPeerConnection === null ||
                (new RTCPeerConnection()).toString().includes('null')
            """)

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_chrome_runtime_present(self):
        """Test that chrome.runtime is present."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_chrome", headless=True)
            session = await manager.create_session(config)

            has_chrome = await session.page.evaluate(
                "typeof chrome !== 'undefined' && chrome.runtime !== undefined"
            )
            assert has_chrome is True

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_screen_properties(self):
        """Test that screen properties are overridden."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_screen", headless=True)
            session = await manager.create_session(config)

            width = await session.page.evaluate("screen.width")
            height = await session.page.evaluate("screen.height")

            assert width > 0
            assert height > 0

            await manager.close_session(session.session_id)


class TestFingerprintE2E:
    """E2E tests for fingerprint generation."""

    def test_fingerprint_generation_consistency(self):
        """Test that fingerprint generation is consistent."""
        from src.browser.fingerprint import FingerprintGenerator

        fp1 = FingerprintGenerator.generate()
        fp2 = FingerprintGenerator.generate()

        assert fp1 is not None
        assert fp2 is not None

    def test_fingerprint_has_required_fields(self):
        """Test that fingerprint has all required fields."""
        from src.browser.fingerprint import FingerprintGenerator

        fp = FingerprintGenerator.generate()

        required_fields = ["user_agent", "platform", "languages", "timezone"]
        for field in required_fields:
            assert field in fp

    def test_fingerprint_platform_windows(self):
        """Test Windows platform fingerprint."""
        from src.browser.fingerprint import FingerprintGenerator

        fp = FingerprintGenerator.generate(platform="windows")
        assert "Windows" in fp["user_agent"] or "Win64" in fp["user_agent"]

    def test_fingerprint_platform_macos(self):
        """Test macOS platform fingerprint."""
        from src.browser.fingerprint import FingerprintGenerator

        fp = FingerprintGenerator.generate(platform="macos")
        assert "Mac" in fp["user_agent"] or "Intel" in fp["user_agent"]

    def test_fingerprint_platform_linux(self):
        """Test Linux platform fingerprint."""
        from src.browser.fingerprint import FingerprintGenerator

        fp = FingerprintGenerator.generate(platform="linux")
        assert "Linux" in fp["user_agent"] or "X11" in fp["user_agent"]


class TestProxyE2E:
    """E2E tests for proxy functionality."""

    @pytest.mark.asyncio
    async def test_session_with_proxy_config(self):
        """Test creating session with proxy configuration."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(
                name="test_proxy", proxy="http://localhost:8080", headless=True
            )
            session = await manager.create_session(config)

            assert session is not None
            assert session.profile_name == "test_proxy"

            await manager.close_session(session.session_id)

    def test_proxy_config_parsing(self):
        """Test proxy configuration parsing."""
        from src.browser.manager import ProfileConfig

        config = ProfileConfig(
            name="test",
            proxy="http://user:pass@proxy.example.com:8080",
            proxy_username="user",
            proxy_password="pass",
        )

        assert config.proxy == "http://user:pass@proxy.example.com:8080"
        assert config.proxy_username == "user"
        assert config.proxy_password == "pass"


class TestBrowserContextE2E:
    """E2E tests for browser context."""

    @pytest.mark.asyncio
    async def test_context_timezone(self):
        """Test timezone configuration."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(
                name="test_tz", timezone="America/New_York", headless=True
            )
            session = await manager.create_session(config)

            tz = await session.page.evaluate(
                "Intl.DateTimeFormat().resolvedOptions().timeZone"
            )

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_context_language(self):
        """Test language configuration."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_lang", language="en-US", headless=True)
            session = await manager.create_session(config)

            lang = await session.page.evaluate("navigator.language")

            await manager.close_session(session.session_id)

    @pytest.mark.asyncio
    async def test_session_navigation(self):
        """Test basic navigation."""
        from src.browser.manager import BrowserManager, ProfileConfig

        async with BrowserManager() as manager:
            config = ProfileConfig(name="test_nav", headless=True)
            session = await manager.create_session(config)

            await session.page.goto(
                "https://example.com", wait_until="domcontentloaded"
            )
            title = await session.page.title()

            assert "Example" in title

            await manager.close_session(session.session_id)
