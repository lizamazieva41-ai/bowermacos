# 1. TIÊU CHUẨN BẢO MẬT - PHIÊN BẢN MỞ RỘNG

## Authentication
- JWT tokens với expiration
- API keys với quyền hạn chế
- Rate limiting per user
- Account lockout after 5 failed attempts

## Network Security
- HTTPS bắt buộc (production)
- TLS 1.3
- Firewall: Chỉ allow ports 8000-9000, 9222

## Data Protection
| Loại | Phương pháp |
|------|-------------|
| Passwords | bcrypt |
| API Keys | AES-256 |
| Proxy Credentials | DPAPI encryption |
| Database | SQLite encryption (optional) |

## Rate Limiting
```python
# Example: FastAPI rate limiter
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

@app.post("/api/sessions/start")
@limiter.limit("5/minute")
async def create_session(request: Request):
    # Only 5 requests per minute
    pass
```

## Audit Logging
- Authentication events (login, logout, failed)
- Profile changes (create, update, delete)
- Session events (start, stop, crash)
- API access (all requests)
- Error logging

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

---

*Document ID: ABB-V2-DOC-0901 v2*
