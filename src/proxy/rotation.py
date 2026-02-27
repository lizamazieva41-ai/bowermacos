"""
Proxy rotation and health check module.
"""

import asyncio
import logging
import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

import httpx

logger = logging.getLogger(__name__)


class RotationStrategy(Enum):
    """Proxy rotation strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    STICKY = "sticky"
    FAILOVER = "failover"
    WEIGHTED = "weighted"
    GEO_MATCH = "geo_match"


class ProxyStatus(Enum):
    ACTIVE = "active"
    TESTING = "testing"
    FAILED = "failed"
    EXPIRED = "expired"
    COOLDOWN = "cooldown"


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
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    weight: int = 100
    tags: List[str] = field(default_factory=list)
    session_id: Optional[str] = None


@dataclass
class ProxyGroup:
    """Group of proxies with similar characteristics."""

    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    proxy_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    proxies: List[str] = field(default_factory=list)
    rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    min_proxies: int = 1
    max_proxies: int = 100


class ProxyRotation:
    """Advanced proxy rotation with multiple strategies."""

    def __init__(
        self,
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        cooldown_seconds: int = 60,
        max_retries: int = 3,
    ):
        self.strategy = strategy
        self.cooldown_seconds = cooldown_seconds
        self.max_retries = max_retries
        self._current_index = 0
        self._sticky_sessions: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def select_proxy(
        self,
        proxies: List[Proxy],
        session_id: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Optional[Proxy]:
        """Select a proxy based on the rotation strategy."""
        active_proxies = [p for p in proxies if self._is_available(p)]

        if not active_proxies:
            return None

        if self.strategy == RotationStrategy.ROUND_ROBIN:
            return await self._round_robin(active_proxies)
        elif self.strategy == RotationStrategy.RANDOM:
            return await self._random_select(active_proxies)
        elif self.strategy == RotationStrategy.STICKY:
            return await self._sticky_select(active_proxies, session_id)
        elif self.strategy == RotationStrategy.WEIGHTED:
            return await self._weighted_select(active_proxies)
        elif self.strategy == RotationStrategy.GEO_MATCH:
            return await self._geo_match_select(active_proxies, country)
        else:
            return await self._round_robin(active_proxies)

    def _is_available(self, proxy: Proxy) -> bool:
        """Check if proxy is available for use."""
        if proxy.status != ProxyStatus.ACTIVE:
            return False

        if proxy.cooldown_until and datetime.now() < proxy.cooldown_until:
            return False

        return True

    async def _round_robin(self, proxies: List[Proxy]) -> Proxy:
        """Round-robin selection."""
        async with self._lock:
            proxy = proxies[self._current_index % len(proxies)]
            self._current_index += 1
            return proxy

    async def _random_select(self, proxies: List[Proxy]) -> Proxy:
        """Random selection."""
        return random.choice(proxies)

    async def _sticky_select(
        self, proxies: List[Proxy], session_id: Optional[str]
    ) -> Proxy:
        """Sticky session - same proxy for same session."""
        if session_id and session_id in self._sticky_sessions:
            sticky_proxy_id = self._sticky_sessions[session_id]
            for proxy in proxies:
                if proxy.url == sticky_proxy_id and self._is_available(proxy):
                    return proxy

        proxy = random.choice(proxies)
        if session_id:
            self._sticky_sessions[session_id] = proxy.url
        return proxy

    async def _weighted_select(self, proxies: List[Proxy]) -> Proxy:
        """Weighted selection based on performance."""
        weights = []
        for proxy in proxies:
            success_rate = (
                proxy.success_count / (proxy.success_count + proxy.fail_count + 1)
            )
            latency_factor = max(0, 1 - (proxy.latency_ms or 1000) / 5000)
            weight = int(success_rate * 50 + latency_factor * 50 + proxy.weight)
            weights.append(max(1, weight))

        total_weight = sum(weights)
        rand = random.uniform(0, total_weight)
        cumulative = 0

        for i, proxy in enumerate(proxies):
            cumulative += weights[i]
            if rand <= cumulative:
                return proxy

        return proxies[0]

    async def _geo_match_select(
        self, proxies: List[Proxy], country: Optional[str]
    ) -> Proxy:
        """Select proxy matching the target country."""
        if not country:
            return random.choice(proxies)

        matching = [p for p in proxies if p.country == country]
        if matching:
            return random.choice(matching)

        return random.choice(proxies)


class ProxyPool:
    """Manage a pool of proxies with rotation and health checking."""

    def __init__(
        self,
        max_failures: int = 3,
        cooldown_seconds: int = 60,
    ):
        self.proxies: Dict[str, Proxy] = {}
        self.groups: Dict[str, ProxyGroup] = {}
        self.max_failures = max_failures
        self.cooldown_seconds = cooldown_seconds
        self._current_index = 0
        self._lock = asyncio.Lock()
        self.rotation = ProxyRotation(cooldown_seconds=cooldown_seconds)
        self._usage_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_latency": 0,
                "last_used": None,
                "uptime_percentage": 0,
            }
        )

    def add_proxy(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        country: Optional[str] = None,
        proxy_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Add a proxy to the pool. Returns proxy ID."""
        proxy_id = self._generate_proxy_id(url)
        self.proxies[proxy_id] = Proxy(
            url=url,
            username=username,
            password=password,
            status=ProxyStatus.ACTIVE,
            proxy_type=proxy_type or self._detect_proxy_type(url),
            country=country,
            tags=tags or [],
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

    def create_group(
        self,
        name: str,
        country: Optional[str] = None,
        proxy_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
    ) -> str:
        """Create a proxy group."""
        group = ProxyGroup(
            name=name,
            country=country,
            proxy_type=proxy_type,
            tags=tags or [],
            rotation_strategy=rotation_strategy,
        )
        self.groups[name] = group
        logger.info(f"Created proxy group: {name}")
        return name

    def add_proxy_to_group(self, proxy_id: str, group_name: str) -> bool:
        """Add a proxy to a group."""
        if proxy_id not in self.proxies:
            return False

        if group_name not in self.groups:
            return False

        if proxy_id not in self.groups[group_name].proxies:
            self.groups[group_name].proxies.append(proxy_id)

        return True

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

    async def get_next_proxy(
        self,
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        session_id: Optional[str] = None,
        group: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Optional[Proxy]:
        """Get next available proxy using specified strategy."""
        async with self._lock:
            proxies = self._get_proxies_for_selection(group, country)

            if not proxies:
                return None

            self.rotation.strategy = strategy
            proxy = await self.rotation.select_proxy(
                proxies, session_id=session_id, country=country
            )

            if proxy:
                proxy.last_used = datetime.now()
                self._update_usage_stats(proxy.url, "request")

            return proxy

    def _get_proxies_for_selection(
        self, group: Optional[str] = None, country: Optional[str] = None
    ) -> List[Proxy]:
        """Get proxies filtered by group and country."""
        proxies = list(self.proxies.values())

        if group and group in self.groups:
            group_obj = self.groups[group]
            proxies = [self.proxies[pid] for pid in group_obj.proxies if pid in self.proxies]

        if country:
            proxies = [p for p in proxies if p.country == country]

        return [p for p in proxies if self.rotation._is_available(p)]

    async def get_next_with_retry(
        self,
        max_retries: Optional[int] = None,
        **kwargs,
    ) -> tuple[Optional[Proxy], int]:
        """Get next proxy with automatic retry on failure."""
        max_retries = max_retries or self.max_retries
        tried_proxies = set()

        for attempt in range(max_retries):
            proxy = await self.get_next_proxy(**kwargs)

            if not proxy:
                break

            if proxy.url in tried_proxies:
                continue

            tried_proxies.add(proxy.url)
            return proxy, attempt + 1

        return None, max_retries

    async def mark_success(self, proxy_id: str, latency_ms: Optional[int] = None):
        """Mark proxy as successful."""
        async with self._lock:
            if proxy_id in self.proxies:
                proxy = self.proxies[proxy_id]
                proxy.success_count += 1
                proxy.consecutive_failures = 0
                proxy.status = ProxyStatus.ACTIVE

                if latency_ms:
                    proxy.latency_ms = latency_ms

                self._update_usage_stats(proxy.url, "success", latency_ms)

    async def mark_failure(self, proxy_id: str):
        """Mark proxy as failed with cooldown."""
        async with self._lock:
            if proxy_id in self.proxies:
                proxy = self.proxies[proxy_id]
                proxy.fail_count += 1
                proxy.consecutive_failures += 1
                proxy.last_failure = datetime.now()

                self._update_usage_stats(proxy.url, "failure")

                if proxy.consecutive_failures >= self.max_failures:
                    proxy.status = ProxyStatus.FAILED
                    logger.warning(f"Proxy {proxy_id} marked as failed")

                proxy.cooldown_until = datetime.now() + timedelta(
                    seconds=self.cooldown_seconds * proxy.consecutive_failures
                )

    async def check_proxy_health(
        self, proxy: Proxy, timeout: int = 10
    ) -> bool:
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
                start = time.time()
                response = await client.get("http://ipinfo.io/json")
                latency = int((time.time() - start) * 1000)

                if response.status_code == 200:
                    proxy.latency_ms = latency
                    proxy.last_checked = datetime.now()
                    data = response.json()
                    proxy.country = data.get("country", "Unknown")
                    proxy.region = data.get("region", None)
                    proxy.city = data.get("city", None)
                    proxy.isp = data.get("org", None)
                    return True

        except Exception as e:
            logger.debug(f"Proxy health check failed: {e}")

        proxy.status = ProxyStatus.FAILED
        return False

    async def health_check_all(self, timeout: int = 10):
        """Check health of all proxies."""
        logger.info("Starting proxy health check...")

        tasks = []
        for proxy_id, proxy in self.proxies.items():
            proxy.status = ProxyStatus.TESTING
            tasks.append(self._check_and_update(proxy_id, proxy, timeout))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for proxy_id, result in zip(self.proxies.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Proxy {proxy_id} health check error: {result}")

        logger.info("Proxy health check completed")

    async def _check_and_update(
        self, proxy_id: str, proxy: Proxy, timeout: int
    ) -> bool:
        """Check and update proxy status."""
        is_healthy = await self.check_proxy_health(proxy, timeout)

        async with self._lock:
            if is_healthy:
                proxy.status = ProxyStatus.ACTIVE
                logger.info(f"Proxy {proxy_id}: OK ({proxy.latency_ms}ms)")
            else:
                proxy.status = ProxyStatus.FAILED
                logger.warning(f"Proxy {proxy_id}: FAILED")

        return is_healthy

    def _update_usage_stats(
        self, proxy_url: str, event: str, latency: Optional[int] = None
    ):
        """Update usage statistics for a proxy."""
        stats = self._usage_stats[proxy_url]

        if event == "request":
            stats["total_requests"] += 1
            stats["last_used"] = datetime.now()
        elif event == "success":
            stats["successful_requests"] += 1
            if latency:
                current_avg = stats["avg_latency"]
                total_success = stats["successful_requests"]
                stats["avg_latency"] = (
                    (current_avg * (total_success - 1) + latency) / total_success
                )
        elif event == "failure":
            stats["failed_requests"] += 1

        total = stats["total_requests"]
        if total > 0:
            stats["uptime_percentage"] = (
                stats["successful_requests"] / total
            ) * 100

    def get_proxy_by_id(self, proxy_id: str) -> Optional[Proxy]:
        """Get proxy by ID."""
        return self.proxies.get(proxy_id)

    def get_active_proxies(self) -> List[Proxy]:
        """Get all active proxies."""
        return [
            p
            for p in self.proxies.values()
            if p.status == ProxyStatus.ACTIVE
        ]

    def get_all_proxies(self) -> List[Proxy]:
        """Get all proxies."""
        return list(self.proxies.values())

    def get_proxies_by_group(self, group_name: str) -> List[Proxy]:
        """Get proxies in a specific group."""
        if group_name not in self.groups:
            return []

        return [
            self.proxies[pid]
            for pid in self.groups[group_name].proxies
            if pid in self.proxies
        ]

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy from pool."""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]

            for group in self.groups.values():
                if proxy_id in group.proxies:
                    group.proxies.remove(proxy_id)

            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        total = len(self.proxies)
        active = len([p for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE])
        failed = len([p for p in self.proxies.values() if p.status == ProxyStatus.FAILED])

        total_requests = sum(s["total_requests"] for s in self._usage_stats.values())
        total_success = sum(s["successful_requests"] for s in self._usage_stats.values())

        return {
            "total": total,
            "active": active,
            "failed": failed,
            "utilization": f"{(active/total*100):.1f}%" if total > 0 else "0%",
            "total_requests": total_requests,
            "success_rate": f"{(total_success/total_requests*100):.1f}%"
            if total_requests > 0
            else "0%",
            "groups": len(self.groups),
        }

    def get_usage_stats(self, proxy_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed usage statistics."""
        if proxy_id:
            proxy = self.proxies.get(proxy_id)
            if proxy:
                return self._usage_stats.get(proxy.url, {})
            return {}

        return dict(self._usage_stats)

    def get_group_stats(self, group_name: str) -> Dict[str, Any]:
        """Get statistics for a specific group."""
        if group_name not in self.groups:
            return {}

        group = self.groups[group_name]
        proxies = self.get_proxies_by_group(group_name)

        return {
            "name": group.name,
            "total_proxies": len(proxies),
            "active_proxies": len([p for p in proxies if p.status == ProxyStatus.ACTIVE]),
            "rotation_strategy": group.rotation_strategy.value,
        }


class ProxyManager:
    """High-level proxy management with rotation."""

    def __init__(
        self,
        max_failures: int = 3,
        cooldown_seconds: int = 60,
    ):
        self.pool = ProxyPool(max_failures, cooldown_seconds)

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

    async def rotate(
        self,
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        session_id: Optional[str] = None,
        group: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Optional[Proxy]:
        """Get next available proxy."""
        return await self.pool.get_next_proxy(
            strategy=strategy,
            session_id=session_id,
            group=group,
            country=country,
        )

    async def rotate_with_retry(
        self,
        max_retries: int = 3,
        **kwargs,
    ) -> tuple[Optional[Proxy], int]:
        """Get next proxy with retry."""
        return await self.pool.get_next_with_retry(max_retries=max_retries, **kwargs)

    async def report_success(
        self, proxy_id: str, latency_ms: Optional[int] = None
    ):
        """Report successful proxy usage."""
        await self.pool.mark_success(proxy_id, latency_ms)

    async def report_failure(self, proxy_id: str):
        """Report failed proxy usage."""
        await self.pool.mark_failure(proxy_id)

    async def health_check(self):
        """Run health check on all proxies."""
        await self.pool.health_check_all()

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        return self.pool.get_stats()

    def create_group(
        self,
        name: str,
        country: Optional[str] = None,
        proxy_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
    ) -> str:
        """Create a proxy group."""
        return self.pool.create_group(
            name, country, proxy_type, tags, rotation_strategy
        )

    def add_to_group(self, proxy_id: str, group_name: str) -> bool:
        """Add proxy to group."""
        return self.pool.add_proxy_to_group(proxy_id, group_name)

    def get_group_stats(self, group_name: str) -> Dict[str, Any]:
        """Get group statistics."""
        return self.pool.get_group_stats(group_name)
