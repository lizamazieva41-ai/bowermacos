# Error Catalog — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **SSOT cho**: Tất cả error codes và HTTP status codes  
> **Người phê duyệt**: Tech Lead

---

## 1. Tổng quan

Tài liệu này là **Single Source of Truth** cho tất cả error codes của BrowserManager.  
Mọi endpoint, CLI command và GUI message phải sử dụng error codes từ catalog này.

### 1.1 Format chuẩn Error Response

Tất cả API errors trả về theo compat envelope:

```json
{
  "code": -1001,
  "msg": "Profile not found",
  "data": null,
  "requestId": "req-abc123"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `code` | integer | App error code (0 = success; < 0 = error) |
| `msg` | string | Human-readable error message (English) |
| `data` | any\|null | Payload (null khi error) |
| `requestId` | string | Correlation ID cho logging |

### 1.2 Nguyên tắc đặt code

| Range | Nhóm |
|---|---|
| `0` | Success |
| `-1` | Generic error (dùng khi không rõ nhóm) |
| `-1001` — `-1099` | Profile errors |
| `-1101` — `-1199` | Group errors |
| `-1201` — `-1299` | Tag errors |
| `-1301` — `-1399` | Proxy errors |
| `-1401` — `-1499` | Job / Agent errors |
| `-1501` — `-1599` | Authentication / Authorization errors |
| `-1601` — `-1699` | Validation errors |
| `-1701` — `-1799` | System / Infrastructure errors |
| `-1801` — `-1899` | Scope / Not Implemented errors |

---

## 2. Success Code

| HTTP | `code` | `msg` | Mô tả |
|---|---|---|---|
| 200 | `0` | `"success"` | Yêu cầu thành công |

---

## 3. Profile Errors (-1001 — -1099)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 404 | `-1001` | `"Profile not found"` | `envId` không tồn tại | Kiểm tra lại envId; liệt kê profiles qua `/api/env/list` |
| 409 | `-1002` | `"Profile name already exists"` | Tên profile bị trùng | Dùng tên khác |
| 422 | `-1003` | `"Profile is currently active"` | Profile đang chạy, không thể xoá | Close profile trước: `POST /api/env/close` |
| 422 | `-1004` | `"Profile is in recycle bin"` | Profile đã bị xoá mềm | Restore trước hoặc thao tác trên recycle bin |
| 409 | `-1005` | `"Profile already open"` | Profile đã đang mở | Dùng `/api/env/active` để lấy debug port |
| 503 | `-1006` | `"Browser launch failed"` | Không thể khởi động browser | Kiểm tra log agent; thử lại sau |
| 422 | `-1007` | `"Max concurrent profiles reached"` | Đạt giới hạn 20 profiles active | Close một số profiles trước |
| 400 | `-1008` | `"Invalid proxy configuration"` | Proxy config sai format | Kiểm tra `proxyHost`, `proxyPort`, `proxyType` |
| 500 | `-1009` | `"Profile data directory error"` | Lỗi tạo/truy cập data dir | Kiểm tra disk space và permissions |
| 422 | `-1010` | `"Profile not in recycle bin"` | Cố restore profile chưa bị xoá | Chỉ restore profile có trạng thái `deleted` |

---

## 4. Group Errors (-1101 — -1199)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 404 | `-1101` | `"Group not found"` | `groupId` không tồn tại | Liệt kê groups qua `/api/envgroup/page` |
| 409 | `-1102` | `"Group name already exists"` | Tên group bị trùng | Dùng tên khác |
| 422 | `-1103` | `"Group has profiles"` | Cố xoá group còn profiles | Chuyển profiles sang group khác trước |
| 400 | `-1104` | `"Group name too long"` | Tên > 100 ký tự | Rút ngắn tên |

---

## 5. Tag Errors (-1201 — -1299)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 404 | `-1201` | `"Tag not found"` | `tagId` không tồn tại | Liệt kê tags qua `/api/envtag/all` |
| 409 | `-1202` | `"Tag name already exists"` | Tên tag bị trùng | Dùng tên khác |
| 400 | `-1203` | `"Tag name too long"` | Tên > 50 ký tự | Rút ngắn tên |
| 422 | `-1204` | `"Tag still assigned to profiles"` | Cố xoá tag đang dùng | Gỡ tag khỏi profiles trước hoặc dùng force delete |

---

## 6. Proxy Errors (-1301 — -1399)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 404 | `-1301` | `"Proxy not found"` | `proxyId` không tồn tại | Liệt kê proxies qua `/api/proxyInfo/page` |
| 409 | `-1302` | `"Proxy already exists"` | Proxy config trùng | Kiểm tra host:port đã được thêm |
| 400 | `-1303` | `"Invalid proxy type"` | `proxyType` không thuộc enum | Dùng: `http`, `https`, `socks4`, `socks5` |
| 422 | `-1304` | `"Proxy in use by profiles"` | Cố xoá proxy đang được dùng | Gỡ proxy khỏi profiles trước |
| 503 | `-1305` | `"Proxy connection test failed"` | Proxy không phản hồi | Kiểm tra proxy server đang chạy |

---

## 7. Job / Agent Errors (-1401 — -1499)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 404 | `-1401` | `"Job not found"` | `jobId` không tồn tại | Kiểm tra lại jobId |
| 422 | `-1402` | `"Job already completed"` | Cố cancel/retry job đã xong | Tạo job mới nếu cần |
| 422 | `-1403` | `"Job queue full"` | Queue đạt max capacity | Đợi jobs hiện tại hoàn thành |
| 503 | `-1404` | `"Agent not running"` | Background agent chưa start | Start agent: `bm agent start` |
| 503 | `-1405` | `"Agent connection timeout"` | Không kết nối được với agent | Kiểm tra agent health: `GET /health` |
| 500 | `-1406` | `"Job execution failed"` | Job thực thi thất bại | Xem job logs để biết chi tiết |
| 422 | `-1407` | `"Max retries exceeded"` | Job đã retry hết lần | Kiểm tra nguyên nhân từ job logs |

---

## 8. Authentication / Authorization Errors (-1501 — -1599)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 401 | `-1501` | `"Unauthorized: missing token"` | Không có Bearer token | Thêm header `Authorization: Bearer <token>` |
| 401 | `-1502` | `"Unauthorized: invalid token"` | Token sai hoặc đã hết hạn | Lấy token mới qua auth endpoint |
| 401 | `-1503` | `"Unauthorized: token expired"` | Token hết hạn | Rotate token: `POST /api/auth/refresh` |
| 403 | `-1504` | `"Forbidden: insufficient permissions"` | Token không đủ quyền | Dùng token có role phù hợp |
| 429 | `-1505` | `"Too many requests"` | Vượt rate limit (100 req/s default) | Giảm tần suất gọi; xem header `Retry-After` |

---

## 9. Validation Errors (-1601 — -1699)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 400 | `-1601` | `"Validation error: missing required field"` | Field bắt buộc bị thiếu | Xem `msg` để biết field nào |
| 400 | `-1602` | `"Validation error: invalid field type"` | Sai type (vd: string thay vì int) | Sửa type theo OpenAPI schema |
| 400 | `-1603` | `"Validation error: value out of range"` | Giá trị ngoài min/max | Xem schema để biết range |
| 400 | `-1604` | `"Validation error: invalid enum value"` | Giá trị không thuộc enum | Xem `msg` để biết enum values hợp lệ |
| 400 | `-1605` | `"Validation error: invalid JSON"` | Request body không phải JSON hợp lệ | Kiểm tra JSON syntax |
| 400 | `-1606` | `"Validation error: field too long"` | String vượt maxLength | Rút ngắn giá trị |
| 400 | `-1607` | `"Validation error: invalid page parameters"` | `pageNum` < 1 hoặc `pageSize` > 100 | Dùng pageNum ≥ 1, pageSize 1–100 |

---

## 10. System / Infrastructure Errors (-1701 — -1799)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 500 | `-1701` | `"Internal server error"` | Lỗi không xác định | Xem agent logs; báo bug |
| 503 | `-1702` | `"Database unavailable"` | SQLite locked hoặc corrupt | Kiểm tra file DB; xem `runbook.md` §DB |
| 503 | `-1703` | `"Service temporarily unavailable"` | Agent overloaded | Đợi và thử lại sau 5s |
| 507 | `-1704` | `"Insufficient storage"` | Disk đầy | Giải phóng disk; xem `runbook.md` §disk |
| 500 | `-1705` | `"Migration failed"` | DB migration lỗi khi startup | Kiểm tra migration logs; xem `runbook.md` §migration |

---

## 11. Scope / Not Implemented Errors (-1801 — -1899)

| HTTP | `code` | `msg` | Nguyên nhân | Cách xử lý |
|---|---|---|---|---|
| 501 | `-1801` | `"Not Implemented: cloud-only feature"` | Gọi cloud-only endpoint (vd: cleanCloud) | Dùng local equivalent; xem `scope-exceptions.md` |
| 501 | `-1802` | `"Not Implemented: feature planned for future version"` | Feature chưa implement | Xem roadmap trong `scope-exceptions.md` |

---

## 12. HTTP Status Code Mapping

| HTTP Status | Ý nghĩa | Khi nào dùng |
|---|---|---|
| 200 | OK | Request thành công |
| 400 | Bad Request | Validation error, sai format |
| 401 | Unauthorized | Thiếu hoặc sai token |
| 403 | Forbidden | Đủ auth nhưng thiếu permission |
| 404 | Not Found | Resource không tồn tại |
| 409 | Conflict | Duplicate resource, state conflict |
| 422 | Unprocessable Entity | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Lỗi server không xác định |
| 501 | Not Implemented | Feature out of scope |
| 503 | Service Unavailable | Agent/DB chưa sẵn sàng |
| 507 | Insufficient Storage | Disk đầy |

---

## 13. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
