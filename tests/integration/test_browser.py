"""
Test browser manager.
"""
import asyncio
import pytest

from src.browser.manager import BrowserManager, ProfileConfig


@pytest.mark.asyncio
async def test_browser_start():
    """Test basic browser start."""
    async with BrowserManager() as manager:
        assert manager.browser is not None
        assert manager.playwright is not None


@pytest.mark.asyncio
async def test_create_session():
    """Test creating a browser session."""
    async with BrowserManager() as manager:
        config = ProfileConfig(
            name="test_profile",
            headless=True,
        )
        session = await manager.create_session(config)
        
        assert session.session_id is not None
        assert session.profile_name == "test_profile"
        assert session.status == "active"
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_navigate():
    """Test navigation."""
    async with BrowserManager() as manager:
        config = ProfileConfig(name="test", headless=True)
        session = await manager.create_session(config)
        
        await manager.navigate(session.session_id, "https://example.com")
        
        title = await session.page.title()
        assert "Example" in title
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_stealth_fingerprint():
    """Test stealth fingerprint is applied."""
    async with BrowserManager() as manager:
        config = ProfileConfig(name="test", headless=True)
        session = await manager.create_session(config)
        
        webdriver = await session.page.evaluate("navigator.webdriver")
        assert webdriver is None or webdriver is False
        
        await manager.close_session(session.session_id)
