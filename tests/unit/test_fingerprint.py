"""
Test fingerprint generator.
"""
import pytest
from src.browser.fingerprint import (
    FingerprintGenerator,
    BrowserFingerprint,
    USER_AGENTS,
    PLATFORMS,
)


def test_fingerprint_generation():
    """Test basic fingerprint generation."""
    fp = FingerprintGenerator.generate()
    assert fp.user_agent is not None
    assert fp.platform in PLATFORMS.values()
    assert len(fp.languages) > 0
    assert fp.timezone is not None


def test_fingerprint_platform_specific():
    """Test fingerprint generation for specific platform."""
    fp = FingerprintGenerator.generate(platform="windows")
    assert "Windows" in fp.user_agent
    assert fp.platform == "Win32"


def test_fingerprint_dict_output():
    """Test fingerprint as dictionary."""
    fp_dict = FingerprintGenerator.generate_dict()
    assert "user_agent" in fp_dict
    assert "platform" in fp_dict
    assert "timezone" in fp_dict
    assert isinstance(fp_dict["languages"], list)


def test_fingerprint_use_case():
    """Test fingerprint generation for specific use case."""
    fp_dict = FingerprintGenerator.generate_for_profile("shopping")
    assert "user_agent" in fp_dict
    assert any(browser in fp_dict["user_agent"] for browser in ["Chrome", "Safari", "Firefox"])


def test_fingerprint_export_import():
    """Test fingerprint export and import."""
    fp = FingerprintGenerator.generate()
    json_str = FingerprintGenerator.export_fingerprint(fp)
    
    imported_fp = FingerprintGenerator.import_fingerprint(json_str)
    assert imported_fp.user_agent == fp.user_agent
    assert imported_fp.platform == fp.platform
    assert imported_fp.timezone == fp.timezone


def test_multiple_fingerprints_unique():
    """Test that multiple fingerprints are unique."""
    fps = [FingerprintGenerator.generate() for _ in range(10)]
    uas = [fp.user_agent for fp in fps]
    assert len(set(uas)) > 1


def test_platform_selection():
    """Test all platform options."""
    for platform in ["windows", "macos", "linux", "android", "ios"]:
        fp = FingerprintGenerator.generate(platform=platform)
        assert fp is not None
        assert fp.platform in PLATFORMS.values()
