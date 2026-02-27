"""
Error handling utilities with standardized error codes.
"""

from enum import IntEnum
from typing import Optional, Dict, Any
from fastapi import HTTPException


class ErrorCode(IntEnum):
    VALIDATION_ERROR = 1001
    NETWORK_ERROR = 2001
    AUTH_ERROR = 3001
    SYSTEM_ERROR = 4001
    SESSION_ERROR = 5001
    PROXY_ERROR = 6001
    PROFILE_ERROR = 7001
    NOT_FOUND = 4040


class APIError(Exception):
    def __init__(
        self,
        code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
        request_id: Optional[str] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(self.message)


def api_error(code: ErrorCode, message: str, details: Optional[Dict] = None):
    return APIError(code=code, message=message, details=details)


def not_found_error(resource: str, resource_id: Any):
    return APIError(
        code=ErrorCode.NOT_FOUND,
        message=f"{resource} not found: {resource_id}",
        status_code=404,
    )


def validation_error(message: str, field: Optional[str] = None):
    details = {"field": field} if field else None
    return APIError(code=ErrorCode.VALIDATION_ERROR, message=message, details=details)
