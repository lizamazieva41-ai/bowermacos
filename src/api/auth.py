"""
JWT Authentication module.
Provides token-based authentication for API endpoints.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps

import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class TokenData(BaseModel):
    sub: str
    exp: datetime
    iat: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class User(BaseModel):
    username: str
    disabled: bool = False


class APIKey(BaseModel):
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


api_keys: Dict[str, APIKey] = {}
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> User:
    token_data = verify_token(credentials.credentials)
    return User(username=token_data.sub)


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


def generate_api_key(name: str, days_valid: int = 365) -> str:
    import secrets

    key = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)

    api_keys[key] = APIKey(
        key=key,
        name=name,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
    )

    logger.info(f"Generated API key for: {name}")
    return key


def verify_api_key(key: str) -> bool:
    api_key = api_keys.get(key)
    if not api_key:
        return False

    if not api_key.is_active:
        return False

    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        return False

    return True


def _get_stored_password_hash(username: str) -> str:
    """Get stored password hash for user. In production, load from database."""
    default_password = os.environ.get("ADMIN_PASSWORD", "admin")
    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")

    if admin_hash:
        return admin_hash

    return default_password


async def login(username: str, password: str) -> Optional[TokenResponse]:
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

    stored_hash = _get_stored_password_hash(username)

    from src.utils.credentials import CredentialsManager

    if CredentialsManager.verify_password(password, stored_hash):
        if username in failed_login_attempts:
            del failed_login_attempts[username]

        access_token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    if username not in failed_login_attempts:
        failed_login_attempts[username] = {
            "count": 0,
            "first_attempt": datetime.now(timezone.utc),
        }

    failed_login_attempts[username]["count"] += 1

    if failed_login_attempts[username]["count"] >= MAX_LOGIN_ATTEMPTS:
        lockout_until = datetime.now(timezone.utc) + timedelta(
            minutes=LOCKOUT_DURATION_MINUTES
        )
        lockout_info[username] = {
            "until": lockout_until,
            "attempts": failed_login_attempts[username]["count"],
        }
        del failed_login_attempts[username]
        logger.warning(
            f"Account {username} locked out after {MAX_LOGIN_ATTEMPTS} failed login attempts"
        )
        raise HTTPException(
            status_code=429,
            detail="Account locked due to too many failed attempts. "
            f"Try again in {LOCKOUT_DURATION_MINUTES} minutes.",
        )

    remaining_attempts = MAX_LOGIN_ATTEMPTS - failed_login_attempts[username]["count"]
    logger.warning(
        f"Failed login attempt for {username}. {remaining_attempts} attempts remaining"
    )

    return None
