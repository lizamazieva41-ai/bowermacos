"""
Proxy validation service.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import socket
import re

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"


@dataclass
class ProxyValidationResult:
    is_valid: bool
    protocol_supported: bool
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class ProxyValidator:
    """Validate proxy configurations."""

    SUPPORTED_PROTOCOLS = {"http", "https", "socks5", "socks4"}

    PROXY_REGEX = re.compile(
        r"^(?P<type>http|https|socks5|socks4)://"
        r"(?:(?P<username>[^:]+):(?P<password>[^@]+)@)?"
        r"(?P<host>[^:]+):(?P<port>\d+)$"
    )

    def parse_proxy_url(self, proxy_url: str) -> Optional[ProxyConfig]:
        match = self.PROXY_REGEX.match(proxy_url)
        if not match:
            return None

        return ProxyConfig(
            server=f"{match.group('host')}:{match.group('port')}",
            username=match.group("username"),
            password=match.group("password"),
            proxy_type=match.group("type"),
        )

    def validate_proxy_type(self, proxy_type: str) -> bool:
        return proxy_type.lower() in self.SUPPORTED_PROTOCOLS

    async def validate_proxy(
        self, proxy_url: str, timeout: int = 10
    ) -> ProxyValidationResult:
        config = self.parse_proxy_url(proxy_url)

        if not config:
            return ProxyValidationResult(
                is_valid=False,
                protocol_supported=False,
                error_message="Invalid proxy URL format",
            )

        if not self.validate_proxy_type(config.proxy_type):
            return ProxyValidationResult(
                is_valid=False,
                protocol_supported=False,
                error_message=f"Unsupported protocol: {config.proxy_type}. Supported: {self.SUPPORTED_PROTOCOLS}",
            )

        try:
            response_time = await self._check_connectivity(config, timeout)
            return ProxyValidationResult(
                is_valid=True,
                protocol_supported=True,
                response_time_ms=response_time,
            )
        except Exception as e:
            return ProxyValidationResult(
                is_valid=False, protocol_supported=True, error_message=str(e)
            )

    async def _check_connectivity(self, config: ProxyConfig, timeout: int) -> float:
        host, port_str = config.server.rsplit(":", 1)
        port = int(port_str)

        start_time = asyncio.get_event_loop().time()

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
        except asyncio.TimeoutError:
            raise Exception(f"Connection timeout after {timeout}s")
        except socket.gaierror as e:
            raise Exception(f"DNS resolution failed: {e}")
        except ConnectionRefusedError:
            raise Exception("Connection refused - proxy may be down")

        end_time = asyncio.get_event_loop().time()
        return (end_time - start_time) * 1000

    def validate_credentials(self, proxy_url: str) -> Tuple[bool, Optional[str]]:
        config = self.parse_proxy_url(proxy_url)
        if not config:
            return False, "Invalid proxy URL"

        if config.username and config.password:
            return True, None

        if config.proxy_type in {"http", "https"} and not config.username:
            return False, "HTTP proxy requires authentication"

        return True, None


async def validate_proxy_endpoint(proxy_url: Optional[str]) -> Dict[str, Any]:
    """FastAPI endpoint handler for proxy validation."""
    if not proxy_url:
        return {"valid": False, "message": "No proxy URL provided"}

    validator = ProxyValidator()
    result = await validator.validate_proxy(proxy_url)

    return {
        "valid": result.is_valid,
        "protocol_supported": result.protocol_supported,
        "response_time_ms": result.response_time_ms,
        "message": result.error_message or "Proxy is valid",
    }
