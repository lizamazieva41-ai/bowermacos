"""
Proxy management module.
"""
import logging
from typing import Optional, Dict
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def parse(cls, proxy_string: str) -> "ProxyConfig":
        """Parse proxy string in format: protocol://user:pass@host:port"""
        pattern = r"(?:(?P<user>[^:]+):(?P<pass>[^@]+)@)?(?P<host>.+)"
        match = re.match(pattern, proxy_string)
        
        if not match:
            raise ValueError(f"Invalid proxy format: {proxy_string}")
        
        host = match.group("host")
        username = match.group("user")
        password = match.group("pass")

        if not host.startswith(("http://", "socks5://", "socks4://")):
            host = f"http://{host}"
        
        return cls(url=host, username=username, password=password)

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "server": self.url,
            "username": self.username,
            "password": self.password,
        }


class ProxyValidator:
    """Validate and test proxy connections."""

    @staticmethod
    async def validate(proxy_config: ProxyConfig) -> bool:
        """Validate proxy is reachable."""
        import httpx

        try:
            proxy_url = ProxyValidator._format_for_httpx(proxy_config)
            transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
            async with httpx.AsyncClient(transport=transport, timeout=10) as client:
                response = await client.get("http://ipinfo.io/json")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Proxy validation failed: {e}")
            return False

    @staticmethod
    def _format_for_httpx(proxy: ProxyConfig) -> str:
        """Format proxy for httpx."""
        if proxy.username and proxy.password:
            return f"{proxy.url.replace('http://', '')}"
        return proxy.url
