"""
Stress tests for browser manager performance and concurrency.
Tests concurrent sessions, performance metrics, and load handling.
"""
import asyncio
import time
import psutil
import pytest
from typing import List, Dict, Any

from src.browser.manager import BrowserManager, ProfileConfig


async def get_memory_usage_mb() -> float:
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


async def get_session_memory_mb(session) -> float:
    return await get_memory_usage_mb()


@pytest.mark.asyncio
async def test_concurrent_sessions_10():
    """Test creating 10 concurrent sessions."""
    async with BrowserManager() as manager:
        start_time = time.time()
        
        configs = [
            ProfileConfig(name=f"stress_test_{i}", headless=True)
            for i in range(10)
        ]
        
        sessions = await asyncio.gather(*[
            manager.create_session(config) for config in configs
        ])
        
        creation_time = time.time() - start_time
        
        assert len(sessions) == 10
        assert creation_time <= 5.0, f"Session creation took {creation_time}s, expected <= 5s"
        
        for session in sessions:
            await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_concurrent_sessions_20():
    """Test creating 20 concurrent sessions (target per docs)."""
    async with BrowserManager() as manager:
        start_time = time.time()
        
        configs = [
            ProfileConfig(name=f"stress_test_{i}", headless=True)
            for i in range(20)
        ]
        
        sessions = await asyncio.gather(*[
            manager.create_session(config) for config in configs
        ])
        
        creation_time = time.time() - start_time
        
        assert len(sessions) == 20
        assert creation_time <= 10.0, f"Session creation took {creation_time}s"
        
        for session in sessions:
            await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_session_startup_time():
    """Test individual session startup time meets requirement (<= 5s)."""
    async with BrowserManager() as manager:
        config = ProfileConfig(name="startup_test", headless=True)
        
        start_time = time.time()
        session = await manager.create_session(config)
        startup_time = time.time() - start_time
        
        assert startup_time <= 5.0, f"Startup time {startup_time}s exceeds 5s limit"
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_navigation_performance():
    """Test navigation performance meets requirement (<= 3s)."""
    async with BrowserManager() as manager:
        config = ProfileConfig(name="nav_test", headless=True)
        session = await manager.create_session(config)
        
        start_time = time.time()
        await manager.navigate(session.session_id, "https://example.com")
        nav_time = time.time() - start_time
        
        assert nav_time <= 3.0, f"Navigation took {nav_time}s, expected <= 3s"
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_memory_per_session():
    """Test memory usage per session meets requirement (<= 200MB)."""
    initial_memory = await get_memory_usage_mb()
    
    async with BrowserManager() as manager:
        config = ProfileConfig(name="memory_test", headless=True)
        session = await manager.create_session(config)
        
        await asyncio.sleep(1)
        
        current_memory = await get_memory_usage_mb()
        memory_used = current_memory - initial_memory
        
        assert memory_used <= 200, f"Memory usage {memory_used}MB exceeds 200MB limit"
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_sequential_session_creation():
    """Test sequential session creation performance."""
    async with BrowserManager() as manager:
        session_ids = []
        
        for i in range(10):
            config = ProfileConfig(name=f"seq_test_{i}", headless=True)
            session = await manager.create_session(config)
            session_ids.append(session.session_id)
        
        total_time_start = time.time()
        
        for session_id in session_ids:
            await manager.close_session(session_id)
        
        total_time = time.time() - total_time_start
        
        assert len(session_ids) == 10


