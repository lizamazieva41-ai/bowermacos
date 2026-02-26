# 1. KIẾN TRÚC HỆ THỐNG

## Sơ đồ kiến trúc
```
Client → API Gateway → Process Manager → Browser Pool
                    ↓
              Core Services
              - Profile Manager
              - Fingerprint Service
              - Proxy Manager
              - Stealth Service
                    ↓
              Data Layer (SQLite)
```

## Các thành phần chính
| Thành phần | Công nghệ |
|------------|-----------|
| API Server | FastAPI/Flask |
| CLI Tool | Click/Typer |
| Browser Automation | Playwright, Selenium, UC |
| Database | SQLite |

## Luồng dữ liệu
1. User → HTTP Request → API Server
2. API Server → Process Manager
3. Process Manager → Browser Instance (CDP)
4. Result → API Response → User

*Document ID: ABB-V2-DOC-0501*
