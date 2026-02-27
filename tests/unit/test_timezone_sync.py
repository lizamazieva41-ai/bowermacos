"""
Unit tests for timezone sync module.
"""

import pytest
from datetime import datetime
from src.browser.timezone_sync import (
    TimezoneMapper,
    TimezoneAutoSync,
    TimezoneInfo,
    GeoIPLookup,
)


class TestTimezoneMapper:
    """Unit tests for TimezoneMapper class."""

    def test_get_timezone_for_us(self):
        """Test getting timezone for US."""
        tz = TimezoneMapper.get_timezone_for_country("US", "Pacific")

        assert tz.timezone == "America/Los_Angeles"
        assert tz.offset == -8

    def test_get_timezone_for_uk(self):
        """Test getting timezone for UK."""
        tz = TimezoneMapper.get_timezone_for_country("UK")

        assert tz.timezone == "Europe/London"
        assert tz.offset == 0

    def test_get_timezone_for_germany(self):
        """Test getting timezone for Germany."""
        tz = TimezoneMapper.get_timezone_for_country("DE")

        assert tz.timezone == "Europe/Berlin"
        assert tz.offset == 1

    def test_get_timezone_for_japan(self):
        """Test getting timezone for Japan."""
        tz = TimezoneMapper.get_timezone_for_country("JP")

        assert tz.timezone == "Asia/Tokyo"
        assert tz.offset == 9

    def test_get_timezone_for_unknown_country(self):
        """Test getting timezone for unknown country."""
        tz = TimezoneMapper.get_timezone_for_country("XX")

        assert tz.timezone == "UTC"
        assert tz.offset == 0

    def test_get_timezone_with_region(self):
        """Test getting timezone with region."""
        tz = TimezoneMapper.get_timezone_for_country("US", "Eastern")

        assert tz.timezone == "America/New_York"
        assert tz.offset == -5

    def test_get_all_timezones(self):
        """Test getting all timezones."""
        timezones = TimezoneMapper.get_all_timezones()

        assert "US" in timezones
        assert "UK" in timezones
        assert "DE" in timezones
        assert "JP" in timezones


class TestTimezoneAutoSync:
    """Unit tests for TimezoneAutoSync class."""

    def test_create_auto_sync(self):
        """Test creating auto sync instance."""
        sync = TimezoneAutoSync()

        assert sync is not None
        assert sync.default_timezone == "UTC"

    def test_get_timezone_from_proxy_us(self):
        """Test getting timezone from US proxy."""
        sync = TimezoneAutoSync()
        tz = sync.get_timezone_from_proxy("http://us-proxy.com:8080")

        assert tz is not None

    def test_get_timezone_from_proxy_uk(self):
        """Test getting timezone from UK proxy."""
        sync = TimezoneAutoSync()
        tz = sync.get_timezone_from_proxy("http://uk-proxy.com:8080")

        assert tz is not None

    def test_get_timezone_from_proxy_jp(self):
        """Test getting timezone from Japan proxy."""
        sync = TimezoneAutoSync()
        tz = sync.get_timezone_from_proxy("http://jp-proxy.com:8080")

        assert tz is not None

    def test_get_timezone_from_empty_proxy(self):
        """Test getting timezone from empty proxy."""
        sync = TimezoneAutoSync()
        tz = sync.get_timezone_from_proxy("")

        assert tz.timezone == "UTC"

    def test_get_timezone_from_none_proxy(self):
        """Test getting timezone from None proxy."""
        sync = TimezoneAutoSync()
        tz = sync.get_timezone_from_proxy(None)

        assert tz.timezone == "UTC"

    def test_get_chromium_args(self):
        """Test getting Chromium args."""
        sync = TimezoneAutoSync()
        args = sync.get_chromium_args("America/New_York")

        assert isinstance(args, list)
        assert any("timezone" in arg for arg in args)

    def test_get_stealth_script(self):
        """Test getting stealth script."""
        sync = TimezoneAutoSync()
        script = sync.get_stealth_script("America/New_York")

        assert "America/New_York" in script
        assert "Intl.DateTimeFormat" in script


class TestTimezoneInfo:
    """Unit tests for TimezoneInfo dataclass."""

    def test_timezone_info_creation(self):
        """Test creating TimezoneInfo."""
        tz = TimezoneInfo(
            timezone="America/New_York",
            offset=-5,
            label="Eastern Time",
        )

        assert tz.timezone == "America/New_York"
        assert tz.offset == -5
        assert tz.label == "Eastern Time"

    def test_timezone_info_default(self):
        """Test TimezoneInfo default values."""
        tz = TimezoneInfo(
            timezone="UTC",
            offset=0,
            label="UTC",
        )

        assert tz.timezone == "UTC"
        assert tz.offset == 0


class TestGeoIPLookup:
    """Unit tests for GeoIPLookup class."""

    def test_create_geo_lookup(self):
        """Test creating GeoIPLookup instance."""
        lookup = GeoIPLookup()

        assert lookup is not None
        assert isinstance(lookup._cache, dict)

    def test_clear_cache(self):
        """Test clearing cache."""
        lookup = GeoIPLookup()
        lookup._cache["test"] = TimezoneInfo("UTC", 0, "UTC")

        lookup.clear_cache()

        assert len(lookup._cache) == 0


@pytest.mark.asyncio
class TestTimezoneAsync:
    """Async tests for timezone functionality."""

    async def test_auto_timezone_with_proxy_ip(self):
        """Test auto timezone with proxy IP."""
        from src.browser.timezone_sync import get_auto_timezone

        tz = await get_auto_timezone(proxy_url="http://us-proxy.com:8080")

        assert tz is not None
        assert isinstance(tz.timezone, str)
