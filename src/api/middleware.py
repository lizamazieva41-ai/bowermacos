"""
Audit logging middleware.
Logs all API requests and events for security auditing.
"""

import logging
import time
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class AuditLogger:
    """Centralized audit logging - both file and database."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.log"
        self._db = None

    def set_database(self, database):
        """Set database instance for audit logging."""
        self._db = database

    def _parse_event_type(self, path: str, method: str) -> tuple[str, Optional[str], Optional[str]]:
        """Parse event type from request path and method."""
        if "/auth/login" in path:
            return "auth_login", "auth", None
        elif "/auth/api-key" in path:
            return "api_key_create", "auth", None
        elif "/profiles" in path:
            if method == "POST":
                return "profile_create", "profile", None
            elif method == "PUT" or method == "PATCH":
                return "profile_update", "profile", None
            elif method == "DELETE":
                return "profile_delete", "profile", None
            else:
                return "profile_access", "profile", None
        elif "/sessions" in path:
            if "start" in path or method == "POST":
                return "session_start", "session", None
            elif "stop" in path or method == "DELETE":
                return "session_stop", "session", None
            else:
                return "session_access", "session", None
        elif "/proxies" in path:
            if method == "POST":
                return "proxy_create", "proxy", None
            elif method == "PUT" or method == "PATCH":
                return "proxy_update", "proxy", None
            elif method == "DELETE":
                return "proxy_delete", "proxy", None
            elif "/test" in path:
                return "proxy_test", "proxy", None
            else:
                return "proxy_access", "proxy", None
        elif "/metrics" in path:
            return "metrics_access", "system", None
        elif "/recovery" in path:
            return "recovery_access", "system", None
        else:
            return "api_request", "api", None

    async def log_event(
        self,
        event_type: str,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Log audit event to both file and database."""
        timestamp = datetime.utcnow()
        
        log_data = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user": user,
            "ip_address": ip_address,
            "action": event_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": "success" if status_code and status_code < 400 else "failure",
            "details": json.dumps(details) if details else None,
            "user_agent": user_agent,
            "request_method": method,
            "request_path": path,
            "response_code": status_code,
            "error_message": error_message,
        }

        self._log_to_file(log_data)
        
        if self._db:
            await self._log_to_database(log_data)

        return log_data

    def _log_to_file(self, log_data: Dict[str, Any]):
        """Write audit log to file."""
        try:
            event = {
                "timestamp": log_data["timestamp"].isoformat() if isinstance(log_data["timestamp"], datetime) else log_data["timestamp"],
                "event_type": log_data["event_type"],
                "user": log_data["user"],
                "ip_address": log_data["ip_address"],
                "method": log_data["request_method"],
                "path": log_data["request_path"],
                "status_code": log_data["response_code"],
                "status": log_data["status"],
                "resource_type": log_data["resource_type"],
                "resource_id": log_data["resource_id"],
            }
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")

    async def _log_to_database(self, log_data: Dict[str, Any]):
        """Write audit log to database."""
        try:
            if self._db:
                await self._db.create_audit_log(log_data)
        except Exception as e:
            logger.error(f"Failed to write audit log to database: {e}")


audit_logger = AuditLogger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {"/health", "/docs", "/openapi.json", "/redoc"}

    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded from logging."""
        return path in self.excluded_paths or path.startswith("/docs") or path.startswith("/openapi")

    async def dispatch(self, request: Request, call_next):
        if self._is_excluded(request.url.path):
            return await call_next(request)

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        client_ip = request.client.host if request.client else "unknown"
        if request.client and hasattr(request.client, 'port'):
            client_ip = f"{request.client.host}:{request.client.port}"
        
        user_agent = request.headers.get("user-agent", "unknown")
        auth_header = request.headers.get("authorization", "none")
        user = "anonymous"
        
        if auth_header != "none":
            try:
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                from src.api.auth import verify_token

                token_data = verify_token(token)
                user = token_data.sub
            except Exception:
                user = "invalid_token"

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        duration_ms = (time.time() - start_time) * 1000
        
        event_type, resource_type, resource_id = audit_logger._parse_event_type(
            str(request.url.path), request.method
        )

        error_message = None
        if response.status_code >= 400:
            try:
                body = await request.body()
                if body:
                    error_message = body.decode('utf-8', errors='ignore')[:500]
            except Exception:
                pass

        await audit_logger.log_event(
            event_type=event_type,
            user=user,
            ip_address=client_ip,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            details={
                "request_id": request_id,
                "user_agent": user_agent,
                "duration_ms": round(duration_ms, 2),
                "query_params": str(request.query_params),
            },
            resource_type=resource_type,
            resource_id=resource_id,
            user_agent=user_agent,
            error_message=error_message,
        )

        return response


async def log_auth_event(
    action: str,
    username: str,
    ip_address: Optional[str] = None,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None,
):
    """Log authentication events."""
    await audit_logger.log_event(
        event_type=f"auth_{action}",
        user=username,
        ip_address=ip_address,
        method="AUTH",
        path=f"/auth/{action}",
        status_code=200 if success else 401,
        resource_type="auth",
        details=details,
    )


async def log_security_event(
    event_type: str,
    user: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Log security-related events."""
    await audit_logger.log_event(
        event_type=f"security_{event_type}",
        user=user,
        ip_address=ip_address,
        method="SECURITY",
        path=f"/security/{event_type}",
        status_code=403,
        resource_type="security",
        details=details,
    )


async def log_session_event(
    session_id: str,
    action: str,
    user: Optional[str] = None,
    ip_address: Optional[str] = None,
    status_code: Optional[int] = None,
):
    """Log session-related events."""
    await audit_logger.log_event(
        event_type=f"session_{action}",
        user=user,
        ip_address=ip_address,
        method="SESSION",
        path=f"/sessions/{action}",
        status_code=status_code,
        resource_type="session",
        resource_id=session_id,
    )


async def log_profile_event(
    profile_id: int,
    action: str,
    user: Optional[str] = None,
    ip_address: Optional[str] = None,
    status_code: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Log profile-related events."""
    await audit_logger.log_event(
        event_type=f"profile_{action}",
        user=user,
        ip_address=ip_address,
        method="PROFILE",
        path=f"/profiles/{profile_id}/{action}",
        status_code=status_code,
        resource_type="profile",
        resource_id=str(profile_id),
        details=details,
    )


async def log_proxy_event(
    proxy_id: int,
    action: str,
    user: Optional[str] = None,
    ip_address: Optional[str] = None,
    status_code: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Log proxy-related events."""
    await audit_logger.log_event(
        event_type=f"proxy_{action}",
        user=user,
        ip_address=ip_address,
        method="PROXY",
        path=f"/proxies/{proxy_id}/{action}",
        status_code=status_code,
        resource_type="proxy",
        resource_id=str(proxy_id),
        details=details,
    )


def log_security_event_sync(
    event_type: str,
    user: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Log security-related events (sync version for non-async contexts)."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(log_security_event(event_type, user, ip_address, details))
        else:
            loop.run_until_complete(log_security_event(event_type, user, ip_address, details))
    except Exception:
        pass
