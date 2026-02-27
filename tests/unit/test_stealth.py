"""
Test stealth features.
"""
import pytest
from src.browser.stealth import (
    get_stealth_script,
    get_webgl_stealth_script,
    get_canvas_stealth_script,
    get_webrtc_stealth_script,
    get_audio_stealth_script,
    get_font_stealth_script,
    get_combined_stealth_script,
)


def test_stealth_script_generation():
    """Test that stealth scripts are generated."""
    script = get_stealth_script()
    assert "navigator" in script and "webdriver" in script
    assert "plugins" in script
    assert "languages" in script


def test_webgl_stealth_script():
    """Test WebGL stealth script generation."""
    script = get_webgl_stealth_script()
    assert "getParameter" in script
    assert "WEBGL_debug_renderer_info" in script


def test_canvas_stealth_script():
    """Test Canvas stealth script generation."""
    script = get_canvas_stealth_script()
    assert "toDataURL" in script
    assert "HTMLCanvasElement" in script


def test_webrtc_stealth_script():
    """Test WebRTC stealth script generation."""
    script = get_webrtc_stealth_script()
    assert "RTCPeerConnection" in script
    assert "getUserMedia" in script


def test_audio_stealth_script():
    """Test AudioContext stealth script generation."""
    script = get_audio_stealth_script()
    assert "AudioContext" in script
    assert "createAnalyser" in script


def test_font_stealth_script():
    """Test Font stealth script generation."""
    script = get_font_stealth_script()
    assert "getComputedStyle" in script


def test_combined_stealth_script():
    """Test combined stealth script."""
    script = get_combined_stealth_script()
    assert len(script) > 1000
    assert "navigator" in script and "webdriver" in script
    assert "RTCPeerConnection" in script
    assert "toDataURL" in script
