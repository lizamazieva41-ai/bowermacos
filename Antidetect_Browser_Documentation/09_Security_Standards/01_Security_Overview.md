# 1. TIÊU CHUẨN BẢO MẬT - PHIÊN BẢN MỞ RỘNG

## Authentication
- JWT tokens với expiration (default: 24h)
- API keys với quyền hạn chế
- Rate limiting per user (50-100 requests/minute)
- Account lockout after 5 failed attempts (lock for 15 minutes)
- Password hashing: bcrypt with salt

## Network Security
- HTTPS bắt buộc (production)
- TLS 1.3
- Firewall: Chỉ allow ports 8000-9000, 9222
- CORS policy configured

## Data Protection
| Loại | Phương pháp |
|------|-------------|
| Passwords | bcrypt |
| API Keys | SHA-256 hash (only store hash, not raw key) |
| Proxy Credentials | AES-256 encryption |
| Database | SQLite with encryption (optional) |

## Rate Limiting
```python
# Example: FastAPI rate limiter
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

@app.post("/api/sessions/start")
@limiter.limit("30/minute")
async def create_session(request: Request):
    # Only 30 requests per minute for session creation
    pass

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # Only 5 login attempts per minute
    pass
```

### Rate Limit Rules
| Endpoint | Limit |
|----------|-------|
| /api/v1/auth/login | 5/minute |
| /api/v1/auth/api-key | 3/minute |
| /api/v1/profiles | 100/minute |
| /api/v1/sessions | 30/minute |
| /api/v1/proxies | 60/minute |
| /api/v1/proxies/{id}/test | 10/minute |

## Audit Logging
- Authentication events (login, logout, failed)
- Profile changes (create, update, delete)
- Session events (start, stop, crash)
- API access (all requests)
- Error logging with stack traces

### Audit Log Events
```python
# Log types
AUDIT_LOGIN_SUCCESS = "login_success"
AUDIT_LOGIN_FAILED = "login_failed"
AUDIT_LOGOUT = "logout"
AUDIT_PROFILE_CREATE = "profile_create"
AUDIT_PROFILE_UPDATE = "profile_update"
AUDIT_PROFILE_DELETE = "profile_delete"
AUDIT_PROFILE_CLONE = "profile_clone"
AUDIT_SESSION_START = "session_start"
AUDIT_SESSION_STOP = "session_stop"
AUDIT_SESSION_CRASH = "session_crash"
AUDIT_PROXY_CREATE = "proxy_create"
AUDIT_PROXY_UPDATE = "proxy_update"
AUDIT_PROXY_DELETE = "proxy_delete"
AUDIT_API_ACCESS = "api_access"
```

## TLS Configuration
```bash
# Production startup with TLS
uvicorn main:app --host 0.0.0.0 --port 8000 \
    --ssl-keyfile=./key.pem \
    --ssl-certfile=./cert.pem
```

## Browser Security
- Isolated BrowserContext per profile
- No Local Storage Leak
- Stealth mode mặc định bật
- Chrome flags for security:
  - `--disable-blink-features=AutomationControlled`
  - `--no-sandbox`
  - `--disable-setuid-sandbox`
  - `--disable-dev-shm-usage`

## Session Security
- Session ID: UUID4 (cryptographically secure)
- Session timeout: 30 minutes idle
- Maximum concurrent sessions: 50 (configurable)
- Session recovery on crash

## API Key Security
- Key length: 32 characters minimum
- Key format: alphanumeric + special characters
- Hash stored in database (never plain text)
- Expiration date support
- Revocation capability

---

## Security Headers
```python
# Recommended security headers
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

---

*Document ID: ABB-V2-DOC-0901 v3*
