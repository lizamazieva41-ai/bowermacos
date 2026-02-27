"""
Integration tests for proxy rotation scenarios.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.proxy.rotation import (
    ProxyPool,
    ProxyManager,
    RotationStrategy,
    ProxyStatus,
)


class TestProxyRotationScenarios:
    """Integration tests for proxy rotation scenarios."""

    @pytest.mark.asyncio
    async def test_round_robin_rotation(self):
        """Test round-robin proxy rotation."""
        manager = ProxyManager()

        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")
        manager.pool.add_proxy("http://proxy3.com:8080")

        proxies = []
        for _ in range(6):
            proxy = await manager.rotate(strategy=RotationStrategy.ROUND_ROBIN)
            if proxy:
                proxies.append(proxy.url)

        assert len(set(proxies)) <= 3

    @pytest.mark.asyncio
    async def test_random_rotation(self):
        """Test random proxy rotation."""
        manager = ProxyManager()

        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")
        manager.pool.add_proxy("http://proxy3.com:8080")

        proxies = []
        for _ in range(20):
            proxy = await manager.rotate(strategy=RotationStrategy.RANDOM)
            if proxy:
                proxies.append(proxy.url)

        assert len(set(proxies)) > 1

    @pytest.mark.asyncio
    async def test_sticky_session_rotation(self):
        """Test sticky session rotation."""
        manager = ProxyManager()

        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")

        proxy1 = await manager.rotate(
            strategy=RotationStrategy.STICKY,
            session_id="session_123"
        )

        proxy2 = await manager.rotate(
            strategy=RotationStrategy.STICKY,
            session_id="session_123"
        )

        assert proxy1.url == proxy2.url

    @pytest.mark.asyncio
    async def test_geo_match_rotation(self):
        """Test geo-match proxy rotation."""
        manager = ProxyManager()

        manager.pool.add_proxy(
            "http://us-proxy.com:8080",
            country="US"
        )
        manager.pool.add_proxy(
            "http://de-proxy.com:8080",
            country="DE"
        )
        manager.pool.add_proxy(
            "http://jp-proxy.com:8080",
            country="JP"
        )

        proxy = await manager.rotate(
            strategy=RotationStrategy.GEO_MATCH,
            country="US"
        )

        assert proxy.country == "US"

    @pytest.mark.asyncio
    async def test_proxy_failover_rotation(self):
        """Test proxy failover when primary fails."""
        manager = ProxyManager(cooldown_seconds=1)

        proxy1_id = manager.pool.add_proxy("http://proxy1.com:8080")
        proxy2_id = manager.pool.add_proxy("http://proxy2.com:8080")

        await manager.report_failure(proxy1_id)

        proxy = await manager.rotate()

        assert proxy.url == "http://proxy2.com:8080"

    @pytest.mark.asyncio
    async def test_proxy_retry_on_failure(self):
        """Test automatic retry with different proxy on failure."""
        manager = ProxyManager(max_retries=3)

        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")
        manager.pool.add_proxy("http://proxy3.com:8080")

        proxy, attempts = await manager.rotate_with_retry(
            strategy=RotationStrategy.RANDOM,
            max_retries=3
        )

        assert proxy is not None
        assert attempts >= 1


class TestProxyGroupScenarios:
    """Integration tests for proxy group scenarios."""

    @pytest.mark.asyncio
    async def test_create_and_use_proxy_group(self):
        """Test creating and using a proxy group."""
        manager = ProxyManager()

        manager.create_group(
            name="us_premium",
            country="US",
            rotation_strategy=RotationStrategy.WEIGHTED
        )

        proxy1_id = manager.pool.add_proxy(
            "http://us-proxy1.com:8080",
            country="US"
        )
        proxy2_id = manager.pool.add_proxy(
            "http://us-proxy2.com:8080",
            country="US"
        )

        manager.add_to_group(proxy1_id, "us_premium")
        manager.add_to_group(proxy2_id, "us_premium")

        stats = manager.get_group_stats("us_premium")

        assert stats["name"] == "us_premium"
        assert stats["total_proxies"] == 2

    @pytest.mark.asyncio
    async def test_proxy_group_rotation(self):
        """Test rotation within a proxy group."""
        manager = ProxyManager()

        manager.create_group(
            name="eu_proxies",
            country="DE",
            rotation_strategy=RotationStrategy.RANDOM
        )

        for i in range(3):
            proxy_id = manager.pool.add_proxy(
                f"http://eu-proxy{i}.com:8080",
                country="DE"
            )
            manager.add_to_group(proxy_id, "eu_proxies")

        proxies = []
        for _ in range(10):
            proxy = await manager.rotate(
                strategy=RotationStrategy.RANDOM,
                group="eu_proxies"
            )
            if proxy:
                proxies.append(proxy)

        assert len(proxies) > 0


class TestProxyHealthMonitoring:
    """Integration tests for proxy health monitoring."""

    @pytest.mark.asyncio
    async def test_proxy_health_check(self):
        """Test proxy health check."""
        manager = ProxyManager()

        proxy_id = manager.pool.add_proxy("http://proxy1.com:8080")

        with patch("src.proxy.rotation.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = MagicMock(return_value={
                "country": "US",
                "region": "California",
                "city": "San Francisco",
                "org": "Test ISP"
            })

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            await manager.health_check()

            proxy = manager.pool.proxies[proxy_id]
            assert proxy.country == "US"

    @pytest.mark.asyncio
    async def test_proxy_success_reporting(self):
        """Test reporting proxy success."""
        manager = ProxyManager()

        proxy_id = manager.pool.add_proxy("http://proxy1.com:8080")

        await manager.report_success(proxy_id, latency_ms=50)

        proxy = manager.pool.proxies[proxy_id]
        assert proxy.success_count == 1
        assert proxy.latency_ms == 50

    @pytest.mark.asyncio
    async def test_proxy_failure_reporting(self):
        """Test reporting proxy failure."""
        manager = ProxyManager(max_failures=3)

        proxy_id = manager.pool.add_proxy("http://proxy1.com:8080")

        await manager.report_failure(proxy_id)

        proxy = manager.pool.proxies[proxy_id]
        assert proxy.fail_count == 1
        assert proxy.consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_proxy_cooldown_after_failures(self):
        """Test proxy cooldown after multiple failures."""
        manager = ProxyManager(max_failures=3, cooldown_seconds=60)

        proxy_id = manager.pool.add_proxy("http://proxy1.com:8080")

        for _ in range(3):
            await manager.report_failure(proxy_id)

        proxy = manager.pool.proxies[proxy_id]
        assert proxy.status == ProxyStatus.FAILED
        assert proxy.cooldown_until is not None


class TestProxyStatistics:
    """Integration tests for proxy statistics."""

    def test_pool_statistics(self):
        """Test getting pool statistics."""
        manager = ProxyManager()

        manager.pool.add_proxy("http://proxy1.com:8080")
        manager.pool.add_proxy("http://proxy2.com:8080")
        manager.pool.add_proxy("http://proxy3.com:8080")

        stats = manager.get_stats()

        assert stats["total"] == 3
        assert "active" in stats
        assert "failed" in stats

    @pytest.mark.asyncio
    async def test_usage_statistics(self):
        """Test usage statistics tracking."""
        manager = ProxyManager()

        proxy_id = manager.pool.add_proxy("http://proxy1.com:8080")
        proxy = manager.pool.proxies[proxy_id]

        await manager.report_success(proxy_id, latency_ms=50)
        await manager.report_success(proxy_id, latency_ms=60)
        await manager.report_failure(proxy_id)

        stats = manager.pool.get_usage_stats(proxy_id)

        assert stats["total_requests"] == 3
        assert stats["successful_requests"] == 2
        assert stats["failed_requests"] == 1