@pytest.mark.asyncio
async def test_session_navigation_stress():
    """Test multiple navigations in sequence."""
    async with BrowserManager() as manager:
        config = ProfileConfig(name="nav_stress_test", headless=True)
        session = await manager.create_session(config)
        
        urls = [
            "https://example.com",
            "https://www.iana.org/domains/reserved",
            "https://httpbin.org/get",
        ]
        
        for url in urls:
            start_time = time.time()
            await manager.navigate(session.session_id, url)
            nav_time = time.time() - start_time
            
            assert nav_time <= 3.0, f"Navigation to {url} took {nav_time}s"
        
        await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_max_sessions_limit():
    """Test that max sessions limit is enforced."""
    manager = BrowserManager()
    manager._max_sessions = 5
    await manager.start()
    
    try:
        for i in range(5):
            config = ProfileConfig(name=f"max_test_{i}", headless=True)
            await manager.create_session(config)
        
        with pytest.raises(RuntimeError, match="Maximum sessions"):
            config = ProfileConfig(name="overflow", headless=True)
            await manager.create_session(config)
    finally:
        await manager.stop()


@pytest.mark.asyncio
async def test_session_isolation():
    """Test that sessions are isolated from each other."""
    async with BrowserManager() as manager:
        config1 = ProfileConfig(name="isolation_test_1", headless=True)
        config2 = ProfileConfig(name="isolation_test_2", headless=True)
        
        session1 = await manager.create_session(config1)
        session2 = await manager.create_session(config2)
        
        await manager.navigate(session1.session_id, "https://example.com")
        await manager.navigate(session2.session_id, "https://iana.org")
        
        url1 = session1.page.url
        url2 = session2.page.url
        
        assert "example.com" in url1
        assert "iana.org" in url2
        
        await manager.close_session(session1.session_id)
        await manager.close_session(session2.session_id)


@pytest.mark.asyncio
async def test_rapid_create_destroy():
    """Test rapid session creation and destruction."""
    async with BrowserManager() as manager:
        for i in range(20):
            config = ProfileConfig(name=f"rapid_{i}", headless=True)
            session = await manager.create_session(config)
            await manager.close_session(session.session_id)


@pytest.mark.asyncio
async def test_browser_manager_reuse():
    """Test that browser manager reuses browser instance."""
    async with BrowserManager() as manager:
        config1 = ProfileConfig(name="reuse_1", headless=True)
        config2 = ProfileConfig(name="reuse_2", headless=True)
        
        session1 = await manager.create_session(config1)
        session2 = await manager.create_session(config2)
        
        assert session1.browser is session2.browser
        
        await manager.close_session(session1.session_id)
        await manager.close_session(session2.session_id)


async def run_performance_benchmark() -> Dict[str, Any]:
    """Run complete performance benchmark and return metrics."""
    results = {
        "session_creation_times": [],
        "navigation_times": [],
        "memory_usage": [],
    }
    
    async with BrowserManager() as manager:
        for i in range(10):
            start = time.time()
            config = ProfileConfig(name=f"benchmark_{i}", headless=True)
            session = await manager.create_session(config)
            results["session_creation_times"].append(time.time() - start)
            
            start = time.time()
            await manager.navigate(session.session_id, "https://example.com")
            results["navigation_times"].append(time.time() - start)
            
            await manager.close_session(session.session_id)
        
        avg_creation = sum(results["session_creation_times"]) / len(results["session_creation_times"])
        avg_navigation = sum(results["navigation_times"]) / len(results["navigation_times"])
        
        results["avg_session_creation"] = avg_creation
        results["avg_navigation"] = avg_navigation
        results["meets_startup_requirement"] = avg_creation <= 5.0
        results["meets_navigation_requirement"] = avg_navigation <= 3.0
    
    return results


if __name__ == "__main__":
    async def main():
        print("Running performance benchmark...")
        results = await run_performance_benchmark()
        
        print(f"\n=== Performance Benchmark Results ===")
        print(f"Avg session creation time: {results['avg_session_creation']:.2f}s")
        print(f"Avg navigation time: {results['avg_navigation']:.2f}s")
        print(f"Meets startup requirement (<=5s): {results['meets_startup_requirement']}")
        print(f"Meets navigation requirement (<=3s): {results['meets_navigation_requirement']}")
    
    asyncio.run(main())
