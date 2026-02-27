"""
Stress tests for proxy rotation performance and load.
"""

import pytest
import asyncio
import time
from typing import List

from src.proxy.rotation import ProxyManager, ProxyPool, RotationStrategy


class TestProxyRotationStress:
    """Stress tests for proxy rotation."""

    @pytest.mark.asyncio
    async def test_100_proxies_rotation(self):
        """Test rotating through 100 proxies."""
        pool = ProxyPool()

        for i in range(100):
            pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        proxies = []
        for _ in range(1000):
            proxy = await pool.get_next_proxy(strategy=RotationStrategy.RANDOM)
            if proxy:
                proxies.append(proxy)

        elapsed = time.time() - start_time

        assert len(proxies) == 1000
        assert elapsed < 1.0, f"Rotation took {elapsed}s, expected < 1s"

    @pytest.mark.asyncio
    async def test_concurrent_rotation_requests(self):
        """Test concurrent rotation requests."""
        manager = ProxyManager()

        for i in range(50):
            manager.pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        async def rotate():
            return await manager.rotate(strategy=RotationStrategy.RANDOM)

        results = await asyncio.gather(*[rotate() for _ in range(100)])

        elapsed = time.time() - start_time

        assert len(results) == 100
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_rapid_success_failure_reports(self):
        """Test rapid success/failure reporting."""
        manager = ProxyManager()

        for i in range(10):
            manager.pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        for i in range(100):
            proxy_id = list(manager.pool.proxies.keys())[i % 10]
            if i % 2 == 0:
                await manager.report_success(proxy_id, latency_ms=50)
            else:
                await manager.report_failure(proxy_id)

        elapsed = time.time() - start_time

        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_proxy_group_with_50_proxies(self):
        """Test proxy group with 50 proxies."""
        manager = ProxyManager()

        manager.create_group(
            name="large_group",
            rotation_strategy=RotationStrategy.WEIGHTED
        )

        for i in range(50):
            proxy_id = manager.pool.add_proxy(
                f"http://proxy{i}.com:8080",
                country="US"
            )
            manager.add_to_group(proxy_id, "large_group")

        stats = manager.get_group_stats("large_group")

        assert stats["total_proxies"] == 50


class TestProxyPoolStress:
    """Stress tests for proxy pool operations."""

    @pytest.mark.asyncio
    async def test_rapid_proxy_addition(self):
        """Test rapidly adding proxies."""
        pool = ProxyPool()

        start_time = time.time()

        for i in range(1000):
            pool.add_proxy(f"http://proxy{i}.com:8080")

        elapsed = time.time() - start_time

        assert len(pool.proxies) == 1000
        assert elapsed < 2.0

    @pytest.mark.asyncio
    async def test_rapid_proxy_removal(self):
        """Test rapidly removing proxies."""
        pool = ProxyPool()

        for i in range(100):
            pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        for i in range(100):
            proxy_id = list(pool.proxies.keys())[i]
            pool.remove_proxy(proxy_id)

        elapsed = time.time() - start_time

        assert len(pool.proxies) == 0
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_concurrent_proxy_operations(self):
        """Test concurrent proxy operations."""
        pool = ProxyPool()

        for i in range(20):
            pool.add_proxy(f"http://proxy{i}.com:8080")

        async def rotate_operation():
            return await pool.get_next_proxy()

        async def success_operation(proxy_id):
            await pool.mark_success(proxy_id)

        async def failure_operation(proxy_id):
            await pool.mark_failure(proxy_id)

        proxy_ids = list(pool.proxies.keys())

        tasks = []
        for i in range(50):
            tasks.append(rotate_operation())
            tasks.append(success_operation(proxy_ids[i % 20]))
            tasks.append(failure_operation(proxy_ids[(i + 10) % 20]))

        start_time = time.time()
        await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time

        assert elapsed < 3.0


class TestProxyHealthCheckStress:
    """Stress tests for proxy health checking."""

    @pytest.mark.asyncio
    async def test_health_check_50_proxies(self):
        """Test health checking 50 proxies."""
        manager = ProxyManager()

        for i in range(50):
            manager.pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        await manager.health_check()

        elapsed = time.time() - start_time

        assert elapsed < 30.0

    @pytest.mark.asyncio
    async def test_rapid_health_checks(self):
        """Test rapid repeated health checks."""
        manager = ProxyManager()

        for i in range(10):
            manager.pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        for _ in range(5):
            await manager.health_check()

        elapsed = time.time() - start_time

        assert elapsed < 60.0


class TestProxyStatisticsStress:
    """Stress tests for proxy statistics."""

    def test_stats_calculation_1000_requests(self):
        """Test statistics calculation with 1000 requests."""
        pool = ProxyPool()

        for i in range(10):
            pool.add_proxy(f"http://proxy{i}.com:8080")

        start_time = time.time()

        for i in range(1000):
            proxy_id = list(pool.proxies.keys())[i % 10]
            proxy_url = pool.proxies[proxy_id].url

            if i % 3 == 0:
                pool._update_usage_stats(proxy_url, "request")
            elif i % 3 == 1:
                pool._update_usage_stats(proxy_url, "success", 50)
            else:
                pool._update_usage_stats(proxy_url, "failure")

        stats = pool.get_stats()

        elapsed = time.time() - start_time

        assert stats["total_requests"] == 1000
        assert elapsed < 0.5


@pytest.mark.asyncio
async def test_memory_usage_large_pool():
    """Test memory usage with large proxy pool."""
    pool = ProxyPool()

    for i in range(1000):
        pool.add_proxy(f"http://proxy{i}.com:8080")

    import sys
    import gc
    gc.collect()

    stats = pool.get_stats()
    assert stats["total"] == 1000


@pytest.mark.asyncio
async def test_concurrent_managers():
    """Test multiple concurrent proxy managers."""
    async def manager_workflow(manager_id: int):
        manager = ProxyManager()

        for i in range(10):
            manager.pool.add_proxy(f"http://manager{manager_id}_proxy{i}.com:8080")

        for _ in range(20):
            proxy = await manager.rotate(strategy=RotationStrategy.RANDOM)
            if proxy:
                await manager.report_success(
                    list(manager.pool.proxies.keys())[0],
                    latency_ms=50
                )

        return manager.get_stats()

    results = await asyncio.gather(*[
        manager_workflow(i) for i in range(10)
    ])

    assert len(results) == 10
    for stats in results:
        assert stats["total"] == 10
