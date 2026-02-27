"""
Fingerprint generator module.
Generates random but realistic browser fingerprints.
"""

import random
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class BrowserFingerprint:
    """Complete browser fingerprint."""

    user_agent: str
    platform: str
    vendor: str
    languages: List[str]
    timezone: str
    screen_resolution: str
    color_depth: int
    hardware_concurrency: int
    device_memory: int
    webgl_vendor: str
    webgl_renderer: str
    plugins: List[str]


USER_AGENTS = {
    "windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ],
    "macos": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ],
    "linux": [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ],
    "android": [
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    ],
    "ios": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ],
}

PLATFORMS = {
    "windows": "Win32",
    "macos": "MacIntel",
    "linux": "Linux x86_64",
    "android": "Linux arm64",
    "ios": "iPhone",
}

VENDORS = {
    "windows": "Google Inc.",
    "macos": "Apple Computer, Inc.",
    "linux": "Google Inc.",
    "android": "Google Inc.",
    "ios": "Apple Inc.",
}

LANGUAGES = [
    ["en-US", "en"],
    ["en-GB", "en"],
    ["en-AU", "en"],
    ["en-CA", "en"],
    ["es-ES", "es"],
    ["fr-FR", "fr"],
    ["de-DE", "de"],
    ["it-IT", "it"],
    ["pt-BR", "pt"],
    ["ja-JP", "ja"],
    ["ko-KR", "ko"],
    ["zh-CN", "zh"],
    ["ru-RU", "ru"],
]

TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "America/Vancouver",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Asia/Tokyo",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "Australia/Sydney",
    "Pacific/Auckland",
]

SCREEN_RESOLUTIONS = [
    "1920x1080",
    "2560x1440",
    "1366x768",
    "1536x864",
    "1440x900",
    "1280x720",
    "3840x2160",
    "2560x1080",
]

WEBGL_VENDORS = [
    "Google Inc.",
    "Intel Inc.",
    "NVIDIA Corporation",
    "AMD",
    "Apple Inc.",
]

WEBGL_RENDERERS = [
    "ANGLE (Intel, Intel Iris OpenGL Renderer)",
    "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080)",
    "ANGLE (AMD, AMD Radeon Pro 5500M)",
    "Intel Iris Pro Graphics",
    "Apple M1",
    "Intel Iris OpenGL Engine",
    "NVIDIA GeForce GTX 1080",
    "AMD Radeon Pro 5300M",
]

PLUGINS = [
    "PDF Viewer",
    "Chrome PDF Viewer",
    "Native Client",
]


class FingerprintGenerator:
    """Generate random browser fingerprints."""

    @staticmethod
    def generate(
        platform: Optional[str] = None,
        custom_ua: Optional[str] = None,
    ) -> BrowserFingerprint:
        """
        Generate a random browser fingerprint.

        Args:
            platform: Specific platform (windows/macos/linux/android/ios) or None for random
            custom_ua: Custom User-Agent string

        Returns:
            BrowserFingerprint object
        """
        if platform is None:
            platform = random.choice(list(USER_AGENTS.keys()))

        if custom_ua:
            user_agent = custom_ua
        else:
            user_agent = random.choice(
                USER_AGENTS.get(platform, USER_AGENTS["windows"])
            )

        languages = random.choice(LANGUAGES)

        return BrowserFingerprint(
            user_agent=user_agent,
            platform=PLATFORMS.get(platform, PLATFORMS["windows"]),
            vendor=VENDORS.get(platform, VENDORS["windows"]),
            languages=languages,
            timezone=random.choice(TIMEZONES),
            screen_resolution=random.choice(SCREEN_RESOLUTIONS),
            color_depth=random.choice([24, 32]),
            hardware_concurrency=random.choice([4, 8, 12, 16]),
            device_memory=random.choice([4, 8, 16]),
            webgl_vendor=random.choice(WEBGL_VENDORS),
            webgl_renderer=random.choice(WEBGL_RENDERERS),
            plugins=PLUGINS,
        )

    @staticmethod
    def generate_dict(
        platform: Optional[str] = None,
        custom_ua: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate fingerprint as dictionary."""
        fp = FingerprintGenerator.generate(platform, custom_ua)
        return {
            "user_agent": fp.user_agent,
            "platform": fp.platform,
            "vendor": fp.vendor,
            "languages": fp.languages,
            "timezone": fp.timezone,
            "screen_resolution": fp.screen_resolution,
            "color_depth": fp.color_depth,
            "hardware_concurrency": fp.hardware_concurrency,
            "device_memory": fp.device_memory,
            "webgl_vendor": fp.webgl_vendor,
            "webgl_renderer": fp.webgl_renderer,
            "plugins": fp.plugins,
        }

    @staticmethod
    def generate_for_profile(use_case: str = "general") -> Dict[str, Any]:
        """
        Generate fingerprint based on use case.

        Args:
            use_case: One of general, shopping, social, scraping, streaming
        """
        platform_mapping = {
            "general": None,
            "shopping": random.choice(["windows", "macos"]),
            "social": random.choice(["windows", "macos", "android"]),
            "scraping": random.choice(["windows", "linux"]),
            "streaming": random.choice(["windows", "macos"]),
        }

        platform = platform_mapping.get(use_case)
        return FingerprintGenerator.generate_dict(platform=platform)

    @staticmethod
    def export_fingerprint(fp: BrowserFingerprint) -> str:
        """Export fingerprint to JSON string."""
        return json.dumps(
            {
                "user_agent": fp.user_agent,
                "platform": fp.platform,
                "vendor": fp.vendor,
                "languages": fp.languages,
                "timezone": fp.timezone,
                "screen_resolution": fp.screen_resolution,
                "color_depth": fp.color_depth,
                "hardware_concurrency": fp.hardware_concurrency,
                "device_memory": fp.device_memory,
                "webgl_vendor": fp.webgl_vendor,
                "webgl_renderer": fp.webgl_renderer,
                "plugins": fp.plugins,
            },
            indent=2,
        )

    @staticmethod
    def import_fingerprint(json_str: str) -> BrowserFingerprint:
        """Import fingerprint from JSON string."""
        data = json.loads(json_str)
        return BrowserFingerprint(**data)
