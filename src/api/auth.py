"""
JWT Authentication module.
Provides token-based authentication for API endpoints.
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps

import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.db.store import Database
from src.db.users import User, ApiKey, UserSession, UserRole
from src.utils.credentials import CredentialsManager

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

db = Database()


class TokenData(BaseModel):
    sub: str
    exp: datetime
    iat: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = UserRole.USER.value


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ApiKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None
    days_valid: int = 365


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


failed_login_attempts: Dict[str, Dict[str, Any]] = {}
lockout_info: Dict[str, Dict[str, Any]] = {}


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UserResponse:
    token_data = verify_token(credentials.credentials)
    user = await db.get_user_by_username(token_data.sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Missing or invalid authorization header"
                )

            token = auth_header.split(" ")[1]
            verify_token(token)

        return await func(*args, **kwargs)

    return wrapper


def _hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


async def generate_api_key(
    user_id: int,
    name: str,
    description: Optional[str] = None,
    permissions: Optional[str] = None,
    days_valid: int = 365,
) -> tuple[str, ApiKey]:
    key = secrets.token_urlsafe(32)
    key_hash = _hash_api_key(key)
    expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)

    api_key_data = {
        "user_id": user_id,
        "key_hash": key_hash,
        "name": name,
        "description": description,
        "permissions": permissions,
        "expires_at": expires_at,
        "is_active": True,
    }

    db_api_key = await db.create_api_key(api_key_data)
    logger.info(f"Generated API key for user {user_id}: {name}")
    return key, db_api_key


async def verify_api_key(key: str) -> Optional[ApiKey]:
    key_hash = _hash_api_key(key)
    api_key = await db.get_api_key_by_hash(key_hash)

    if not api_key:
        return None

    if not api_key.is_active:
        return None

    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        return None

    await db.update_api_key(api_key.id, {"last_used_at": datetime.now(timezone.utc)})
    return api_key


async def list_user_api_keys(user_id: int) -> list[ApiKeyResponse]:
    api_keys = await db.list_api_keys(user_id)
    return [ApiKeyResponse.model_validate(k) for k in api_keys]


async def deactivate_api_key(api_key_id: int) -> bool:
    api_key = await db.update_api_key(api_key_id, {"is_active": False})
    return api_key is not None


async def create_user(user_data: UserCreate) -> UserResponse:
    existing_user = await db.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if user_data.email:
        existing_email = await db.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

    password_hash = CredentialsManager.hash_password(user_data.password)

    new_user_data = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": password_hash,
        "role": user_data.role,
        "is_active": True,
        "is_superuser": False,
    }

    user = await db.create_user(new_user_data)
    logger.info(f"Created new user: {user.username}")
    return UserResponse.model_validate(user)


async def get_user(user_id: int) -> Optional[UserResponse]:
    user = await db.get_user(user_id)
    if user:
        return UserResponse.model_validate(user)
    return None


async def list_users(skip: int = 0, limit: int = 100) -> list[UserResponse]:
    users = await db.list_users(skip, limit)
    return [UserResponse.model_validate(u) for u in users]


async def update_user(user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
    update_data = {}
    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.password is not None:
        update_data["password_hash"] = CredentialsManager.hash_password(user_update.password)
    if user_update.role is not None:
        update_data["role"] = user_update.role
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active

    if not update_data:
        return await get_user(user_id)

    user = await db.update_user(user_id, update_data)
    if user:
        return UserResponse.model_validate(user)
    return None


async def delete_user(user_id: int) -> bool:
    return await db.delete_user(user_id)


async def login(username: str, password: str, ip_address: Optional[str] = None) -> Optional[TokenResponse]:
    if username in lockout_info:
        lockout_until = lockout_info[username].get("until")
        if lockout_until and datetime.now(timezone.utc) < lockout_until:
            remaining_seconds = (
                lockout_until - datetime.now(timezone.utc)
            ).total_seconds()
            raise HTTPException(
                status_code=429,
                detail=f"Account locked. Try again in {int(remaining_seconds // 60)} minutes.",
            )
        else:
            del lockout_info[username]
            if username in failed_login_attempts:
                failed_login_attempts[username]["count"] = 0

    user = await db.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
        remaining_seconds = (user.locked_until - datetime.now(timezone.utc)).total_seconds()
        raise HTTPException(
            status_code=429,
            detail=f"Account locked. Try again in {int(remaining_seconds // 60)} minutes.",
        )

    if not CredentialsManager.verify_password(password, user.password_hash):
        login_attempts = user.login_attempts + 1

        if login_attempts >= MAX_LOGIN_ATTEMPTS:
            lockout_until = datetime.now(timezone.utc) + timedelta(
                minutes=LOCKOUT_DURATION_MINUTES
            )
            await db.update_user(user.id, {
                "login_attempts": 0,
                "locked_until": lockout_until,
            })
            logger.warning(f"Account {username} locked out after {MAX_LOGIN_ATTEMPTS} failed login attempts")
            raise HTTPException(
                status_code=429,
                detail="Account locked due to too many failed attempts. "
                f"Try again in {LOCKOUT_DURATION_MINUTES} minutes.",
            )

        await db.update_user(user.id, {"login_attempts": login_attempts})
        remaining_attempts = MAX_LOGIN_ATTEMPTS - login_attempts
        logger.warning(f"Failed login attempt for {username}. {remaining_attempts} attempts remaining")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await db.update_user(user.id, {
        "login_attempts": 0,
        "locked_until": None,
        "last_login": datetime.now(timezone.utc),
    })

    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info(f"User {username} logged in successfully")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def logout(user_id: int) -> bool:
    await db.deactivate_user_sessions(user_id)
    logger.info(f"User {user_id} logged out")
    return True
