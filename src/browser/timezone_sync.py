"""
Timezone auto-sync module.
Automatically detects and sets timezone based on proxy IP location.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TimezoneInfo:
    timezone: str
    offset: int
    label: str


class GeoIPLookup:
    """GeoIP lookup for timezone detection."""

    def __init__(self):
        self._cache: Dict[str, TimezoneInfo] = {}
        self._geo_service = None

    async def lookup(self, ip: str) -> Optional[TimezoneInfo]:
        """
        Lookup timezone for IP address.
        
        Args:
            ip: IP address to lookup
            
        Returns:
            TimezoneInfo or None
        """
        if ip in self._cache:
            return self._cache[ip]

        try:
            tz = await self._fetch_timezone(ip)
            if tz:
                self._cache[ip] = tz
                return tz
        except Exception as e:
            logger.warning(f"GeoIP lookup failed for {ip}: {e}")

        return None

    async def _fetch_timezone(self, ip: str) -> Optional[TimezoneInfo]:
        """Fetch timezone from external service."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,timezone",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "success":
                            return TimezoneInfo(
                                timezone=data.get("timezone", "UTC"),
                                offset=self._get_offset_from_tz(data.get("timezone", "UTC")),
                                label=f"{data.get('city', '')}, {data.get('country', '')}"
                            )
        except Exception as e:
            logger.debug(f"External GeoIP service unavailable: {e}")

        return None

    @staticmethod
    def _get_offset_from_tz(tz: str) -> int:
        """Get UTC offset from timezone name."""
        import pytz
        try:
            tz_obj = pytz.timezone(tz)
            dt = datetime.now(tz_obj)
            return int(dt.utcoffset().total_seconds() / 3600)
        except Exception:
            return 0

    def clear_cache(self):
        """Clear the cache."""
        self._cache.clear()


