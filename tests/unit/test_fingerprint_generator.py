"""
Unit tests for fingerprint generator module.
"""

import pytest
from src.browser.fingerprint import (
    FingerprintGenerator,
    BrowserFingerprint,
    FINGERPRINT_TEMPLATES,
    CANVAS_FINGERPRINTS,
    AUDIO_FINGERPRINTS,
)


class TestFingerprintGenerator:
    """Unit tests for FingerprintGenerator class."""

    def test_generate_fingerprint(self):
        """Test generating a basic fingerprint."""
        fp = FingerprintGenerator.generate(platform="windows")

        assert fp is not None
        assert fp.user_agent is not None
        assert fp.platform == "Win32"
        assert fp.vendor == "Google Inc."

    def test_generate_random_platform(self):
        """Test generating fingerprint with random platform."""
        fp = FingerprintGenerator.generate()

        assert fp is not None
        assert fp.platform in ["Win32", "MacIntel", "Linux x86_64", "Linux arm64", "iPhone"]

    def test_generate_dict(self):
        """Test generating fingerprint as dictionary."""
        fp_dict = FingerprintGenerator.generate_dict(platform="macos")

        assert isinstance(fp_dict, dict)
        assert "user_agent" in fp_dict
        assert "platform" in fp_dict
        assert fp_dict["platform"] == "MacIntel"

    def test_generate_for_profile_general(self):
        """Test generating fingerprint for general use case."""
        fp_dict = FingerprintGenerator.generate_for_profile("general")

        assert fp_dict is not None
        assert "canvas_mode" in fp_dict
        assert "audio_mode" in fp_dict

    def test_generate_for_profile_shopping(self):
        """Test generating fingerprint for shopping."""
        fp_dict = FingerprintGenerator.generate_for_profile("shopping")

        assert fp_dict is not None
        assert fp_dict["canvas_mode"] in ["noise", "block", "redirect"]

    def test_generate_for_profile_anti_bot(self):
        """Test generating fingerprint for anti-bot."""
        fp_dict = FingerprintGenerator.generate_for_profile("anti_bot")

        assert fp_dict is not None
        assert fp_dict["canvas_mode"] in CANVAS_FINGERPRINTS.keys()

    def test_generate_for_profile_high_security(self):
        """Test generating fingerprint for high security."""
        fp_dict = FingerprintGenerator.generate_for_profile("high_security")

        assert fp_dict is not None

    def test_fingerprint_templates(self):
        """Test fingerprint templates exist."""
        assert "general" in FINGERPRINT_TEMPLATES
        assert "shopping" in FINGERPRINT_TEMPLATES
        assert "social" in FINGERPRINT_TEMPLATES
        assert "scraping" in FINGERPRINT_TEMPLATES
        assert "streaming" in FINGERPRINT_TEMPLATES
        assert "anti_bot" in FINGERPRINT_TEMPLATES
        assert "high_security" in FINGERPRINT_TEMPLATES

    def test_generate_canvas_spoofing_script(self):
        """Test generating canvas spoofing script."""
        script = FingerprintGenerator.generate_canvas_spofing_script("noise")

        assert script is not None
        assert "canvas" in script.lower() or "Canvas" in script

    def test_generate_canvas_block_script(self):
        """Test generating canvas block script."""
        script = FingerprintGenerator.generate_canvas_spofing_script("block")

        assert script is not None
        assert "DOMException" in script or "getImageData" in script

    def test_generate_audio_spoofing_script(self):
        """Test generating audio spoofing script."""
        script = FingerprintGenerator.generate_audio_spofing_script("noise")

        assert script is not None
        assert "audio" in script.lower() or "AudioContext" in script

    def test_export_fingerprint(self):
        """Test exporting fingerprint to JSON."""
        fp = FingerprintGenerator.generate(platform="windows")
        json_str = FingerprintGenerator.export_fingerprint(fp)

        assert json_str is not None
        assert "user_agent" in json_str
        assert "platform" in json_str

    def test_import_fingerprint(self):
        """Test importing fingerprint from JSON."""
        fp = FingerprintGenerator.generate(platform="windows")
        json_str = FingerprintGenerator.export_fingerprint(fp)
        imported_fp = FingerprintGenerator.import_fingerprint(json_str)

        assert isinstance(imported_fp, BrowserFingerprint)
        assert imported_fp.user_agent == fp.user_agent
        assert imported_fp.platform == fp.platform

    def test_custom_user_agent(self):
        """Test generating fingerprint with custom user agent."""
        custom_ua = "Mozilla/5.0 (Custom Browser) Custom/1.0"
        fp = FingerprintGenerator.generate(custom_ua=custom_ua)

        assert fp.user_agent == custom_ua

    def test_fonts_generation(self):
        """Test font generation."""
        fp = FingerprintGenerator.generate(platform="windows", use_fonts="common")

        assert fp.fonts is not None
        assert len(fp.fonts) >= 5


class TestBrowserFingerprint:
    """Unit tests for BrowserFingerprint dataclass."""

    def test_fingerprint_creation(self):
        """Test creating a BrowserFingerprint."""
        fp = BrowserFingerprint(
            user_agent="Mozilla/5.0 Test",
            platform="Win32",
            vendor="Google Inc.",
            languages=["en-US", "en"],
            timezone="America/New_York",
            screen_resolution="1920x1080",
            color_depth=24,
            hardware_concurrency=8,
            device_memory=8,
            webgl_vendor="Google Inc.",
            webgl_renderer="ANGLE",
            plugins=["PDF Viewer"],
            canvas_mode="noise",
            audio_mode="noise",
            fonts=["Arial", "Helvetica"],
        )

        assert fp.user_agent == "Mozilla/5.0 Test"
        assert fp.platform == "Win32"
        assert fp.canvas_mode == "noise"

    def test_fingerprint_defaults(self):
        """Test fingerprint default values."""
        fp = BrowserFingerprint(
            user_agent="Test",
            platform="Win32",
            vendor="Test",
            languages=["en"],
            timezone="UTC",
            screen_resolution="1920x1080",
            color_depth=24,
            hardware_concurrency=4,
            device_memory=4,
            webgl_vendor="Test",
            webgl_renderer="Test",
            plugins=[],
        )

        assert fp.canvas_mode == "noise"
        assert fp.audio_mode == "noise"
        assert fp.do_not_track is False
