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
    canvas_mode: str = "noise"
    audio_mode: str = "noise"
    fonts: List[str] = None
    do_not_track: bool = False
    hardware_concurrency_cores: int = 0


USER_AGENTS = {
    "windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ],
    "macos": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ],
    "linux": [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ],
    "android": [
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    ],
    "ios": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    ],
}

CANVAS_FINGERPRINTS = {
    "noise": {
        "method": "noise",
        "description": "Adds random noise to canvas operations",
    },
    "block": {
        "method": "block",
        "description": "Blocks canvas readback",
    },
    "redirect": {
        "method": "redirect",
        "description": "Redirects to offscreen canvas",
    },
}

AUDIO_FINGERPRINTS = {
    "noise": {
        "method": "noise",
        "description": "Adds random noise to audio context",
    },
    "block": {
        "method": "block",
        "description": "Blocks audio context channel data",
    },
    "fake": {
        "method": "fake",
        "description": "Returns fake audio data",
    },
}

FINGERPRINT_TEMPLATES = {
    "general": {
        "platform": None,
        "canvas_mode": "noise",
        "audio_mode": "noise",
        "do_not_track": False,
    },
    "shopping": {
        "platform": random.choice(["windows", "macos"]),
        "canvas_mode": "noise",
        "audio_mode": "noise",
        "do_not_track": True,
    },
    "social": {
        "platform": random.choice(["windows", "macos", "android"]),
        "canvas_mode": "noise",
        "audio_mode": "block",
        "do_not_track": False,
    },
    "scraping": {
        "platform": random.choice(["windows", "linux"]),
        "canvas_mode": "block",
        "audio_mode": "block",
        "do_not_track": True,
    },
    "streaming": {
        "platform": random.choice(["windows", "macos"]),
        "canvas_mode": "noise",
        "audio_mode": "fake",
        "do_not_track": False,
    },
    "anti_bot": {
        "platform": random.choice(["windows", "macos"]),
        "canvas_mode": "redirect",
        "audio_mode": "noise",
        "do_not_track": True,
    },
    "high_security": {
        "platform": random.choice(["windows", "linux"]),
        "canvas_mode": "redirect",
        "audio_mode": "block",
        "do_not_track": True,
    },
}


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

    COMMON_FONTS = [
        "Arial",
        "Helvetica",
        "Times New Roman",
        "Courier New",
        "Verdana",
        "Georgia",
        "Palatino",
        "Garamond",
        "Bookman",
        "Comic Sans MS",
        "Trebuchet MS",
        "Arial Black",
        "Impact",
    ]

    EXTENDED_FONTS = [
        "Microsoft YaHei",
        "SimSun",
        "SimHei",
        "Malgun Gothic",
        "NanumGothic",
        "MingLiU",
        "PMingLiU",
        "Arial Unicode MS",
    ]

    @staticmethod
    def generate(
        platform: Optional[str] = None,
        custom_ua: Optional[str] = None,
        canvas_mode: str = "noise",
        audio_mode: str = "noise",
        use_fonts: str = "common",
    ) -> BrowserFingerprint:
        """
        Generate a random browser fingerprint.

        Args:
            platform: Specific platform (windows/macos/linux/android/ios) or None for random
            custom_ua: Custom User-Agent string
            canvas_mode: Canvas fingerprint mode (noise/block/redirect)
            audio_mode: Audio fingerprint mode (noise/block/fake)
            use_fonts: Font set to use (common/extended/none)

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

        fonts = []
        if use_fonts == "common":
            fonts = random.sample(FingerprintGenerator.COMMON_FONTS, k=random.randint(5, 10))
        elif use_fonts == "extended":
            fonts = random.sample(
                FingerprintGenerator.COMMON_FONTS + FingerprintGenerator.EXTENDED_FONTS,
                k=random.randint(8, 15)
            )

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
            canvas_mode=canvas_mode,
            audio_mode=audio_mode,
            fonts=fonts,
            do_not_track=random.choice([True, False]),
            hardware_concurrency_cores=random.choice([2, 4, 6, 8, 12, 16]),
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
            "canvas_mode": fp.canvas_mode,
            "audio_mode": fp.audio_mode,
            "fonts": fp.fonts,
            "do_not_track": fp.do_not_track,
            "hardware_concurrency_cores": fp.hardware_concurrency_cores,
        }

    @staticmethod
    def generate_for_profile(use_case: str = "general") -> Dict[str, Any]:
        """
        Generate fingerprint based on use case.

        Args:
            use_case: One of general, shopping, social, scraping, streaming, anti_bot, high_security
        """
        template = FINGERPRINT_TEMPLATES.get(use_case, FINGERPRINT_TEMPLATES["general"])

        return FingerprintGenerator.generate(
            platform=template.get("platform"),
            canvas_mode=template.get("canvas_mode", "noise"),
            audio_mode=template.get("audio_mode", "noise"),
        ).__dict__

    @staticmethod
    def generate_canvas_spofing_script(mode: str = "noise") -> str:
        """Generate canvas fingerprint spoofing script."""
        scripts = {
            "noise": """
