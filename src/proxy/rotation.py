"""
Proxy rotation and health check module.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class ProxyStatus(Enum):
    ACTIVE = "active"
    TESTING = "testing"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class Proxy:
    """Proxy configuration with status tracking."""

    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    status: ProxyStatus = ProxyStatus.ACTIVE
    last_checked: Optional[datetime] = None
    latency_ms: Optional[int] = None
    success_count: int = 0
    fail_count: int = 0
    country: Optional[str] = None
    proxy_type: str = "http"


class ProxyPool:
    """Manage a pool of proxies with rotation and health checking."""

    def __init__(self, max_failures: int = 3):
        self.proxies: Dict[str, Proxy] = {}
        self.max_failures = max_failures
        self._current_index = 0
        self._lock = asyncio.Lock()

    def add_proxy(
        self, url: str, username: Optional[str] = None, password: Optional[str] = None
    ) -> str:
        """Add a proxy to the pool. Returns proxy ID."""
        proxy_id = self._generate_proxy_id(url)
        self.proxies[proxy_id] = Proxy(
            url=url,
            username=username,
            password=password,
            status=ProxyStatus.ACTIVE,
            proxy_type=self._detect_proxy_type(url),
        )
        logger.info(f"Added proxy: {proxy_id}")
        return proxy_id

    def add_proxies(self, proxy_list: List[str]) -> List[str]:
        """Add multiple proxies from connection strings."""
        proxy_ids = []
        for proxy_str in proxy_list:
            proxy_id = self.add_proxy(proxy_str)
            proxy_ids.append(proxy_id)
        return proxy_ids

    def _generate_proxy_id(self, url: str) -> str:
        """Generate unique ID for proxy."""
        import hashlib

        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _detect_proxy_type(self, url: str) -> str:
        """Detect proxy type from URL."""
        if "socks5" in url:
            return "socks5"
        elif "socks4" in url:
            return "socks4"
        return "http"

    async def get_next_proxy(self) -> Optional[Proxy]:
        """Get next available proxy using round-robin."""
        async with self._lock:
            active_proxies = [
                p for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE
            ]

            if not active_proxies:
                return None

            proxy = active_proxies[self._current_index % len(active_proxies)]
            self._current_index += 1
            return proxy

    async def mark_success(self, proxy_id: str):
        """Mark proxy as successful."""
        async with self._lock:
            if proxy_id in self.proxies:
                proxy = self.proxies[proxy_id]
                proxy.success_count += 1
                proxy.status = ProxyStatus.ACTIVE

    async def mark_failure(self, proxy_id: str):
        """Mark proxy as failed."""
        async with self._lock:
            if proxy_id in self.proxies:
                proxy = self.proxies[proxy_id]
                proxy.fail_count += 1
                if proxy.fail_count >= self.max_failures:
                    proxy.status = ProxyStatus.FAILED
                    logger.warning(f"Proxy {proxy_id} marked as failed")

    async def check_proxy_health(self, proxy: Proxy, timeout: int = 10) -> bool:
        """Check if proxy is working."""
        try:
            proxy_dict = {
                "server": proxy.url,
                "username": proxy.username,
                "password": proxy.password,
            }

            transport = httpx.AsyncHTTPTransport(proxy=proxy.url)
            async with httpx.AsyncClient(
                transport=transport, timeout=timeout
            ) as client:
                start = datetime.now()
                response = await client.get("http://ipinfo.io/json")
                latency = int((datetime.now() - start).total_seconds() * 1000)

                if response.status_code == 200:
                    proxy.latency_ms = latency
                    proxy.last_checked = datetime.now()
                    data = response.json()
                    proxy.country = data.get("country", "Unknown")
                    return True

        except Exception as e:
            logger.debug(f"Proxy health check failed: {e}")

        proxy.status = ProxyStatus.FAILED
        return False

    async def health_check_all(self, timeout: int = 10):
        """Check health of all proxies."""
        logger.info("Starting proxy health check...")

        for proxy_id, proxy in self.proxies.items():
            proxy.status = ProxyStatus.TESTING
            is_healthy = await self.check_proxy_health(proxy, timeout)

            if is_healthy:
                proxy.status = ProxyStatus.ACTIVE
                logger.info(f"Proxy {proxy_id}: OK ({proxy.latency_ms}ms)")
            else:
                proxy.status = ProxyStatus.FAILED
                logger.warning(f"Proxy {proxy_id}: FAILED")

        logger.info("Proxy health check completed")

    def get_proxy_by_id(self, proxy_id: str) -> Optional[Proxy]:
        """Get proxy by ID."""
        return self.proxies.get(proxy_id)

    def get_active_proxies(self) -> List[Proxy]:
        """Get all active proxies."""
        return [p for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE]

    def get_all_proxies(self) -> List[Proxy]:
        """Get all proxies."""
        return list(self.proxies.values())

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy from pool."""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total = len(self.proxies)
        active = len(
            [p for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE]
        )
        failed = len(
            [p for p in self.proxies.values() if p.status == ProxyStatus.FAILED]
        )

        return {
            "total": total,
            "active": active,
            "failed": failed,
            "utilization": f"{(active/total*100):.1f}%" if total > 0 else "0%",
        }


class ProxyManager:
    """High-level proxy management with rotation."""

    def __init__(self, max_failures: int = 3):
        self.pool = ProxyPool(max_failures)

    async def add_proxies_from_file(self, filepath: str) -> int:
        """Load proxies from file (one per line)."""
        count = 0
        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.pool.add_proxy(line)
                        count += 1
        except FileNotFoundError:
            logger.error(f"Proxy file not found: {filepath}")
        return count

    async def rotate(self) -> Optional[Proxy]:
        """Get next available proxy."""
        return await self.pool.get_next_proxy()

    async def report_success(self, proxy_id: str):
        """Report successful proxy usage."""
        await self.pool.mark_success(proxy_id)

    async def report_failure(self, proxy_id: str):
        """Report failed proxy usage."""
        await self.pool.mark_failure(proxy_id)

    async def health_check(self):
        """Run health check on all proxies."""
        await self.pool.health_check_all()

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        return self.pool.get_stats()
