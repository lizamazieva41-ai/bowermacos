"""
Tests for DNS Leak Protection module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.proxy.dns_leak import (
    DNSLeakProtector,
    DNSConfig,
    get_dns_leak_protection_script,
    get_recommended_dns,
)


class TestDNSLeakProtector:
    """Test DNS Leak Protector class."""

    def test_init_cloudflare(self):
        """Test initialization with cloudflare provider."""
        protector = DNSLeakProtector("cloudflare")
        assert protector.provider == "cloudflare"
        assert protector.config.primary_dns == "1.1.1.1"
        assert protector.config.fallback_dns == "1.0.0.1"

    def test_init_google(self):
        """Test initialization with google provider."""
        protector = DNSLeakProtector("google")
        assert protector.provider == "google"
        assert protector.config.primary_dns == "8.8.8.8"
        assert protector.config.fallback_dns == "8.8.4.4"

    def test_init_quad9(self):
        """Test initialization with quad9 provider."""
        protector = DNSLeakProtector("quad9")
        assert protector.provider == "quad9"
        assert protector.config.primary_dns == "9.9.9.9"

    def test_init_opendns(self):
        """Test initialization with opendns provider."""
        protector = DNSLeakProtector("opendns")
        assert protector.provider == "opendns"
        assert protector.config.primary_dns == "208.67.222.222"

    def test_init_unknown_provider_fallbacks_to_cloudflare(self):
        """Test unknown provider falls back to cloudflare."""
        protector = DNSLeakProtector("unknown_provider")
        assert protector.provider == "unknown_provider"
        assert protector.config.primary_dns == "1.1.1.1"

    def test_get_chromium_args_cloudflare(self):
        """Test chromium arguments for cloudflare."""
        protector = DNSLeakProtector("cloudflare")
        args = protector.get_chromium_args()
        
        assert "--dns-prefetch-disable" in args
        assert "--disable-dns-https-fragmentation" in args
        assert "--enable-features=AsyncDns" in args
        assert "--dns-over-https=https://cloudflare-dns.com/dns-query" in args

    def test_get_chromium_args_google(self):
        """Test chromium arguments for google."""
        protector = DNSLeakProtector("google")
        args = protector.get_chromium_args()
        
        assert "--dns-over-https=https://dns.google/resolve" in args

    def test_get_chromium_args_opendns(self):
        """Test chromium arguments for opendns (no DoH)."""
        protector = DNSLeakProtector("opendns")
        args = protector.get_chromium_args()
        
        assert "--dns-servers=208.67.222.222,208.67.220.220" in args

    def test_get_stealth_script(self):
        """Test stealth script generation."""
        protector = DNSLeakProtector("cloudflare")
        script = protector.get_stealth_script()
        
        assert "DNS leak protection" in script
        assert "RTCPeerConnection" in script
        assert "cloudflare" in script

    def test_get_stealth_script_contains_dns_config(self):
        """Test stealth script contains DNS configuration."""
        protector = DNSLeakProtector("google")
        script = protector.get_stealth_script()
        
        assert "DtlsSrtpKeyAgreement" in script
        assert "goog" in script

    def test_dns_config_dataclass(self):
        """Test DNSConfig dataclass."""
        config = DNSConfig(
            primary_dns="8.8.8.8",
            fallback_dns="8.8.4.4",
            dns_over_https="https://dns.google/resolve"
        )
        
        assert config.primary_dns == "8.8.8.8"
        assert config.fallback_dns == "8.8.4.4"
        assert config.dns_over_https == "https://dns.google/resolve"


class TestDNSCryptScripts:
    """Test DNS leak protection script generation functions."""

    def test_get_dns_leak_protection_script_default(self):
        """Test default DNS leak protection script."""
        script = get_dns_leak_protection_script()
        
        assert "function" in script
        assert "RTCPeerConnection" in script

    def test_get_dns_leak_protection_script_cloudflare(self):
        """Test cloudflare DNS leak protection script."""
        script = get_dns_leak_protection_script("cloudflare")
        
        assert "cloudflare" in script

    def test_get_dns_leak_protection_script_google(self):
        """Test google DNS leak protection script."""
        script = get_dns_leak_protection_script("google")
        
        assert "google" in script

    def test_get_recommended_dns(self):
        """Test recommended DNS providers."""
        dns = get_recommended_dns()
        
        assert "cloudflare" in dns
        assert "google" in dns
        assert "quad9" in dns
        assert "opendns" in dns
        assert "1.1.1.1" in dns["cloudflare"]
        assert "8.8.8.8" in dns["google"]


class TestDNSLeakPrevention:
    """Test DNS leak prevention in browser context."""

    @pytest.mark.asyncio
    async def test_dns_leak_protection_script_blocks_rtc(self):
        """Test that DNS leak script blocks RTC DNS leaks."""
        script = get_dns_leak_protection_script("cloudflare")
        
        assert "RTCPeerConnection.prototype.createOffer" in script
        assert "getStats" in script

    def test_chromium_args_prevent_dns_prefetch(self):
        """Test chromium args prevent DNS prefetch."""
        protector = DNSLeakProtector()
        args = protector.get_chromium_args()
        
        assert any("--dns" in arg for arg in args)

    def test_dns_over_https_enabled_by_default(self):
        """Test DoH is enabled by default."""
        protector = DNSLeakProtector()
        
        assert protector.config.dns_over_https is not None
        assert "cloudflare" in protector.config.dns_over_https.lower()


class TestDNSLeakIntegration:
    """Integration tests for DNS leak protection."""

    def test_all_public_dns_providers_available(self):
        """Test all public DNS providers are available."""
        providers = ["cloudflare", "google", "quad9", "opendns"]
        
        for provider in providers:
            protector = DNSLeakProtector(provider)
            assert protector.config is not None
            assert protector.config.primary_dns is not None

    def test_dns_config_consistency(self):
        """Test DNS configs are consistent."""
        cloudflare = DNSLeakProtector("cloudflare").config
        google = DNSLeakProtector("google").config
        
        assert cloudflare.primary_dns != google.primary_dns
        assert cloudflare.dns_over_https != google.dns_over_https
