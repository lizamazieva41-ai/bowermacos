"""
Timezone auto-sync module.
Automatically detects and sets timezone based on proxy IP location.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimezoneInfo:
    timezone: str
    offset: int
    label: str


class TimezoneMapper:
    """Maps IP locations to timezone information."""

    TIMEZONE_MAP = {
        "US": {
            "Pacific": ("America/Los_Angeles", -8, "Pacific Time (US & Canada)"),
            "Mountain": ("America/Denver", -7, "Mountain Time (US & Canada)"),
            "Central": ("America/Chicago", -6, "Central Time (US & Canada)"),
            "Eastern": ("America/New_York", -5, "Eastern Time (US & Canada)"),
        },
        "UK": ("Europe/London", 0, "London"),
        "DE": ("Europe/Berlin", 1, "Berlin"),
        "FR": ("Europe/Paris", 1, "Paris"),
        "NL": ("Europe/Amsterdam", 1, "Amsterdam"),
        "JP": ("Asia/Tokyo", 9, "Tokyo"),
        "CN": ("Asia/Shanghai", 8, "Shanghai"),
        "HK": ("Asia/Hong_Kong", 8, "Hong Kong"),
        "SG": ("Asia/Singapore", 8, "Singapore"),
        "AU": ("Australia/Sydney", 11, "Sydney"),
        "BR": ("America/Sao_Paulo", -3, "Sao Paulo"),
        "RU": ("Europe/Moscow", 3, "Moscow"),
        "IN": ("Asia/Kolkata", 5, "Kolkata"),
        "AE": ("Asia/Dubai", 4, "Dubai"),
        "CA": {
            "Toronto": ("America/Toronto", -5, "Toronto"),
            "Vancouver": ("America/Vancouver", -8, "Vancouver"),
        },
    }

    DEFAULT_TIMEZONE = ("UTC", 0, "UTC")

    @classmethod
    def get_timezone_for_country(
        cls, country_code: str, region: str = None
    ) -> TimezoneInfo:
        if country_code in cls.TIMEZONE_MAP:
            tz_data = cls.TIMEZONE_MAP[country_code]
            if isinstance(tz_data, dict):
                if region and region in tz_data:
                    tz = tz_data[region]
                    return TimezoneInfo(tz[0], tz[1], tz[2])
                else:
                    tz = list(tz_data.values())[0]
                    return TimezoneInfo(tz[0], tz[1], tz[2])
            else:
                return TimezoneInfo(tz_data[0], tz_data[1], tz_data[2])

        return TimezoneInfo(
            cls.DEFAULT_TIMEZONE[0],
            cls.DEFAULT_TIMEZONE[1],
            cls.DEFAULT_TIMEZONE[2],
        )

    @classmethod
    def get_all_timezones(cls) -> Dict[str, Any]:
        result = {}
        for country, data in cls.TIMEZONE_MAP.items():
            if isinstance(data, dict):
                result[country] = {k: v[0] for k, v in data.items()}
            else:
                result[country] = data[0]
        return result


class TimezoneAutoSync:
    """Auto-sync timezone based on proxy IP."""

    def __init__(self, default_timezone: str = "UTC"):
        self.default_timezone = default_timezone
        self.mapper = TimezoneMapper()

    def get_timezone_from_proxy(self, proxy_url: str) -> TimezoneInfo:
        """Extract timezone hint from proxy URL or use default."""
        if not proxy_url:
            return TimezoneInfo(
                self.default_timezone,
                self.mapper.DEFAULT_TIMEZONE[1],
                self.mapper.DEFAULT_TIMEZONE[2],
            )

        country_hints = {
            "us": "US",
            "uk": "UK",
            "de": "DE",
            "fr": "FR",
            "nl": "NL",
            "jp": "JP",
            "cn": "CN",
            "hk": "HK",
            "sg": "SG",
            "au": "AU",
            "br": "BR",
            "ru": "RU",
            "in": "IN",
            "ae": "AE",
        }

        proxy_lower = proxy_url.lower()
        for hint, country in country_hints.items():
            if hint in proxy_lower:
                return self.mapper.get_timezone_for_country(country)

        return TimezoneInfo(
            self.default_timezone,
            self.mapper.DEFAULT_TIMEZONE[1],
            self.mapper.DEFAULT_TIMEZONE[2],
        )

    def get_chromium_args(self, timezone: str) -> list:
        """Get Chromium args for timezone setting."""
        return [f"--timezone={timezone}"]

    def get_stealth_script(self, timezone: str) -> str:
        """Get JavaScript to spoof timezone in browser."""
        return f"""
(function() {{
    const TIMEZONE = '{timezone}';
    
    if (Intl.DateTimeFormat) {{
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(locale, options) {{
            options = options || {{}};
            options.timeZone = options.timeZone || TIMEZONE;
            return new originalDateTimeFormat(locale, options);
        }};
        
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            return {{
                timeZone: TIMEZONE,
                locale: 'en-US'
            }};
        }};
    }}
    
    if (Date) {{
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            return 0;
        }};
    }}
    
    console.log('Timezone spoofed to:', TIMEZONE);
}})();
"""


def get_timezone_for_ip(country_code: str, region: str = None) -> str:
    """Convenience function to get timezone for country code."""
    return TimezoneMapper.get_timezone_for_country(country_code, region).timezone


def get_auto_timezone(proxy_url: str = None) -> TimezoneInfo:
    """Convenience function to get auto timezone from proxy."""
    auto_sync = TimezoneAutoSync()
    return auto_sync.get_timezone_from_proxy(proxy_url)
