"""
Unit tests for User model and authentication.
"""

import pytest
from datetime import datetime, timedelta
from src.db.users import User, ApiKey, UserSession, UserRole


class TestUserModel:
    """Unit tests for User model."""

    def test_user_creation(self):
        """Test creating a new user."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.USER.value,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.ADMIN.value,
        )

        assert "testuser" in repr(user)
        assert "admin" in repr(user)

    def test_user_default_values(self):
        """Test user default values."""
        user = User(
            id=1,
            username="testuser",
            password_hash="hashed_password",
        )

        assert user.role == "user"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.login_attempts == 0


class TestApiKeyModel:
    """Unit tests for ApiKey model."""

    def test_api_key_creation(self):
        """Test creating a new API key."""
        api_key = ApiKey(
            id=1,
            user_id=1,
            key_hash="abc123",
            name="Test Key",
            description="Test API key",
            permissions="read,write",
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        assert api_key.name == "Test Key"
        assert api_key.user_id == 1
        assert api_key.is_active is True

    def test_api_key_repr(self):
        """Test API key string representation."""
        api_key = ApiKey(
            id=1,
            user_id=1,
            key_hash="abc123",
            name="Test Key",
        )

        assert "Test Key" in repr(api_key)
        assert "1" in repr(api_key)


class TestUserSessionModel:
    """Unit tests for UserSession model."""

    def test_user_session_creation(self):
        """Test creating a new user session."""
        session = UserSession(
            id=1,
            user_id=1,
            token_hash="token123",
            device_info="Chrome on Windows",
            ip_address="192.168.1.1",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
        )

        assert session.user_id == 1
        assert session.is_active is True
        assert session.device_info == "Chrome on Windows"

    def test_user_session_repr(self):
        """Test user session string representation."""
        session = UserSession(
            id=1,
            user_id=1,
            token_hash="token123",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        assert "1" in repr(session)
        assert "active" in repr(session).lower()


class TestUserRole:
    """Unit tests for UserRole enum."""

    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
        assert UserRole.VIEWER.value == "viewer"

    def test_user_role_enum(self):
        """Test UserRole enum membership."""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.VIEWER == "viewer"
