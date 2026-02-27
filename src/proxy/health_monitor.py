"""
Proxy health monitoring service.
Monitors proxy status and health in the background.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ProxyStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    CHECKING = "checking"


@dataclass
class ProxyHealth:
    proxy_url: str
    status: ProxyStatus = ProxyStatus.UNKNOWN
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    successful_checks: int = 0
    error_message: Optional[str] = None


class ProxyHealthMonitor:
    def __init__(
        self,
        check_interval: int = 60,
        max_consecutive_failures: int = 3,
    ):
        self.proxy_health: Dict[str, ProxyHealth] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.check_interval = check_interval
        self.max_consecutive_failures = max_consecutive_failures

    async def start(self):
        """Start the proxy health monitoring."""
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Proxy health monitoring started")

    async def stop(self):
        """Stop the proxy health monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Proxy health monitoring stopped")

    async def _monitor_loop(self):
        """Background task to check proxy health."""
        while self._monitoring:
            try:
                await self._check_all_proxies()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in proxy health monitoring: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_all_proxies(self):
        """Check health of all registered proxies."""
        tasks = []
        for proxy_url in list(self.proxy_health.keys()):
            tasks.append(self._check_proxy_health(proxy_url))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_proxy_health(self, proxy_url: str):
        """Check health of a single proxy."""
        if proxy_url not in self.proxy_health:
            self.proxy_health[proxy_url] = ProxyHealth(proxy_url=proxy_url)

        health = self.proxy_health[proxy_url]
        health.status = ProxyStatus.CHECKING

        try:
            from src.proxy.validator import ProxyValidator
            validator = ProxyValidator()
            result = await validator.validate_proxy(proxy_url, timeout=10)

            health.last_check = datetime.now(timezone.utc)
            health.total_checks += 1

            if result.is_valid:
                health.status = ProxyStatus.HEALTHY
                health.response_time_ms = result.response_time_ms
                health.consecutive_failures = 0
                health.successful_checks += 1
                health.error_message = None
            else:
                health.status = ProxyStatus.UNHEALTHY
                health.consecutive_failures += 1
                health.error_message = result.error_message

        except Exception as e:
            health.status = ProxyStatus.UNHEALTHY
            health.consecutive_failures += 1
            health.error_message = str(e)
            logger.warning(f"Proxy health check failed for {proxy_url}: {e}")

    def register_proxy(self, proxy_url: str):
        """Register a proxy for health monitoring."""
        if proxy_url not in self.proxy_health:
            self.proxy_health[proxy_url] = ProxyHealth(proxy_url=proxy_url)
            logger.info(f"Registered proxy for health monitoring: {proxy_url}")

    def unregister_proxy(self, proxy_url: str):
        """Unregister a proxy from health monitoring."""
        if proxy_url in self.proxy_health:
            del self.proxy_health[proxy_url]
            logger.info(f"Unregistered proxy from health monitoring: {proxy_url}")

    def get_proxy_health(self, proxy_url: str) -> Optional[ProxyHealth]:
        """Get health status for a specific proxy."""
        return self.proxy_health.get(proxy_url)

    def get_all_proxy_health(self) -> List[ProxyHealth]:
        """Get health status for all registered proxies."""
        return list(self.proxy_health.values())

    def get_healthy_proxies(self) -> List[str]:
        """Get list of healthy proxy URLs."""
        return [
            proxy_url
            for proxy_url, health in self.proxy_health.items()
            if health.status == ProxyStatus.HEALTHY
        ]

    def get_unhealthy_proxies(self) -> List[str]:
        """Get list of unhealthy proxy URLs."""
        return [
            proxy_url
            for proxy_url, health in self.proxy_health.items()
            if health.status == ProxyStatus.UNHEALTHY
        ]

    def get_health_summary(self) -> Dict:
        """Get a summary of proxy health status."""
        total = len(self.proxy_health)
        healthy = sum(1 for h in self.proxy_health.values() if h.status == ProxyStatus.HEALTHY)
        unhealthy = sum(1 for h in self.proxy_health.values() if h.status == ProxyStatus.UNHEALTHY)
        unknown = sum(1 for h in self.proxy_health.values() if h.status == ProxyStatus.UNKNOWN)

        return {
            "total_proxies": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "unknown": unknown,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
        }

    async def check_proxy_now(self, proxy_url: str) -> ProxyHealth:
        """Immediately check health of a specific proxy."""
        await self._check_proxy_health(proxy_url)
        return self.proxy_health[proxy_url]


proxy_health_monitor = ProxyHealthMonitor()
