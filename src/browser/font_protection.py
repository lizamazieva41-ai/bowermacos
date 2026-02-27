"""
Font fingerprinting protection module.
Prevents font enumeration and provides consistent font exposure.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class FontConfig:
    platform: str
    common_fonts: List[str]
    system_fonts: List[str]


class FontProtector:
    """Font fingerprinting protection."""

    PLATFORM_FONTS = {
        "windows": FontConfig(
            platform="windows",
            common_fonts=[
                "Arial",
                "Arial Black",
                "Calibri",
                "Cambria",
                "Candara",
                "Comic Sans MS",
                "Consolas",
                "Constantia",
                "Corbel",
                "Courier",
                "Courier New",
                "Georgia",
                "Impact",
                "Lucida Console",
                "Lucida Sans Unicode",
                "Microsoft Sans Serif",
                "Palatino Linotype",
                "Segoe UI",
                "Segoe Print",
                "Segoe Script",
                "Tahoma",
                "Times",
                "Times New Roman",
                "Trebuchet MS",
                "Verdana",
            ],
            system_fonts=[
                "Segoe UI",
                "Microsoft YaHei",
                "SimSun",
                "SimHei",
                "MingLiU",
            ],
        ),
        "macos": FontConfig(
            platform="macos",
            common_fonts=[
                "Arial",
                "Avenir",
                "Avenir Next",
                "Baskerville",
                "Futura",
                "Georgia",
                "Gill Sans",
                "Helvetica",
                "Helvetica Neue",
                "Menlo",
                "Monaco",
                "Optima",
                "Palatino",
                "SF Pro",
                "SF Pro Display",
                "SF Pro Text",
                "System Font",
                "Times New Roman",
                "Trebuchet MS",
                "Verdana",
            ],
            system_fonts=[
                ".AppleSystemUIFont",
                "Helvetica Neue",
                "PingFang SC",
                "Microsoft YaHei",
            ],
        ),
        "linux": FontConfig(
            platform="linux",
            common_fonts=[
                "Arial",
                "Courier",
                "Courier New",
                "DejaVu Sans",
                "DejaVu Serif",
                "FreeSans",
                "FreeSerif",
                "Liberation Mono",
                "Liberation Sans",
                "Liberation Serif",
                "Nimbus Mono",
                "Nimbus Sans",
                "Nimbus Serif",
                "Roboto",
                "Sans",
                "Serif",
                "Ubuntu",
                "Ubuntu Mono",
            ],
            system_fonts=[
                "Noto Sans CJK",
                "WenQuanYi Micro Hei",
                "AR PL UMing CN",
            ],
        ),
    }

    def __init__(self, platform: str = "windows", restrict_fonts: bool = True):
        self.platform = platform
        self.restrict_fonts = restrict_fonts
        self.config = self.PLATFORM_FONTS.get(platform, self.PLATFORM_FONTS["windows"])

    def get_allowed_fonts(self) -> List[str]:
        if self.restrict_fonts:
            return self.config.common_fonts
        return self.config.common_fonts + self.config.system_fonts

    def get_font_list_js(self) -> str:
        fonts = self.get_allowed_fonts()
        return "['" + "','".join(fonts) + "']"

    def get_stealth_script(self, seed: int = None) -> str:
        if seed:
            random.seed(seed)

        fonts = self.get_allowed_fonts()
        safe_fonts = random.sample(fonts, min(20, len(fonts)))
        fonts_js = "['" + "','".join(safe_fonts) + "']"

        return f"""
(function() {{
    const SAFE_FONTS = {fonts_js};
    const DEFAULT_FONT = 'Arial, sans-serif';

    const originalQuery = window.QueryInterface;
    const originalGetComputedStyle = window.getComputedStyle;
    
    window.getComputedStyle = function(element, pseudo) {{
        const style = originalGetComputedStyle.apply(this, arguments);
        if (style && style.fontFamily) {{
            const fontFamily = style.fontFamily;
            Object.defineProperty(style, 'fontFamily', {{
                get: function() {{
                    const allowedFonts = SAFE_FONTS.filter(f => 
                        fontFamily.includes(f)
                    );
                    return allowedFonts.length > 0 
                        ? allowedFonts[0] + ', sans-serif'
                        : DEFAULT_FONT;
                }},
                configurable: true
            }});
        }}
        return style;
    }};

    if (document.fonts) {{
        const originalCheck = document.fonts.check;
        document.fonts.check = function(font) {{
            return SAFE_FONTS.some(f => 
                font.includes(f) || font.includes('sans-serif') || font.includes('serif')
            );
        }};

        const originalLoad = document.fonts.load;
        document.fonts.load = function(font) {{
            return originalLoad.call(this, font).catch(() => {{
                return Promise.resolve();
            }});
        }};

        document.fonts.forEach = function(callback) {{
            SAFE_FONTS.forEach(font => {{
                callback(new FontFace(font, 'url(data:font/woff2;)'));
            }});
        }};
    }};

    Object.defineProperty(document, 'fonts', {{
        get: function() {{
            return {{
                check: document.fonts.check,
                load: document.fonts.load,
                ready: Promise.resolve(),
                status: 'loaded'
            }};
        }},
        configurable: true
    }});

    console.log('Font fingerprint protection activated - platform: {self.platform}');
}})();
"""


def get_font_protection_script(platform: str = "windows") -> str:
    """Get font protection script for specified platform."""
    protector = FontProtector(platform)
    return protector.get_stealth_script()


def get_recommended_fonts(platform: str) -> Dict[str, List[str]]:
    """Get recommended fonts for platform."""
    config = FontProtector.PLATFORM_FONTS.get(platform)
    if not config:
        return {"common": [], "system": []}
    return {
        "common": config.common_fonts[:15],
        "system": config.system_fonts[:5],
    }
