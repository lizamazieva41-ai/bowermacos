# 1. TÀI LIỆU API

## Base URL
```
Development: http://localhost:8000
```

## Authentication
```
Authorization: Bearer <api_token>
```

## Endpoints

### Profile Management
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | /api/v1/profiles | Liệt kê profiles |
| POST | /api/v1/profiles | Tạo profile mới |
| GET | /api/v1/profiles/{id} | Lấy profile |
| PUT | /api/v1/profiles/{id} | Cập nhật profile |
| DELETE | /api/v1/profiles/{id} | Xóa profile |

### Session Management
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | /api/v1/sessions | Tạo session |
| POST | /api/v1/sessions/{id}/start | Khởi động session |
| POST | /api/v1/sessions/{id}/stop | Dừng session |

### Browser Control
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | /api/v1/sessions/{id}/navigate | Điều hướng URL |
| POST | /api/v1/sessions/{id}/click | Click element |
| POST | /api/v1/sessions/{id}/type | Nhập text |
| GET | /api/v1/sessions/{id}/screenshot | Chụp màn hình |

## Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success"
}
```

*Document ID: ABB-V2-DOC-0701*
