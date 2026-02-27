"""
Integration tests for Phase 3 features.
"""
import pytest
from src.api.auth import create_access_token, verify_token, generate_api_key, verify_api_key
from src.proxy.validator import ProxyValidator
from src.proxy.dns_leak import DNSLeakProtector, get_dns_leak_protection_script


class TestAuthModule:
    """Test JWT authentication module."""

    def test_create_access_token(self):
        token = create_access_token({"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_verify_token_valid(self):
        token = create_access_token({"sub": "testuser"})
        token_data = verify_token(token)
        assert token_data.sub == "testuser"

    def test_verify_token_invalid(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_token")
        assert exc_info.value.status_code == 401

    def test_generate_api_key(self):
        key = generate_api_key("test_key")
        assert key is not None
        assert len(key) > 20

    def test_verify_api_key_valid(self):
        key = generate_api_key("test_key")
        assert verify_api_key(key) is True

    def test_verify_api_key_invalid(self):
        assert verify_api_key("nonexistent_key") is False


class TestProxyValidator:
    """Test proxy validation."""

    def test_parse_proxy_url_http(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("http://proxy.example.com:8080")
        assert result is not None
        assert result.proxy_type == "http"
        assert result.server == "proxy.example.com:8080"

    def test_parse_proxy_url_with_auth(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("http://user:pass@proxy.example.com:8080")
        assert result is not None
        assert result.username == "user"
        assert result.password == "pass"

    def test_parse_proxy_url_socks5(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("socks5://proxy.example.com:1080")
        assert result is not None
        assert result.proxy_type == "socks5"

    def test_parse_proxy_url_invalid(self):
        validator = ProxyValidator()
        result = validator.parse_proxy_url("invalid_url")
        assert result is None

    def test_validate_proxy_type_supported(self):
        validator = ProxyValidator()
        assert validator.validate_proxy_type("http") is True
        assert validator.validate_proxy_type("socks5") is True
        assert validator.validate_proxy_type("https") is True

    def test_validate_proxy_type_unsupported(self):
        validator = ProxyValidator()
        assert validator.validate_proxy_type("ftp") is False


class TestDNSLeakProtector:
    """Test DNS leak protection."""

    def test_dns_protector_init(self):
        protector = DNSLeakProtector("cloudflare")
        assert protector.provider == "cloudflare"
        assert protector.config.primary_dns == "1.1.1.1"

    def test_dns_protector_google(self):
        protector = DNSLeakProtector("google")
        assert protector.config.primary_dns == "8.8.8.8"

    def test_get_chromium_args(self):
        protector = DNSLeakProtector("cloudflare")
        args = protector.get_chromium_args()
        assert "--dns-prefetch-disable" in args

    def test_get_stealth_script(self):
        script = get_dns_leak_protection_script("cloudflare")
        assert "DNS leak protection activated" in script
        assert "cloudflare" in script

    def test_get_recommended_dns(self):
        from src.proxy.dns_leak import get_recommended_dns
        dns_list = get_recommended_dns()
        assert "cloudflare" in dns_list
        assert "google" in dns_list
