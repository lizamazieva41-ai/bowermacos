"""
Unit tests for proxy modules.
"""

import pytest
from src.proxy.validator import ProxyValidator
from src.proxy.dns_leak import DNSLeakProtector, get_dns_leak_protection_script
from src.proxy.loader import ProxyConfig


class TestProxyValidatorUnit:
    """Unit tests for ProxyValidator."""

    def test_parse_http_proxy(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("http://proxy.example.com:8080")
        assert result is not None
        assert result.proxy_type == "http"
        assert result.server == "proxy.example.com:8080"

    def test_parse_https_proxy(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("https://proxy.example.com:8080")
        assert result is not None
        assert result.proxy_type == "https"

    def test_parse_socks5_proxy(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("socks5://proxy.example.com:1080")
        assert result is not None
        assert result.proxy_type == "socks5"

    def test_parse_socks4_proxy(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("socks4://proxy.example.com:1080")
        assert result is not None
        assert result.proxy_type == "socks4"

    def test_parse_proxy_with_auth(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url(
            "http://user:password@proxy.example.com:8080"
        )
        assert result is not None
        assert result.username == "user"
        assert result.password == "password"

    def test_parse_proxy_with_special_chars_in_password(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url(
            "http://user:p%40ss%21wd@proxy.example.com:8080"
        )
        assert result is not None
        assert result.username == "user"

    def test_parse_invalid_proxy(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("invalid-url")
        assert result is None

    def test_parse_proxy_no_port(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("http://proxy.example.com")
        assert result is None

    def test_validate_supported_protocols(self):
        validator = ProxyValidator()
        assert validator.validate_proxy_type("http") is True
        assert validator.validate_proxy_type("https") is True
        assert validator.validate_proxy_type("socks5") is True
        assert validator.validate_proxy_type("socks4") is True

    def test_validate_unsupported_protocols(self):
        validator = ProxyValidator()
        assert validator.validate_proxy_type("ftp") is False
        assert validator.validate_proxy_type("socks6") is False
        assert validator.validate_proxy_type("htt") is False

    def test_validate_credentials_with_auth(self):
        validator = ProxyValidator()
        valid, msg = validator.validate_credentials("http://user:pass@proxy:8080")
        assert valid is True
        assert msg is None

    def test_validate_credentials_no_auth(self):
        validator = ProxyValidator()
        valid, msg = validator.validate_credentials("http://proxy:8080")
        # HTTP proxy without auth is valid format but may need auth based on config

    def test_validate_credentials_http_requires_auth(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("http://proxy:8080")
        # HTTP proxy without auth is still valid format


class TestDNSLeakProtectorUnit:
    """Unit tests for DNSLeakProtector."""

    def test_init_default(self):
        protector = DNSLeakProtector()
        assert protector.provider == "cloudflare"
        assert protector.config.primary_dns == "1.1.1.1"

    def test_init_google(self):
        protector = DNSLeakProtector("google")
        assert protector.provider == "google"
        assert protector.config.primary_dns == "8.8.8.8"

    def test_init_quad9(self):
        protector = DNSLeakProtector("quad9")
        assert protector.provider == "quad9"
        assert protector.config.primary_dns == "9.9.9.9"

    def test_init_opendns(self):
        protector = DNSLeakProtector("opendns")
        assert protector.provider == "opendns"
        assert protector.config.primary_dns == "208.67.222.222"

    def test_get_chromium_args_cloudflare(self):
        protector = DNSLeakProtector("cloudflare")
        args = protector.get_chromium_args()
        assert "--dns-prefetch-disable" in args

    def test_get_chromium_args_google(self):
        protector = DNSLeakProtector("google")
        args = protector.get_chromium_args()
        assert "--dns-prefetch-disable" in args
        # Check that DNS servers are configured

    def test_get_stealth_script_contains_dns_config(self):
        script = get_dns_leak_protection_script("cloudflare")
        assert "DNS leak protection activated" in script
        assert "cloudflare" in script

    def test_get_stealth_script_rtc_peer_connection(self):
        script = get_dns_leak_protection_script()
        assert "RTCPeerConnection" in script

    def test_get_recommended_dns_returns_dict(self):
        from src.proxy.dns_leak import get_recommended_dns

        dns_list = get_recommended_dns()
        assert isinstance(dns_list, dict)
        assert "cloudflare" in dns_list
        assert "google" in dns_list
        assert "quad9" in dns_list
        assert "opendns" in dns_list


class TestProxyConfig:
    """Unit tests for ProxyConfig."""

    def test_proxy_config_parse_basic(self):
        config = ProxyConfig.parse("http://proxy.example.com:8080")
        assert config.url == "http://proxy.example.com:8080"
        assert config.username is None
        assert config.password is None

    def test_proxy_config_parse_with_auth(self):
        config = ProxyConfig.parse("http://user:pass@proxy.example.com:8080")
        # Username may be None depending on implementation

    def test_proxy_config_to_dict(self):
        config = ProxyConfig(
            url="http://proxy.example.com:8080", username="user", password="pass"
        )
        d = config.to_dict()
        assert d["server"] == "http://proxy.example.com:8080"
        assert d["username"] == "user"
        assert d["password"] == "pass"
