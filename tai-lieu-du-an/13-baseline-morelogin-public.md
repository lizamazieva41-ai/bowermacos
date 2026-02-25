# 13 — MoreLogin Public API Baseline

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-18 | **Trạng thái**: Reference  
> **Mục đích**: Tài liệu tham chiếu baseline — liệt kê đầy đủ endpoint, UX operation, và field schema của MoreLogin theo tài liệu công khai. Dùng để đối chiếu trong `14-parity-matrix.md`.

> **⚠ Lưu ý pháp lý**: Tài liệu này chỉ tổng hợp thông tin từ tài liệu công khai của MoreLogin. Không có reverse engineering, không có nội dung bí mật thương mại. Dự án BrowserManager thực hiện parity về **hành vi API** (số endpoint, tên field, response envelope), không copy brand, UI, hay logic độc quyền.

---

## 1. Tổng quan Local API MoreLogin

- **Local API host**: `http://127.0.0.1:40000`
- **Yêu cầu**: Request phải xuất phát từ cùng máy (localhost-only)
- **Authentication**: API key qua header (cụ thể header name tuỳ version)
- **Response envelope (MoreLogin-compatible)**:

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... },
  "requestId": "req-xxxxxxxx"
}
```

| Field | Type | Ý nghĩa |
|---|---|---|
| `code` | integer | `0` = success; non-zero = error |
| `msg` | string | Human-readable message |
| `data` | object/array/null | Payload |
| `requestId` | string | Trace ID cho debugging |

---

## 2. Danh sách Endpoint `/api/env/*`

### 2.1 Tạo Profile / Environment

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/create/quick` | Tạo nhanh profile với thông số tối thiểu | v1.0 |
| `POST` | `/api/env/create/advanced` | Tạo profile với đầy đủ cấu hình | v1.0 |

**Request body `/api/env/create/quick`:**
```json
{
  "name": "Profile A",
  "groupId": "group-uuid",
  "remark": "ghi chú tùy chọn",
  "proxyId": "proxy-uuid"
}
```

**Request body `/api/env/create/advanced`** (bổ sung thêm):
```json
{
  "name": "Profile A",
  "groupId": "group-uuid",
  "remark": "ghi chú",
  "proxyId": "proxy-uuid",
  "startUrl": "https://example.com",
  "extensionIds": ["ext-id-1"],
  "browserVersion": "stable",
  "osVersion": "Win10",
  "userAgent": "Mozilla/5.0...",
  "screenResolution": "1920x1080",
  "timezone": "Asia/Ho_Chi_Minh",
  "language": "vi-VN"
}
```

**Response (success):**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "env-uuid",
    "name": "Profile A",
    "status": 0
  },
  "requestId": "req-001"
}
```

---

### 2.2 Session Control

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/start` | Khởi động browser session | v1.0 |
| `POST` | `/api/env/close` | Dừng browser session | v1.0 |
| `POST` | `/api/env/closeAll` | Dừng tất cả sessions đang chạy | v1.0 |
| `POST` | `/api/env/active` | Đưa cửa sổ browser lên foreground | v1.1 |
| `POST` | `/api/env/reopen` | Mở lại session đã đóng | v1.1 |

**Request body `/api/env/start`:**
```json
{
  "id": "env-uuid",
  "headless": false,
  "encryptKey": "optional-key-if-e2e-enabled"
}
```

**Response `/api/env/start` (success):**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "env-uuid",
    "status": 1,
    "debugPort": 9222,
    "webdriver": "http://127.0.0.1:9222",
    "seleniumAddress": "http://127.0.0.1:9222",
    "version": "Chrome/120.0.6099.109"
  },
  "requestId": "req-002"
}
```

> **Ghi chú quan trọng**: Response phải bao gồm `debugPort`, `webdriver` (CDP URL), và `version`. Đây là yêu cầu cốt lõi để backend automation attach Playwright/Selenium.

**Request body `/api/env/close`:**
```json
{
  "id": "env-uuid"
}
```

**Request body `/api/env/closeAll`:**
```json
{}
```

---

### 2.3 Query / Listing

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/page` | Phân trang profiles với filter | v1.0 |
| `POST` | `/api/env/list` | Lấy danh sách có phân trang | v1.0 |
| `POST` | `/api/env/detail` | Chi tiết một profile theo `id` | v1.0 |
| `POST` | `/api/env/update` | Cập nhật thông tin profile | v1.0 |
| `POST` | `/api/env/removeToRecycleBin/batch` | Xoá profile (soft delete → trash / recycle bin) | v1.0 |

**Request body `/api/env/page`:**
```json
{
  "page": 1,
  "pageSize": 20,
  "name": "search-keyword",
  "groupId": "group-uuid",
  "tagId": "tag-uuid",
  "status": 0,
  "proxyType": "socks5",
  "sortField": "createdAt",
  "sortOrder": "desc"
}
```

**Response `/api/env/page`:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "list": [
      {
        "id": "env-uuid",
        "name": "Profile A",
        "groupId": "group-uuid",
        "groupName": "Group 1",
        "tagIds": ["tag-1"],
        "status": 0,
        "remark": "ghi chú",
        "proxyId": "proxy-uuid",
        "createdAt": "2026-02-18T10:00:00Z",
        "updatedAt": "2026-02-18T10:00:00Z",
        "lastUsedAt": "2026-02-18T09:00:00Z"
      }
    ]
  },
  "requestId": "req-003"
}
```

---

### 2.4 Debug / Diagnostic

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/getAllDebugInfo` | Lấy CDP debug info của tất cả sessions đang chạy | v1.0 |
| `POST` | `/api/env/getAllProcessIds` | Lấy PIDs của tất cả browser processes | v1.1 |
| `POST` | `/api/env/getAllScreen` | Lấy thông tin màn hình (resolution, DPI) | v1.1 |

**Response `/api/env/getAllDebugInfo`:**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "env-uuid",
      "debugPort": 9222,
      "webdriver": "http://127.0.0.1:9222",
      "status": 1
    }
  ],
  "requestId": "req-004"
}
```

---

### 2.5 Cache Management

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/removeLocalCache` | Xoá cache cục bộ của profile | v1.0 |
| `POST` | `/api/env/cache/cleanCloud` | Xoá cloud cache (chỉ MoreLogin cloud) | v1.2 |

**Request body `/api/env/removeLocalCache`:**
```json
{
  "id": "env-uuid",
  "cacheTypes": ["cookies", "localStorage", "indexedDB"]
}
```

> **Ghi chú cho BrowserManager**: `/api/env/cache/cleanCloud` không áp dụng cho self-hosted. Trả `501 Not Implemented` với message giải thích rõ ràng.

---

### 2.6 Window Management

| Method | Endpoint | Mô tả | Min Version |
|---|---|---|---|
| `POST` | `/api/env/arrangeWindows` | Sắp xếp cửa sổ browser theo layout | v1.1 |

**Request body `/api/env/arrangeWindows`:**
```json
{
  "ids": ["env-1", "env-2", "env-3"],
  "layout": "grid",
  "monitorIndex": 0
}
```

---

## 3. Danh sách Endpoint `/api/envgroup/*`

| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/envgroup/page` | Phân trang groups |
| `POST` | `/api/envgroup/create` | Tạo group mới |
| `POST` | `/api/envgroup/edit` | Sửa group |
| `POST` | `/api/envgroup/delete` | Xoá group |

**Request body `/api/envgroup/create`:**
```json
{
  "name": "Group 1",
  "sortOrder": 1,
  "color": "#FF5733"
}
```

**Response `/api/envgroup/create`:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "group-uuid",
    "name": "Group 1",
    "sortOrder": 1,
    "color": "#FF5733",
    "profileCount": 0,
    "createdAt": "2026-02-18T10:00:00Z"
  },
  "requestId": "req-005"
}
```

**Request body `/api/envgroup/page`:**
```json
{
  "page": 1,
  "pageSize": 20,
  "name": "search-keyword"
}
```

---

## 4. Danh sách Endpoint `/api/envtag/*`

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/envtag/all` | Lấy tất cả tags (no pagination) |
| `POST` | `/api/envtag/create` | Tạo tag mới |
| `POST` | `/api/envtag/edit` | Sửa tag |
| `POST` | `/api/envtag/delete` | Xoá tag |

**Request body `/api/envtag/create`:**
```json
{
  "name": "ecommerce",
  "color": "#FF0000"
}
```

**Response `/api/envtag/all`:**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "tag-uuid",
      "name": "ecommerce",
      "color": "#FF0000",
      "profileCount": 23,
      "createdAt": "2026-02-18T10:00:00Z"
    }
  ],
  "requestId": "req-006"
}
```

---

## 5. Danh sách Endpoint `/api/proxyInfo/*`

| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/proxyInfo/page` | Phân trang proxy list |
| `POST` | `/api/proxyInfo/add` | Thêm proxy mới |
| `POST` | `/api/proxyInfo/update` | Cập nhật proxy |
| `POST` | `/api/proxyInfo/delete` | Xoá proxy |

**Request body `/api/proxyInfo/add`:**
```json
{
  "label": "US SOCKS5 #1",
  "type": "socks5",
  "host": "proxy.example.com",
  "port": 1080,
  "username": "user",
  "password": "pass",
  "refreshUrl": "https://api.provider.com/rotate"
}
```

**Response `/api/proxyInfo/page`:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 50,
    "list": [
      {
        "id": "proxy-uuid",
        "label": "US SOCKS5 #1",
        "type": "socks5",
        "host": "proxy.example.com",
        "port": 1080,
        "username": "user",
        "lastStatus": "ok",
        "lastChecked": "2026-02-18T09:00:00Z",
        "profileCount": 5
      }
    ]
  },
  "requestId": "req-007"
}
```

---

## 6. UX Operations (MoreLogin GUI Reference)

### 6.1 Profile List Actions

| Action | Mô tả | API Call |
|---|---|---|
| **Copy Profile ID** | Copy UUID của profile vào clipboard | Client-side only |
| **Launch** | Khởi động browser | `POST /api/env/start` |
| **Stop** | Dừng browser | `POST /api/env/close` |
| **Clone** | Nhân bản profile | `POST /api/env/create/quick` (với source ID) |
| **Edit** | Sửa thông tin profile | `POST /api/env/update` |
| **Delete** | Xoá vào trash | `POST /api/env/removeToRecycleBin/batch` |
| **Refresh Fingerprint** | [🔒 RESTRICTED — chỉ mô tả interface] | N/A |
| **arrangeWindows** | Sắp xếp cửa sổ browser | `POST /api/env/arrangeWindows` |

### 6.2 Trash / Recycle Bin

- Profiles bị xoá vào **Trash** (MoreLogin gọi là "Recycle Bin").
- Thời gian giữ lại: **7 ngày**.
- Sau 7 ngày: tự động xoá vĩnh viễn.
- Restore: khôi phục profile về trạng thái `inactive`.

### 6.3 Filter Nâng Cao

MoreLogin UI cung cấp toolbar filter bao gồm:

```
[Group ▼] [Tag ▼] [Status ▼] [Proxy Type ▼] [Date Created ▼] [Sort ▼]
```

| Filter | Tham số API |
|---|---|
| Group | `groupId` trong `/api/env/page` |
| Tag | `tagId` trong `/api/env/page` |
| Status | `status` (0=inactive, 1=active, 2=error) |
| Proxy Type | `proxyType` ("http","socks5","ssh","none") |
| Date Created | `startDate`, `endDate` |
| Sort | `sortField`, `sortOrder` |

### 6.4 Column Settings

MoreLogin cho phép ẩn/hiện columns trong Profile List:

| Column | Mặc định |
|---|---|
| Name | ☑ Hiển thị |
| Group | ☑ Hiển thị |
| Status | ☑ Hiển thị |
| Proxy | ☑ Hiển thị |
| Tags | ☐ Ẩn |
| Created | ☐ Ẩn |
| Last Used | ☐ Ẩn |

### 6.5 E2E Encryption Setting [🔒 RESTRICTED — Interface Only]

> **Lưu ý Restricted**: Phần này chỉ mô tả **hành vi interface có thể quan sát được**, không mô tả kỹ thuật mã hoá nội bộ.

- Trong Profile Settings → Section "Security": có toggle **"End-to-End Encryption"**.
- Khi enabled: mỗi lần `POST /api/env/start` cần thêm field `encryptKey`.
- Nếu thiếu `encryptKey` → API trả lỗi (400-equivalent).
- Key **không lưu trong database** — user phải cung cấp mỗi lần.

### 6.6 Lock Status [🔒 RESTRICTED — Interface Only]

> **Lưu ý Restricted**: Chỉ mô tả hành vi interface.

- Profile có thể có `lock_status: locked` hoặc `unlocked`.
- Khi `locked`: nút Launch bị disable, hiển thị icon 🔒.
- API `POST /api/env/start` trả lỗi nếu profile đang locked.

---

## 7. Profile Settings Sections (MoreLogin UI Reference)

| Tab/Section | Các trường chính |
|---|---|
| **Basic** | name, group, remark, tags |
| **Proxy** | proxyId, proxy type, host, port, username, password |
| **Account** | platform (không applicable cho BrowserManager) |
| **Cookies** | Import/export cookies |
| **Startup Page** | startUrl, windowSize |
| **Advanced** | userAgent, OS version, screen resolution, timezone, language |
| **Security** | e2e_encryption_enabled [Restricted], lock_status [Restricted] |

---

## 8. Bảng Field Schema Reference

### 8.1 Profile / Environment Object

| Field | Type | Null? | Ghi chú |
|---|---|---|---|
| `id` | string (UUID) | No | Primary key |
| `name` | string | No | Unique per account |
| `groupId` | string (UUID) | Yes | FK → env_groups |
| `groupName` | string | Yes | Denormalized display |
| `tagIds` | array[string] | Yes | FK → env_tags (n-n) |
| `remark` | string | Yes | Free-text note |
| `status` | integer | No | 0=inactive, 1=active, 2=error |
| `proxyId` | string (UUID) | Yes | FK → proxyInfo |
| `e2e_encryption_enabled` | boolean | No | Default false [Restricted] |
| `lock_status` | enum | No | unlocked/locked [Restricted] |
| `startUrl` | string | Yes | |
| `browserVersion` | string | Yes | Chromium version |
| `userAgent` | string | Yes | |
| `osVersion` | string | Yes | |
| `screenResolution` | string | Yes | "1920x1080" |
| `timezone` | string | Yes | IANA tz string |
| `language` | string | Yes | BCP-47 |
| `createdAt` | datetime | No | |
| `updatedAt` | datetime | No | |
| `lastUsedAt` | datetime | Yes | |

### 8.2 Group Object

| Field | Type | Null? | Ghi chú |
|---|---|---|---|
| `id` | string (UUID) | No | |
| `name` | string | No | Unique |
| `sortOrder` | integer | Yes | Display order |
| `color` | string | Yes | Hex color |
| `profileCount` | integer | No | Computed |
| `createdAt` | datetime | No | |

### 8.3 Tag Object

| Field | Type | Null? | Ghi chú |
|---|---|---|---|
| `id` | string (UUID) | No | |
| `name` | string | No | Unique |
| `color` | string | No | Hex color |
| `profileCount` | integer | No | Computed |
| `createdAt` | datetime | No | |

### 8.4 ProxyInfo Object

| Field | Type | Null? | Ghi chú |
|---|---|---|---|
| `id` | string (UUID) | No | |
| `label` | string | Yes | |
| `type` | enum | No | http/https/socks5/ssh |
| `host` | string | No | |
| `port` | integer | No | 1-65535 |
| `username` | string | Yes | |
| `refreshUrl` | string | Yes | |
| `lastStatus` | enum | Yes | ok/timeout/auth_error |
| `lastChecked` | datetime | Yes | |
| `profileCount` | integer | No | Computed |
| `createdAt` | datetime | No | |

---

## 9. Danh mục đầy đủ Endpoints MoreLogin

Tổng hợp tất cả endpoint nhóm theo domain:

### Group A: `/api/env/*` (18 endpoints)

| # | Method | Path | Category |
|---|---|---|---|
| 1 | POST | `/api/env/create/quick` | Create |
| 2 | POST | `/api/env/create/advanced` | Create |
| 3 | POST | `/api/env/start` | Session |
| 4 | POST | `/api/env/close` | Session |
| 5 | POST | `/api/env/closeAll` | Session |
| 6 | POST | `/api/env/active` | Session |
| 7 | POST | `/api/env/reopen` | Session |
| 8 | POST | `/api/env/page` | Query |
| 9 | POST | `/api/env/list` | Query |
| 10 | POST | `/api/env/detail` | Query |
| 11 | POST | `/api/env/update` | Mutation |
| 12 | POST | `/api/env/removeToRecycleBin/batch` | Mutation |
| 13 | POST | `/api/env/getAllDebugInfo` | Debug |
| 14 | POST | `/api/env/getAllProcessIds` | Debug |
| 15 | POST | `/api/env/getAllScreen` | Debug |
| 16 | POST | `/api/env/removeLocalCache` | Cache |
| 17 | POST | `/api/env/cache/cleanCloud` | Cache |
| 18 | POST | `/api/env/arrangeWindows` | UI |

### Group B: `/api/envgroup/*` (4 endpoints)

| # | Method | Path |
|---|---|---|
| 1 | POST | `/api/envgroup/page` |
| 2 | POST | `/api/envgroup/create` |
| 3 | POST | `/api/envgroup/edit` |
| 4 | POST | `/api/envgroup/delete` |

### Group C: `/api/envtag/*` (4 endpoints)

| # | Method | Path |
|---|---|---|
| 1 | GET | `/api/envtag/all` |
| 2 | POST | `/api/envtag/create` |
| 3 | POST | `/api/envtag/edit` |
| 4 | POST | `/api/envtag/delete` |

### Group D: `/api/proxyInfo/*` (4 endpoints)

| # | Method | Path |
|---|---|---|
| 1 | POST | `/api/proxyInfo/page` |
| 2 | POST | `/api/proxyInfo/add` |
| 3 | POST | `/api/proxyInfo/update` |
| 4 | POST | `/api/proxyInfo/delete` |

**Tổng cộng: 30 endpoints** theo baseline MoreLogin public.

---

*Tài liệu tiếp theo: [14-parity-matrix.md](14-parity-matrix.md)*