class TimezoneMapper:
    """Maps IP locations to timezone information."""

    TIMEZONE_MAP = {
        "US": {
            "Pacific": ("America/Los_Angeles", -8, "Pacific Time (US & Canada)"),
            "Mountain": ("America/Denver", -7, "Mountain Time (US & Canada)"),
            "Central": ("America/Chicago", -6, "Central Time (US & Canada)"),
            "Eastern": ("America/New_York", -5, "Eastern Time (US & Canada)"),
            "Arizona": ("America/Phoenix", -7, "Arizona"),
            "Alaska": ("America/Anchorage", -9, "Alaska"),
            "Hawaii": ("Pacific/Honolulu", -10, "Hawaii"),
        },
        "UK": ("Europe/London", 0, "London"),
        "DE": ("Europe/Berlin", 1, "Berlin"),
        "FR": ("Europe/Paris", 1, "Paris"),
        "NL": ("Europe/Amsterdam", 1, "Amsterdam"),
        "ES": ("Europe/Madrid", 1, "Madrid"),
        "IT": ("Europe/Rome", 1, "Rome"),
        "PL": ("Europe/Warsaw", 1, "Warsaw"),
        "SE": ("Europe/Stockholm", 1, "Stockholm"),
        "JP": ("Asia/Tokyo", 9, "Tokyo"),
        "CN": ("Asia/Shanghai", 8, "Shanghai"),
        "HK": ("Asia/Hong_Kong", 8, "Hong Kong"),
        "SG": ("Asia/Singapore", 8, "Singapore"),
        "KR": ("Asia/Seoul", 9, "Seoul"),
        "TW": ("Asia/Taipei", 8, "Taipei"),
        "IN": ("Asia/Kolkata", 5, "Kolkata"),
        "AE": ("Asia/Dubai", 4, "Dubai"),
        "AU": {
            "Sydney": ("Australia/Sydney", 11, "Sydney"),
            "Melbourne": ("Australia/Melbourne", 11, "Melbourne"),
            "Brisbane": ("Australia/Brisbane", 10, "Brisbane"),
            "Perth": ("Australia/Perth", 8, "Perth"),
        },
        "NZ": ("Pacific/Auckland", 13, "Auckland"),
        "BR": ("America/Sao_Paulo", -3, "Sao Paulo"),
        "AR": ("America/Argentina/Buenos_Aires", -3, "Buenos Aires"),
        "MX": ("America/Mexico_City", -6, "Mexico City"),
        "CA": {
            "Toronto": ("America/Toronto", -5, "Toronto"),
            "Vancouver": ("America/Vancouver", -8, "Vancouver"),
            "Montreal": ("America/Montreal", -5, "Montreal"),
            "Calgary": ("America/Edmonton", -7, "Calgary"),
        },
        "RU": ("Europe/Moscow", 3, "Moscow"),
        "UA": ("Europe/Kiev", 2, "Kyiv"),
        "TR": ("Europe/Istanbul", 3, "Istanbul"),
        "ZA": ("Africa/Johannesburg", 2, "Johannesburg"),
        "EG": ("Africa/Cairo", 2, "Cairo"),
    }

    COUNTRY_TO_REGION = {
        "US": "US",
        "GB": "UK",
        "DE": "DE",
        "FR": "FR",
        "NL": "NL",
        "ES": "ES",
        "IT": "IT",
        "PL": "PL",
        "SE": "SE",
        "JP": "JP",
        "CN": "CN",
        "HK": "HK",
        "SG": "SG",
        "KR": "KR",
        "TW": "TW",
        "IN": "IN",
        "AE": "AE",
        "AU": "AU",
        "NZ": "NZ",
        "BR": "BR",
        "AR": "AR",
        "MX": "MX",
        "CA": "CA",
        "RU": "RU",
        "UA": "UA",
        "TR": "TR",
        "ZA": "ZA",
        "EG": "EG",
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
        self.geo_lookup = GeoIPLookup()
        self._proxy_tz_cache: Dict[str, str] = {}

    async def get_timezone_from_proxy_ip(self, proxy_ip: str) -> TimezoneInfo:
        """
        Get timezone by looking up proxy IP.
        
        Args:
            proxy_ip: Proxy IP address
            
        Returns:
            TimezoneInfo
        """
        if proxy_ip in self._proxy_tz_cache:
            tz_name = self._proxy_tz_cache[proxy_ip]
            return TimezoneMapper.get_timezone_for_country(
                TimezoneMapper.COUNTRY_TO_REGION.get(tz_name, "US")
            )

        tz = await self.geo_lookup.lookup(proxy_ip)
        if tz:
            country = self._get_country_from_tz(tz.timezone)
            if country:
                self._proxy_tz_cache[proxy_ip] = country
            return tz

        return TimezoneInfo(
            self.default_timezone,
            self.mapper.DEFAULT_TIMEZONE[1],
            self.mapper.DEFAULT_TIMEZONE[2],
        )

    def _get_country_from_tz(self, timezone: str) -> Optional[str]:
        """Extract country code from timezone."""
        tz_to_country = {
            "America/Los_Angeles": "US",
            "America/Chicago": "US",
            "America/Denver": "US",
            "America/New_York": "US",
            "Europe/London": "GB",
            "Europe/Berlin": "DE",
            "Europe/Paris": "FR",
            "Asia/Tokyo": "JP",
            "Asia/Shanghai": "CN",
            "Asia/Hong_Kong": "HK",
            "Asia/Singapore": "SG",
            "Asia/Seoul": "KR",
        }
        return tz_to_country.get(timezone)

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
            "uk": "GB",
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
            "kr": "KR",
            "tw": "TW",
        }

        proxy_lower = proxy_url.lower()
        for hint, country in country_hints.items():
            if hint in proxy_lower:
                return self.mapper.get_timezone_for_country(
                    self.mapper.COUNTRY_TO_REGION.get(country, country)
                )

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


async def get_auto_timezone(proxy_url: str = None, proxy_ip: str = None) -> TimezoneInfo:
    """
    Convenience function to get auto timezone.
    
    Args:
        proxy_url: Proxy URL for hint-based detection
        proxy_ip: Proxy IP for GeoIP lookup
        
    Returns:
        TimezoneInfo
    """
    auto_sync = TimezoneAutoSync()
    
    if proxy_ip:
        return await auto_sync.get_timezone_from_proxy_ip(proxy_ip)
    
    return auto_sync.get_timezone_from_proxy(proxy_url)
