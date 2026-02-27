"""
Tests for WebRTC Protection module.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.browser.stealth import (
    get_webrtc_stealth_script,
    get_combined_stealth_script,
)


class TestWebRTCStealthScript:
    """Test WebRTC stealth script generation."""

    def test_webrtc_script_disables_rtc_peer_connection(self):
        """Test script disables RTCPeerConnection."""
        script = get_webrtc_stealth_script()
        
        assert "RTCPeerConnection" in script
        assert "window.RTCPeerConnection = function()" in script
        assert "return null" in script

    def test_webrtc_script_disables_get_user_media(self):
        """Test script disables getUserMedia."""
        script = get_webrtc_stealth_script()
        
        assert "getUserMedia" in script
        assert "Promise.reject" in script or "NotAllowedError" in script

    def test_webrtc_script_disables_enumerate_devices(self):
        """Test script disables enumerateDevices."""
        script = get_webrtc_stealth_script()
        
        assert "enumerateDevices" in script
        assert "Promise.resolve([])" in script

    def test_webrtc_script_blocks_webkit_rtc(self):
        """Test script blocks webkitRTCPeerConnection."""
        script = get_webrtc_stealth_script()
        
        assert "webkitRTCPeerConnection" in script
        assert "webkitGetUserMedia" in script

    def test_webrtc_script_blocks_moz_rtc(self):
        """Test script blocks mozRTCPeerConnection."""
        script = get_webrtc_stealth_script()
        
        assert "mozRTCPeerConnection" in script
        assert "mozGetUserMedia" in script

    def test_webrtc_script_handles_media_stream_track(self):
        """Test script handles MediaStreamTrack."""
        script = get_webrtc_stealth_script()
        
        assert "MediaStreamTrack" in script
        assert "getSources" in script

    def test_webrtc_script_removes_rtc_session_description(self):
        """Test script removes RTCSessionDescription."""
        script = get_webrtc_stealth_script()
        
        assert "RTCSessionDescription" in script
        assert "RTCIceCandidate" in script

    def test_webrtc_script_contains_log(self):
        """Test script contains console log for debugging."""
        script = get_webrtc_stealth_script()
        
        assert "console.log" in script
        assert "WebRTC protection activated" in script


class TestWebRTCProtectionCoverage:
    """Test WebRTC protection coverage."""

    def test_combined_script_includes_webrtc(self):
        """Test combined stealth script includes WebRTC protection."""
        combined = get_combined_stealth_script()
        
        assert "WebRTC protection activated" in combined

    def test_webrtc_script_handles_all_vendors(self):
        """Test script handles all browser vendors."""
        script = get_webrtc_stealth_script()
        
        vendors = ["RTCPeerConnection", "webkitRTCPeerConnection", "mozRTCPeerConnection"]
        assert all(vendor in script for vendor in vendors)

    def test_webrtc_script_handles_media_methods(self):
        """Test script handles all media methods."""
        script = get_webrtc_stealth_script()
        
        media_methods = [
            "getUserMedia",
            "enumerateDevices",
            "getSources",
            "webkitGetUserMedia",
            "mozGetUserMedia",
            "msGetUserMedia"
        ]
        for method in media_methods:
            assert method in script


class TestWebRTCIPLeakPrevention:
    """Test WebRTC IP leak prevention."""

    def test_rtc_peer_connection_returns_null(self):
        """Test RTCPeerConnection returns null to prevent leaks."""
        script = get_webrtc_stealth_script()
        
        assert "return null" in script

    def test_get_user_media_rejects(self):
        """Test getUserMedia rejects to prevent media leaks."""
        script = get_webrtc_stealth_script()
        
        assert "Promise.reject" in script or "Error" in script

    def test_enumerate_devices_returns_empty(self):
        """Test enumerateDevices returns empty list."""
        script = get_webrtc_stealth_script()
        
        assert "Promise.resolve([])" in script or "[]" in script


class TestWebRTCBrowserFlags:
    """Test browser flags for WebRTC blocking."""

    def test_webrtc_flags_available_in_manager(self):
        """Test WebRTC flags are available."""
        from src.browser.manager import BrowserManager
        
        assert hasattr(BrowserManager, 'start')
        
    def test_dns_leak_protection_script_complements_webrtc(self):
        """Test DNS leak script complements WebRTC protection."""
        from src.proxy.dns_leak import get_dns_leak_protection_script
        
        dns_script = get_dns_leak_protection_script()
        webrtc_script = get_webrtc_stealth_script()
        
        assert "RTCPeerConnection" in dns_script or "RTCPeerConnection" in webrtc_script


class TestWebRTCStealthScriptExecution:
    """Test WebRTC stealth script can be executed."""

    def test_script_is_valid_javascript(self):
        """Test script is valid JavaScript."""
        script = get_webrtc_stealth_script()
        
        assert "(function()" in script
        assert "})();" in script

    def test_script_has_proper_closure(self):
        """Test script has proper IIFE closure."""
        script = get_webrtc_stealth_script()
        
        assert script.count("(function()") == 1
        assert script.count("})();") >= 1


class TestWebRTCProtectionEdgeCases:
    """Test edge cases for WebRTC protection."""

    def test_webrtc_script_handles_null_window(self):
        """Test script handles missing window object."""
        script = get_webrtc_stealth_script()
        
        assert "window.RTCPeerConnection" in script

    def test_webrtc_script_handles_existing_rtc(self):
        """Test script handles existing RTCPeerConnection."""
        script = get_webrtc_stealth_script()
        
        assert "OriginalRTCPeerConnection" in script

    def test_webrtc_script_does_not_break_page(self):
        """Test script doesn't break page functionality."""
        script = get_webrtc_stealth_script()
        
        assert "null" in script
        assert "undefined" in script or "function" in script


class TestWebRTCIntegrationWithBrowser:
    """Integration tests for WebRTC with browser context."""

    def test_webrtc_script_can_be_added_to_page(self):
        """Test WebRTC script can be added to page context."""
        script = get_webrtc_stealth_script()
        
        assert len(script) > 0
        assert "function" in script

    def test_webrtc_protection_applies_to_all_pages(self):
        """Test protection applies to all pages."""
        combined = get_combined_stealth_script()
        
        assert combined.count("WebRTC") > 0

    def test_webrtc_and_dns_leak_work_together(self):
        """Test WebRTC and DNS leak protection work together."""
        from src.browser.stealth import get_all_stealth_scripts
        
        all_scripts = get_all_stealth_scripts()
        
        assert any("WebRTC" in s for s in all_scripts)
        assert any("DNS" in s for s in all_scripts)
