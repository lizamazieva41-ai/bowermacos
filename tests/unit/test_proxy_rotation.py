"""
Unit tests for proxy rotation module.
"""

import pytest
import asyncio
from datetime import datetime
from src.proxy.rotation import (
    ProxyPool,
    ProxyManager,
    ProxyRotation,
    RotationStrategy,
    ProxyStatus,
    Proxy,
    ProxyGroup,
)


class TestProxyRotation:
    """Unit tests for ProxyRotation class."""

    @pytest.mark.asyncio
    async def test_round_robin_strategy(self):
        """Test round-robin rotation strategy."""
        rotation = ProxyRotation(strategy=RotationStrategy.ROUND_ROBIN)

        proxies = [
            Proxy(url="http://proxy1.com:8080"),
            Proxy(url="http://proxy2.com:8080"),
            Proxy(url="http://proxy3.com:8080"),
        ]

        selected = await rotation.select_proxy(proxies)
        assert selected is not None

    @pytest.mark.asyncio
    async def test_random_strategy(self):
        """Test random rotation strategy."""
        rotation = ProxyRotation(strategy=RotationStrategy.RANDOM)

        proxies = [
            Proxy(url="http://proxy1.com:8080"),
            Proxy(url="http://proxy2.com:8080"),
        ]

        selected = await rotation.select_proxy(proxies)
        assert selected is not None
        assert selected.url.startswith("http://proxy")

    @pytest.mark.asyncio
    async def test_sticky_strategy(self):
        """Test sticky session rotation strategy."""
        rotation = ProxyRotation(strategy=RotationStrategy.STICKY)

        proxies = [
            Proxy(url="http://proxy1.com:8080"),
            Proxy(url="http://proxy2.com:8080"),
        ]

        selected1 = await rotation.select_proxy(proxies, session_id="session_123")
        selected2 = await rotation.select_proxy(proxies, session_id="session_123")

        assert selected1 is not None
        assert selected2 is not None


class TestProxyPool:
    """Unit tests for ProxyPool class."""

    def test_add_proxy(self):
        """Test adding a proxy to the pool."""
        pool = ProxyPool()
        proxy_id = pool.add_proxy(
            url="http://testproxy.com:8080",
            username="user",
            password="pass",
        )

        assert proxy_id is not None
        assert len(pool.proxies) == 1

    def test_add_multiple_proxies(self):
        """Test adding multiple proxies."""
        pool = ProxyPool()
        proxy_list = [
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
            "http://proxy3.com:8080",
        ]

        proxy_ids = pool.add_proxies(proxy_list)

        assert len(proxy_ids) == 3
        assert len(pool.proxies) == 3

    def test_detect_proxy_type(self):
        """Test proxy type detection."""
        pool = ProxyPool()

        assert pool._detect_proxy_type("http://proxy.com:8080") == "http"
        assert pool._detect_proxy_type("socks5://proxy.com:1080") == "socks5"
        assert pool._detect_proxy_type("socks4://proxy.com:1080") == "socks4"

    def test_get_active_proxies(self):
        """Test getting active proxies."""
        pool = ProxyPool()
        pool.add_proxy("http://proxy1.com:8080")
        pool.add_proxy("http://proxy2.com:8080")

        active = pool.get_active_proxies()
        assert len(active) == 2

    def test_remove_proxy(self):
        """Test removing a proxy."""
        pool = ProxyPool()
        proxy_id = pool.add_proxy("http://proxy1.com:8080")

        result = pool.remove_proxy(proxy_id)
        assert result is True
        assert len(pool.proxies) == 0

    def test_create_group(self):
        """Test creating a proxy group."""
        pool = ProxyPool()
        group_name = pool.create_group(
            name="us_proxies",
            country="US",
            rotation_strategy=RotationStrategy.RANDOM,
        )

        assert group_name == "us_proxies"
        assert "us_proxies" in pool.groups

    def test_add_proxy_to_group(self):
        """Test adding proxy to group."""
        pool = ProxyPool()
        proxy_id = pool.add_proxy("http://proxy1.com:8080")
        pool.create_group("us_proxies", country="US")

        result = pool.add_proxy_to_group(proxy_id, "us_proxies")
        assert result is True

    @pytest.mark.asyncio
    async def test_mark_success(self):
        """Test marking proxy as successful."""
        pool = ProxyPool()
        proxy_id = pool.add_proxy("http://proxy1.com:8080")

        await pool.mark_success(proxy_id, latency_ms=50)

        proxy = pool.proxies[proxy_id]
        assert proxy.success_count == 1
        assert proxy.latency_ms == 50
        assert proxy.status == ProxyStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_mark_failure(self):
        """Test marking proxy as failed."""
        pool = ProxyPool(max_failures=3)
        proxy_id = pool.add_proxy("http://proxy1.com:8080")

        await pool.mark_failure(proxy_id)

        proxy = pool.proxies[proxy_id]
        assert proxy.fail_count == 1
        assert proxy.consecutive_failures == 1


class TestProxyManager:
    """Unit tests for ProxyManager class."""

    def test_create_manager(self):
        """Test creating a proxy manager."""
        manager = ProxyManager(max_failures=3, cooldown_seconds=60)

        assert manager.pool is not None
        assert manager.pool.max_failures == 3
        assert manager.pool.cooldown_seconds == 60

    def test_create_group(self):
        """Test creating a proxy group via manager."""
        manager = ProxyManager()
        group_name = manager.create_group(
            name="eu_proxies",
            country="DE",
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
        )

        assert group_name == "eu_proxies"

    @pytest.mark.asyncio
    async def test_rotate_with_strategy(self):
        """Test rotating with specific strategy."""
        manager = ProxyManager()
        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")

        proxy = await manager.rotate(strategy=RotationStrategy.RANDOM)
        assert proxy is not None

    def test_get_stats(self):
        """Test getting proxy stats."""
        manager = ProxyManager()
        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")

        stats = manager.get_stats()

        assert stats["total"] == 2
        assert "active" in stats
        assert "failed" in stats


class TestProxyGroup:
    """Unit tests for ProxyGroup class."""

    def test_create_group(self):
        """Test creating a proxy group."""
        group = ProxyGroup(
            name="test_group",
            description="Test proxy group",
            country="US",
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
        )

        assert group.name == "test_group"
        assert group.country == "US"
        assert group.rotation_strategy == RotationStrategy.ROUND_ROBIN
