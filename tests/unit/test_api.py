"""
Unit tests for API modules.
"""

import pytest
from src.api.schemas import ApiResponse, ProfileResponse, ErrorResponse
from src.api.errors import ErrorCode, APIError


class TestApiResponse:
    """Unit tests for ApiResponse schema."""

    def test_ok_response_default(self):
        response = ApiResponse.ok()
        assert response.success is True
        assert response.data is None
        assert response.message == "Success"
        assert response.error_info is None

    def test_ok_response_with_data(self):
        response = ApiResponse.ok(data={"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}

    def test_ok_response_with_message(self):
        response = ApiResponse.ok(message="Custom message")
        assert response.message == "Custom message"

    def test_error_response(self):
        response = ApiResponse.error(code=400, message="Bad request")
        assert response.success is False
        assert response.data is None
        assert response.error_info is not None
        assert response.error_info.code == 400

    def test_error_response_with_details(self):
        response = ApiResponse.error(
            code=400, message="Bad request", details={"field": "name"}
        )
        assert response.error_info.details == {"field": "name"}

    def test_error_response_timestamp(self):
        response = ApiResponse.error(code=400, message="Error")
        assert response.error_info.timestamp is not None


class TestProfileResponse:
    """Unit tests for ProfileResponse schema."""

    def test_profile_response_creation(self):
        from datetime import datetime

        profile = ProfileResponse(
            id=1,
            name="test_profile",
            use_case="browsing",
            browser_engine="chromium",
            user_agent="Mozilla/5.0...",
            proxy=None,
            proxy_username=None,
            proxy_password=None,
            resolution="1920x1080",
            timezone="UTC",
            language="en-US",
            headless=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert profile.id == 1
        assert profile.name == "test_profile"
        assert profile.browser_engine == "chromium"

    def test_profile_response_optional_fields(self):
        from datetime import datetime

        profile = ProfileResponse(
            id=1,
            name="test",
            browser_engine="chromium",
            resolution="1920x1080",
            headless=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert profile.use_case is None
        assert profile.user_agent is None
        assert profile.proxy is None


class TestErrorCode:
    """Unit tests for ErrorCode enum."""

    def test_error_code_values(self):
        assert ErrorCode.VALIDATION_ERROR == 1001
        assert ErrorCode.NETWORK_ERROR == 2001
        assert ErrorCode.AUTH_ERROR == 3001
        assert ErrorCode.SYSTEM_ERROR == 4001
        assert ErrorCode.SESSION_ERROR == 5001
        assert ErrorCode.PROXY_ERROR == 6001
        assert ErrorCode.PROFILE_ERROR == 7001
        assert ErrorCode.NOT_FOUND == 4040


class TestAPIError:
    """Unit tests for APIError exception."""

    def test_api_error_creation(self):
        error = APIError(code=ErrorCode.VALIDATION_ERROR, message="Invalid input")
        assert error.code == ErrorCode.VALIDATION_ERROR
        assert error.message == "Invalid input"
        assert error.status_code == 400

    def test_api_error_with_details(self):
        error = APIError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid input",
            details={"field": "email"},
        )
        assert error.details == {"field": "email"}

    def test_api_error_custom_status_code(self):
        error = APIError(code=ErrorCode.NOT_FOUND, message="Not found", status_code=404)
        assert error.status_code == 404

    def test_api_error_is_exception(self):
        error = APIError(code=400, message="Error")
        assert isinstance(error, Exception)


class TestAuthModuleUnit:
    """Unit tests for auth module."""

    def test_create_access_token(self):
        from src.api.auth import create_access_token

        token = create_access_token({"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token(self):
        from src.api.auth import create_access_token, verify_token

        token = create_access_token({"sub": "testuser"})
        token_data = verify_token(token)
        assert token_data.sub == "testuser"

    def test_generate_api_key(self):
        from src.api.auth import generate_api_key, verify_api_key

        key = generate_api_key("test_key")
        assert key is not None
        assert len(key) > 20
        assert verify_api_key(key) is True

    def test_verify_invalid_api_key(self):
        from src.api.auth import verify_api_key

        assert verify_api_key("nonexistent_key") is False


class TestBrowserManagerConfig:
    """Unit tests for BrowserManager ProfileConfig."""

    def test_profile_config_defaults(self):
        from src.browser.manager import ProfileConfig

        config = ProfileConfig(name="test")
        assert config.name == "test"
        assert config.headless is True
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080

    def test_profile_config_with_proxy(self):
        from src.browser.manager import ProfileConfig

        config = ProfileConfig(
            name="test",
            proxy="http://proxy:8080",
            proxy_username="user",
            proxy_password="pass",
        )
        assert config.proxy == "http://proxy:8080"
        assert config.proxy_username == "user"
        assert config.proxy_password == "pass"

    def test_profile_config_with_timezone(self):
        from src.browser.manager import ProfileConfig

        config = ProfileConfig(
            name="test", timezone="America/New_York", language="en-US"
        )
        assert config.timezone == "America/New_York"
        assert config.language == "en-US"
