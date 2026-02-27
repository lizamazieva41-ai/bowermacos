"""
Standardized API response schemas.
"""

from typing import Any, Optional, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ErrorDetail(BaseModel):
    code: int
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=_utc_now)
    request_id: Optional[str] = None


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "Success"
    error_info: Optional[ErrorResponse] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "Success"):
        return cls(success=True, data=data, message=message, error_info=None)

    @classmethod
    def error(cls, code: int, message: str, details: Optional[Dict] = None):
        return cls(
            success=False,
            data=None,
            message=message,
            error_info=ErrorResponse(code=code, message=message, details=details),
        )


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    use_case: Optional[str] = None
    browser_engine: str
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    resolution: str
    timezone: Optional[str] = None
    language: Optional[str] = None
    headless: bool
    created_at: datetime
    updated_at: datetime


class ProfileListResponse(BaseModel):
    profiles: list[ProfileResponse]
    total: int
