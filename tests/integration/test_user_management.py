"""
Integration tests for user management flows.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.db.store import Database
from src.db.users import User, ApiKey, UserSession, UserRole
from src.api.auth import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user,
    generate_api_key,
    verify_api_key,
    list_user_api_keys,
    deactivate_api_key,
    login,
    logout,
)


class TestUserManagementIntegration:
    """Integration tests for user management."""

    @pytest.mark.asyncio
    async def test_create_user_flow(self):
        """Test complete user creation flow."""
        from src.api.auth import UserCreate

        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="securepassword123",
            role="user",
        )

        with patch("src.api.auth.db") as mock_db:
            mock_db.get_user_by_username = AsyncMock(return_value=None)
            mock_db.get_user_by_email = AsyncMock(return_value=None)
            mock_db.create_user = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                email="test@example.com",
                role="user",
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                last_login=None,
            ))

            user = await create_user(user_data)

            assert user is not None

    @pytest.mark.asyncio
    async def test_get_user_flow(self):
        """Test getting a user."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                email="test@example.com",
                role="user",
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                last_login=None,
            ))

            user = await get_user(1)

            assert user is not None
            mock_db.get_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_list_users_flow(self):
        """Test listing users."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.list_users = AsyncMock(return_value=[
                MagicMock(
                    id=1,
                    username="user1",
                    email="user1@example.com",
                    role="user",
                    is_active=True,
                    is_superuser=False,
                    created_at=datetime.utcnow(),
                    last_login=None,
                ),
                MagicMock(
                    id=2,
                    username="user2",
                    email="user2@example.com",
                    role="admin",
                    is_active=True,
                    is_superuser=True,
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                ),
            ])

            users = await list_users()

            assert len(users) == 2

    @pytest.mark.asyncio
    async def test_update_user_flow(self):
        """Test updating a user."""
        from src.api.auth import UserUpdate

        with patch("src.api.auth.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                email="old@example.com",
                role="user",
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                last_login=None,
            ))
            mock_db.update_user = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                email="new@example.com",
                role="user",
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                last_login=None,
            ))

            user_update = UserUpdate(email="new@example.com")
            user = await update_user(1, user_update)

            assert user is not None


class TestApiKeyManagementIntegration:
    """Integration tests for API key management."""

    @pytest.mark.asyncio
    async def test_generate_api_key_flow(self):
        """Test generating an API key."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.create_api_key = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=1,
                key_hash="hashed_key",
                name="Test Key",
                description="Test description",
                permissions="read,write",
                expires_at=datetime.utcnow() + timedelta(days=365),
                is_active=True,
                created_at=datetime.utcnow(),
            ))

            key, api_key = await generate_api_key(
                user_id=1,
                name="Test Key",
                description="Test description",
                permissions="read,write",
                days_valid=365,
            )

            assert key is not None
            assert len(key) > 0

    @pytest.mark.asyncio
    async def test_verify_api_key_flow(self):
        """Test verifying an API key."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_api_key_by_hash = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=1,
                key_hash="hashed_key",
                expires_at=datetime.utcnow() + timedelta(days=365),
                is_active=True,
            ))

            result = await verify_api_key("test_key")

            assert result is not None

    @pytest.mark.asyncio
    async def test_verify_expired_api_key(self):
        """Test verifying an expired API key."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_api_key_by_hash = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=1,
                key_hash="hashed_key",
                expires_at=datetime.utcnow() - timedelta(days=1),
                is_active=True,
            ))

            result = await verify_api_key("test_key")

            assert result is None

    @pytest.mark.asyncio
    async def test_verify_inactive_api_key(self):
        """Test verifying an inactive API key."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_api_key_by_hash = AsyncMock(return_value=MagicMock(
                id=1,
                user_id=1,
                key_hash="hashed_key",
                expires_at=datetime.utcnow() + timedelta(days=365),
                is_active=False,
            ))

            result = await verify_api_key("test_key")

            assert result is None

    @pytest.mark.asyncio
    async def test_list_user_api_keys(self):
        """Test listing user API keys."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.list_api_keys = AsyncMock(return_value=[
                MagicMock(
                    id=1,
                    name="Key 1",
                    description="Description 1",
                    permissions="read",
                    is_active=True,
                    expires_at=datetime.utcnow() + timedelta(days=30),
                    created_at=datetime.utcnow(),
                    last_used_at=None,
                ),
                MagicMock(
                    id=2,
                    name="Key 2",
                    description="Description 2",
                    permissions="read,write",
                    is_active=True,
                    expires_at=datetime.utcnow() + timedelta(days=60),
                    created_at=datetime.utcnow(),
                    last_used_at=datetime.utcnow(),
                ),
            ])

            keys = await list_user_api_keys(1)

            assert len(keys) == 2


class TestLoginFlowIntegration:
    """Integration tests for login flow."""

    @pytest.mark.asyncio
    async def test_successful_login(self):
        """Test successful login."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_user_by_username = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                password_hash="$2b$12$hashedpassword",
                role="user",
                is_active=True,
                login_attempts=0,
                locked_until=None,
            ))
            mock_db.update_user = AsyncMock()

            result = await login("testuser", "correctpassword")

            assert result is not None
            assert result.access_token is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Test login with wrong password."""
        with patch("src.api.auth.db") as mock_db:
            from src.utils.credentials import CredentialsManager

            mock_db.get_user_by_username = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                password_hash=CredentialsManager.hash_password("correctpassword"),
                role="user",
                is_active=True,
                login_attempts=0,
                locked_until=None,
            ))

            with pytest.raises(Exception):
                await login("testuser", "wrongpassword")

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """Test login with inactive user."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.get_user_by_username = AsyncMock(return_value=MagicMock(
                id=1,
                username="testuser",
                password_hash="hashedpassword",
                role="user",
                is_active=False,
                login_attempts=0,
                locked_until=None,
            ))

            with pytest.raises(Exception):
                await login("testuser", "password")

    @pytest.mark.asyncio
    async def test_logout_flow(self):
        """Test logout flow."""
        with patch("src.api.auth.db") as mock_db:
            mock_db.deactivate_user_sessions = AsyncMock(return_value=True)

            result = await logout(1)

            assert result is True
            mock_db.deactivate_user_sessions.assert_called_once_with(1)
