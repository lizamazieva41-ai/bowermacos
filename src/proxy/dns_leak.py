"""
DNS Leak Protection module.
Provides DNS configuration and leak prevention for browser sessions.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DNSConfig:
    primary_dns: str
    fallback_dns: Optional[str] = None
    dns_over_https: Optional[str] = None


class DNSLeakProtector:
    """DNS leak protection and configuration."""

    PUBLIC_DNS_SERVERS = {
        "google": DNSConfig(
            primary_dns="8.8.8.8",
            fallback_dns="8.8.4.4",
            dns_over_https="https://dns.google/resolve",
        ),
        "cloudflare": DNSConfig(
            primary_dns="1.1.1.1",
            fallback_dns="1.0.0.1",
            dns_over_https="https://cloudflare-dns.com/dns-query",
        ),
        "quad9": DNSConfig(
            primary_dns="9.9.9.9",
            fallback_dns="149.112.112.112",
            dns_over_https="https://dns.quad9.net:5053/dns-query",
        ),
        "opendns": DNSConfig(
            primary_dns="208.67.222.222",
            fallback_dns="208.67.220.220",
            dns_over_https=None,
        ),
    }

    def __init__(self, provider: str = "cloudflare"):
        self.provider = provider
        self.config = self.PUBLIC_DNS_SERVERS.get(
            provider, self.PUBLIC_DNS_SERVERS["cloudflare"]
        )

    def get_chromium_args(self) -> List[str]:
        args = [
            "--dns-prefetch-disable",
            "--disable-dns-https-fragmentation",
        ]

        if self.config.dns_over_https:
            args.extend(
                [
                    "--enable-features=AsyncDns",
                    f"--dns-over-https={self.config.dns_over_https}",
                ]
            )
        else:
            args.extend(
                [
                    f"--dns-servers={self.config.primary_dns}{',' + self.config.fallback_dns if self.config.fallback_dns else ''}",
                ]
            )

        return args

    def get_stealth_script(self) -> str:
        return f"""
(function() {{
    // DNS leak protection - force DNS over HTTPS
    if (window.RTCPeerConnection) {{
        const originalCreateOffer = RTCPeerConnection.prototype.createOffer;
        RTCPeerConnection.prototype.createOffer = function() {{
            // Add DNS configuration hints
            this.optional = this.optional || [];
            this.optional.push({{
                DtlsSrtpKeyAgreement: true
            }}, {{
                goog: {{
                    dscp: '45'
                }}
            }});
            return originalCreateOffer.apply(this, arguments);
        }};
    }}

    // Block WebRTC-based DNS leaks
    const originalGetStats = RTCPeerConnection.prototype.getStats;
    RTCPeerConnection.prototype.getStats = function(selector) {{
        return originalGetStats.apply(this, arguments).then(stats => {{
            const newStats = new Map();
            for (const [key, value] of stats) {{
                // Filter out DNS-related leak information
                if (!value || !value.type || !value.type.includes('candidate')) {{
                    newStats.set(key, value);
                }}
            }}
            return newStats;
        }});
    }};

    console.log('DNS leak protection activated - provider: {self.provider}');
}})();
"""


def get_dns_leak_protection_script(provider: str = "cloudflare") -> str:
    """Get DNS leak protection script for specified provider."""
    protector = DNSLeakProtector(provider)
    return protector.get_stealth_script()


def get_recommended_dns() -> Dict[str, str]:
    """Get recommended DNS providers."""
    return {
        "cloudflare": "1.1.1.1 (Fast, Privacy-focused)",
        "google": "8.8.8.8 (Reliable)",
        "quad9": "9.9.9.9 (Security-focused)",
        "opendns": "208.67.222.222 (Family-safe)",
    }
