# 1. TÀI LIỆU API

## Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com (with TLS)
```

## Authentication

All endpoints (except `/`, `/health`, `/dashboard`, `/api/v1/auth/*`) require authentication using one of the following methods:

### Method 1: Bearer Token (JWT)
```
Authorization: Bearer <jwt_token>
```

### Method 2: API Key
```
Authorization: Bearer <api_key>
```

### Getting a Token
- **Login**: `POST /api/v1/auth/login` with `{"username": "admin", "password": "admin"}`
- **Create API Key**: `GET /api/v1/auth/api-key?name=mykey&days_valid=365`

### Rate Limiting
- `/api/v1/auth/login`: 5 requests/minute
- `/api/v1/auth/api-key`: 3 requests/minute
- `/api/v1/profiles` (GET): 100 requests/minute
- `/api/v1/profiles` (POST): 50 requests/minute
- `/api/v1/proxies` (GET): 60 requests/minute
- `/api/v1/proxies` (POST): 30 requests/minute
- `/api/v1/proxies/{id}/test`: 10 requests/minute
- `/api/v1/sessions` (GET): 60 requests/minute
- `/api/v1/sessions` (POST): 30 requests/minute

### Security Features
- Account lockout after 5 failed login attempts (15 minutes)
- JWT token expiration: 60 minutes
- Audit logging for all API requests

---

## Endpoints

### Authentication
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| POST | /api/v1/auth/login | Đăng nhập lấy JWT token | No |
| GET | /api/v1/auth/api-key | Tạo API key mới | No |

### Profile Management
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| GET | /api/v1/profiles | Liệt kê tất cả profiles | Yes |
| POST | /api/v1/profiles | Tạo profile mới | Yes |
| GET | /api/v1/profiles/{id} | Lấy chi tiết profile | Yes |
| PUT | /api/v1/profiles/{id} | Cập nhật profile | Yes |
| DELETE | /api/v1/profiles/{id} | Xóa profile | Yes |
| POST | /api/v1/profiles/{id}/clone | Clone profile | Yes |
| GET | /api/v1/profiles/{id}/export | Export profile ra JSON | Yes |
| POST | /api/v1/profiles/import | Import profile từ JSON | Yes |

### Session Management
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| GET | /api/v1/sessions | Liệt kê tất cả sessions | Yes |
| POST | /api/v1/sessions | Tạo session mới | Yes |
| GET | /api/v1/sessions/{id} | Lấy chi tiết session | Yes |
| DELETE | /api/v1/sessions/{id} | Đóng session | Yes |
| POST | /api/v1/sessions/{id}/start | Khởi động session | Yes |
| POST | /api/v1/sessions/{id}/stop | Dừng session | Yes |

### Browser Control
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| POST | /api/v1/sessions/{id}/navigate | Điều hướng URL | Yes |
| POST | /api/v1/sessions/{id}/click | Click element | Yes |
| POST | /api/v1/sessions/{id}/type | Nhập text | Yes |
| POST | /api/v1/sessions/{id}/screenshot | Chụp màn hình | Yes |
| POST | /api/v1/sessions/{id}/execute | Execute JavaScript | Yes |
| GET | /api/v1/sessions/{id}/page-source | Lấy page source HTML | Yes |

### Proxy Management
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| GET | /api/v1/proxies | Liệt kê tất cả proxies | Yes |
| POST | /api/v1/proxies | Tạo proxy mới | Yes |
| GET | /api/v1/proxies/{id} | Lấy chi tiết proxy | Yes |
| PUT | /api/v1/proxies/{id} | Cập nhật proxy | Yes |
| DELETE | /api/v1/proxies/{id} | Xóa proxy | Yes |
| POST | /api/v1/proxies/{id}/test | Test proxy connectivity | Yes |
| GET | /api/v1/proxies/health | Proxy health summary | Yes |
| GET | /api/v1/proxy/validate | Validate proxy URL | Yes |

### Monitoring & Recovery
| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|--------|---------------|
| GET | /api/v1/metrics | Performance metrics | Yes |
| GET | /api/v1/recovery/status | Session recovery status | Yes |

### WebSocket
| Endpoint | Mô tả |
|----------|--------|
| /ws/session/{session_id} | Real-time browser control |

### Public Endpoints (No Auth Required)
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | / | API info |
| GET | /health | Health check |
| GET | /dashboard | Dashboard UI |

---

## Request/Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success"
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "message": "Error message",
  "error_info": {
    "code": 1001,
    "message": "Error message",
    "details": { ... },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid-here"
  }
}
```

### Error Codes
| Code | Meaning |
|------|---------|
| 1001 | Validation Error |
| 2001 | Network Error |
| 3001 | Authentication Error |
| 4001 | System Error |
| 5001 | Session Error |
| 6001 | Proxy Error |
| 7001 | Profile Error |
| 4040 | Not Found |

### Profile Create/Update Request
```json
{
  "name": "profile_name",
  "use_case": "general",
  "browser_engine": "chromium",
  "user_agent": "Mozilla/5.0...",
  "proxy": "http://host:port",
  "proxy_username": "user",
  "proxy_password": "pass",
  "resolution": "1920x1080",
  "timezone": "America/New_York",
  "language": "en-US",
  "headless": true,
  "advanced_settings": "{}"
}
```

### Proxy Create/Update Request
```json
{
  "name": "proxy_name",
  "proxy_type": "http",
  "host": "proxy.example.com",
  "port": 8080,
  "username": "user",
  "password": "pass",
  "is_active": true
}
```

### Session Create Request
```json
{
  "profile_id": 1
}
```

### Navigate Request
```json
{
  "url": "https://example.com",
  "timeout": 30000
}
```

### Click Request
```json
{
  "selector": "#button-id",
  "timeout": 5000
}
```

### Type Request
```json
{
  "selector": "#input-id",
  "text": "Hello World",
  "timeout": 5000
}
```

### Script Execute Request
```json
{
  "script": "return document.title;"
}
```

---

## CLI Commands

| Command | Mô tả |
|---------|--------|
| open -n <name> | Mở browser với profile |
| navigate <session_id> <url> | Điều hướng URL |
| click <session_id> <selector> | Click element |
| type-text <session_id> <selector> <text> | Nhập text |
| screenshot <session_id> [-o path] | Chụp màn hình |
| execute <session_id> <script> | Execute JavaScript |
| list-sessions | Liệt kê sessions |
| list-profiles | Liệt kê profiles |
| create-profile -n <name> | Tạo profile |
| delete-profile <id> | Xóa profile |
| clone-profile <id> -n <name> | Clone profile |
| export-profile <id> [-o file] | Export profile |
| import-profile <file> | Import profile |
| validate-proxy -p <proxy> | Validate proxy |
| health | Health check |

---

## Examples

### Login và tạo session
```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Response:
# {"success":true,"data":{"access_token":"eyJ...","token_type":"bearer","expires_in":3600}}

# 2. Tạo profile
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"name": "my-profile", "headless": true}'

# 3. Tạo session
curl -X POST http://localhost:8000/api/v1/sessions?profile_id=1 \
  -H "Authorization: Bearer eyJ..."

# 4. Navigate
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/navigate \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### WebSocket Usage
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Gửi command
ws.send(JSON.stringify({
  command: 'navigate',
  params: { url: 'https://example.com' }
}));
```

---

*Document ID: ABB-V2-DOC-0701*
*Last Updated: 2024*
*Version: 1.0*