(function() {
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {
        const imageData = originalGetImageData.call(this, sx, sy, sw, sh);
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            const noise = (Math.random() - 0.5) * 2;
            data[i] = Math.max(0, Math.min(255, data[i] + noise));
            data[i+1] = Math.max(0, Math.min(255, data[i+1] + noise));
            data[i+2] = Math.max(0, Math.min(255, data[i+2] + noise));
        }
        return imageData;
    };
})();
""",
            "block": """
(function() {
    CanvasRenderingContext2D.prototype.getImageData = function() {
        throw new DOMException('DOM Exception 18');
    };
})();
""",
            "redirect": """
(function() {
    const htmlElement = HTMLCanvasElement.prototype;
Canvas    const originalGetContext = htmlCanvasElement.getContext;
    
    htmlCanvasElement.getContext = function(type) {
        const context = originalGetContext.apply(this, arguments);
        if (type === '2d') {
            const originalGetImageData = context.getImageData;
            context.getImageData = function(sx, sy, sw, sh) {
                const offscreen = document.createElement('canvas');
                offscreen.width = this.canvas.width;
                offscreen.height = this.canvas.height;
                const offCtx = offscreen.getContext('2d');
                offCtx.drawImage(this.canvas, 0, 0);
                return offCtx.getImageData(sx, sy, sw, sh);
            };
        }
        return context;
    };
})();
""",
        }
        return scripts.get(mode, scripts["noise"])

    @staticmethod
    def generate_audio_spofing_script(mode: str = "noise") -> str:
        """Generate audio fingerprint spoofing script."""
        scripts = {
            "noise": """
(function() {
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.call(this);
        const originalGetByteFrequencyData = analyser.getByteFrequencyData;
        analyser.getByteFrequencyData = function(array) {
            originalGetByteFrequencyData.call(this, array);
            for (let i = 0; i < array.length; i++) {
                array[i] = Math.floor(array[i] + (Math.random() - 0.5) * 2);
            }
            return array;
        };
        return analyser;
    };
})();
""",
            "block": """
(function() {
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.call(this);
        analyser.getByteFrequencyData = function() {};
        analyser.getByteTimeDomainData = function() {};
        return analyser;
    };
})();
""",
            "fake": """
(function() {
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.call(this);
        const fakeData = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData = function(array) {
            for (let i = 0; i < array.length; i++) {
                array[i] = fakeData[i];
            }
        };
        return analyser;
    };
})();
""",
        }
        return scripts.get(mode, scripts["noise"])

    @staticmethod
    def export_fingerprint(fp: BrowserFingerprint) -> str:
        """Export fingerprint to JSON string."""
        return json.dumps(fp.__dict__, indent=2)

    @staticmethod
    def import_fingerprint(json_str: str) -> BrowserFingerprint:
        """Import fingerprint from JSON string."""
        data = json.loads(json_str)
        return BrowserFingerprint(**data)
