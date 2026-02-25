# 12 — API Compatibility Layer

> **Phiên bản**: 1.1 | **Ngày**: 2026-02-18 | **Trạng thái**: Review  
> **EPIC tương ứng**: P3 — API Compatibility (MoreLogin-style endpoint mapping)

---

## 1. Mục tiêu tài liệu

Mô tả **Compatibility Layer** — một tầng mapping endpoint giúp:
- Backend được viết theo style MoreLogin Local API (`/api/env/*`) có thể gọi BrowserManager **mà không cần sửa code backend**.
- Thiết kế như một **reverse proxy / adaptor middleware** trong cùng ASP.NET Core agent.
- Giúp migration backend cũ sang BrowserManager dễ dàng hơn.

> **Lưu ý**: Layer này là **tùy chọn** (P3, không bắt buộc). Nó **không thay đổi** API bản địa của BrowserManager (`/api/profiles/*`). Cả hai style đều hoạt động song song.

---

## 2. Tổng quan Mapping

### 2.1 Nguyên tắc mapping

```
Request đến: POST /api/env/create/quick
                    ↓ Compatibility Middleware
Chuyển thành: POST /api/profiles  (internal)
                    ↓
Response từ BrowserManager → Transform ngược lại
                    ↓
Trả về client: MoreLogin-style JSON format
```

### 2.2 Bảng mapping tổng hợp

| MoreLogin Endpoint | BrowserManager Endpoint | Method | Ghi chú |
|---|---|---|---|
| `POST /api/env/create/quick` | `POST /api/profiles` | POST | Tạo profile nhanh |
| `POST /api/env/create/advanced` | `POST /api/profiles` | POST | Tạo profile đầy đủ |
| `POST /api/env/start` | `POST /api/sessions/start` | POST | Launch session |
| `POST /api/env/close` | `POST /api/sessions/{id}/stop` | POST | Stop session |
| `POST /api/env/active` | `GET /api/sessions?status=running` | GET | Danh sách session đang chạy |
| `POST /api/env/detail` | `GET /api/profiles/{id}` | GET | Chi tiết profile |
| `POST /api/env/list` | `GET /api/profiles` | GET | Danh sách profiles |
| `POST /api/env/update` | `PATCH /api/profiles/{id}` | PATCH | Cập nhật profile |
| `POST /api/env/removeToRecycleBin/batch` | `DELETE /api/profiles` (batch) | DELETE | Chuyển profiles vào Trash (soft delete) |
| `POST /api/env/page` | `GET /api/profiles?page=&page_size=` | GET | Phân trang |
| `POST /api/env/reopen` | `POST /api/sessions/start` | POST | Reopen session |
| `POST /api/env/getAllDebugInfo` | `POST /api/sessions/debug-info` | POST | CDP debug ports |
| `POST /api/env/getAllProcessIds` | `POST /api/sessions/debug-info` | POST | PID tất cả session |
| `POST /api/env/getAllScreen` | Native (no alias) | POST | Thông tin màn hình/monitor |
| `POST /api/env/closeAll` | `POST /api/sessions/close-all` | POST | Stop all sessions |
| `POST /api/envgroup/list` | `GET /api/profiles?group=` | GET | Filter by group |
| `POST /api/proxyInfo/add` | `POST /api/proxies` | POST | Thêm proxy |
| `POST /api/proxyInfo/list` | `GET /api/proxies` | GET | Danh sách proxy |
| `POST /api/proxyInfo/delete` | `DELETE /api/proxies/{id}` | DELETE | Xoá proxy |

---

## 3. Field Mapping — Request Transformation

### 3.1 `POST /api/env/create/quick` → `POST /api/profiles`

**MoreLogin request format:**
```json
{
  "name": "Profile A",
  "groupId": "group-uuid",
  "proxyMethod": 2,
  "proxyType": "socks5",
  "host": "proxy.example.com",
  "port": "1080",
  "proxyUserName": "user",
  "proxyPassword": "pass",
  "browserFingerPrint": {
    "coreVersion": "120",
    "ostype": "Windows",
    "osVersion": "10",
    "resolution": "1920_1080"
  }
}
```

**Transformed to BrowserManager format:**
```json
{
  "name": "Profile A",
  "group_name": "{resolved from groupId}",
  "proxy": {
    "type": "socks5",
    "host": "proxy.example.com",
    "port": 1080,
    "username": "user",
    "password": "pass"
  }
}
```

> **Ghi chú**: Các trường `browserFingerPrint` (coreVersion, resolution, ostype…) được lưu vào `profiles.metadata` JSON blob nếu muốn preserve, nhưng không ảnh hưởng browser launch (vì BrowserManager không hỗ trợ fingerprint emulation).

### 3.2 `POST /api/env/start` → `POST /api/sessions/start`

**MoreLogin request:**
```json
{
  "envId": "profile-uuid"
}
```

**Transformed:**
```json
{
  "profile_id": "profile-uuid",
  "headless": false
}
```

**MoreLogin response format:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "profile-uuid",
    "http": "127.0.0.1:9222",
    "ws": "ws://127.0.0.1:9222/json/version",
    "webdriver": "path/to/chromedriver.exe",
    "seleniumVersion": "4.0"
  }
}
```

**BrowserManager native response (được transform ra MoreLogin format):**
```json
// BrowserManager native:
{
  "data": {
    "session_id": "sess-uuid",
    "profile_id": "profile-uuid",
    "debug_port": 9222,
    "pid": 12345,
    "status": "running"
  }
}

// → Transformed to MoreLogin format:
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "profile-uuid",
    "http": "127.0.0.1:9222",
    "ws": "ws://127.0.0.1:9222/json/version",
    "webdriver": "C:\\Program Files\\BrowserManager\\chromedriver.exe",
    "seleniumVersion": "4.0"
  }
}
```

### 3.3 `POST /api/env/getAllDebugInfo` → `POST /api/sessions/debug-info`

**MoreLogin response format:**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "profile-uuid",
      "http": "127.0.0.1:9222",
      "ws": "ws://127.0.0.1:9222/json/version"
    }
  ]
}
```

**Transform from BrowserManager native:**
```json
// BrowserManager native:
{
  "data": [
    {"session_id": "...", "profile_id": "uuid", "debug_port": 9222, "cdp_url": "http://127.0.0.1:9222"}
  ]
}

// → MoreLogin format:
{
  "code": 0,
  "msg": "success",
  "data": [
    {"id": "uuid", "http": "127.0.0.1:9222", "ws": "ws://127.0.0.1:9222/json/version"}
  ]
}
```

---

## 4. Response Envelope Transformation

MoreLogin dùng format response khác với BrowserManager:

| Trường | MoreLogin format | BrowserManager format |
|---|---|---|
| Success wrapper | `{"code": 0, "msg": "success", "data": {...}}` | `{"data": {...}, "request_id": "...", "timestamp": "..."}` |
| Error wrapper | `{"code": -1, "msg": "error message", "data": null}` | `{"error": "error_code", "message": "...", "details": [...]}` |

**Middleware transform logic:**
```csharp
public class CompatibilityResponseTransformer
{
    /// <summary>
    /// Transforms BrowserManager native response into MoreLogin compat envelope.
    /// Output: { code, msg, data, requestId } (camelCase — parity with MoreLogin API format).
    /// </summary>
    public static object ToMoreLoginFormat(
        object bmResponse,
        bool isError,
        string requestId = null,
        string errorMsg = null)
    {
        var rid = requestId ?? Guid.NewGuid().ToString("N")[..12];

        if (isError)
            return new { code = -1, msg = errorMsg ?? "error", data = (object)null, requestId = rid };

        return new { code = 0, msg = "success", data = bmResponse, requestId = rid };
    }
}
```

> **G1 Closure note**: Compat endpoint middleware inject `HttpContext.TraceIdentifier` làm `requestId` (camelCase), đảm bảo format MoreLogin-compatible. Native endpoint giữ `request_id` (snake_case) theo tiêu chuẩn BrowserManager.

---

## 5. Implementation — ASP.NET Core Middleware

### 5.1 Route Registration

Compatibility routes được đăng ký **chỉ khi** config `compatibility.enabled = true`:

```csharp
// Program.cs / Startup
if (config.GetValue<bool>("compatibility:enabled"))
{
    app.MapGroup("/api/env").MapCompatibilityEnvEndpoints();
    app.MapGroup("/api/envgroup").MapCompatibilityEnvGroupEndpoints();
    app.MapGroup("/api/proxyInfo").MapCompatibilityProxyEndpoints();
    
    logger.LogInformation("API Compatibility Layer enabled (MoreLogin-style endpoints)");
}
```

### 5.2 Handler ví dụ — Create Quick

```csharp
public static class CompatibilityEnvEndpoints
{
    public static RouteGroupBuilder MapCompatibilityEnvEndpoints(this RouteGroupBuilder group)
    {
        group.MapPost("/create/quick", async (
            HttpContext ctx,
            IProfileService profileSvc,
            IGroupService groupSvc,
            [FromBody] MoreLoginCreateQuickDto dto) =>
        {
            // Transform MoreLogin format → BrowserManager format
            var createDto = new ProfileCreateDto
            {
                Name = dto.Name,
                GroupName = dto.GroupId != null 
                    ? await groupSvc.GetGroupNameAsync(dto.GroupId) 
                    : null,
                Proxy = dto.ProxyType != null ? new ProxyConfigDto
                {
                    Type = dto.ProxyType,
                    Host = dto.Host,
                    Port = int.Parse(dto.Port ?? "0"),
                    Username = dto.ProxyUserName,
                    Password = dto.ProxyPassword
                } : null
            };

            try
            {
                var profile = await profileSvc.CreateAsync(createDto);
                
                // Transform BrowserManager response → MoreLogin format
                return Results.Ok(new
                {
                    code = 0,
                    msg = "success",
                    data = new { id = profile.Id, name = profile.Name }
                });
            }
            catch (ConflictException ex)
            {
                return Results.Ok(new { code = -1, msg = ex.Message, data = (object)null });
            }
        });

        group.MapPost("/start", async (
            HttpContext ctx,
            ISessionManager sessionMgr,
            [FromBody] MoreLoginStartDto dto) =>
        {
            var session = await sessionMgr.StartAsync(new SessionStartDto { ProfileId = dto.EnvId });
            return Results.Ok(new
            {
                code = 0,
                msg = "success",
                data = new
                {
                    id = dto.EnvId,
                    http = $"127.0.0.1:{session.DebugPort}",
                    ws = $"ws://127.0.0.1:{session.DebugPort}/json/version",
                    webdriver = ChromeDriverLocator.GetPath(),
                    seleniumVersion = "4.0"
                }
            });
        });

        // ... các endpoints khác

        return group;
    }
}
```

### 5.3 MoreLogin DTO models

```csharp
// DTOs cho MoreLogin-style request bodies
public record MoreLoginCreateQuickDto(
    string Name,
    string? GroupId,
    int? ProxyMethod,
    string? ProxyType,
    string? Host,
    string? Port,
    string? ProxyUserName,
    string? ProxyPassword,
    MoreLoginFingerprint? BrowserFingerPrint
);

public record MoreLoginFingerprint(
    string? CoreVersion,
    string? OsType,
    string? OsVersion,
    string? Resolution
);

public record MoreLoginStartDto(string EnvId);
public record MoreLoginCloseDto(string Id);
public record MoreLoginDetailDto(string Id);
```

---

## 6. Configuration

### 6.1 Settings trong `appsettings.json`

```json
{
  "compatibility": {
    "enabled": false,
    "log_requests": true,
    "response_format": "morelogin"
  }
}
```

### 6.2 Bật/Tắt qua CLI

```bash
# Bật Compatibility Layer
bm config set compatibility.enabled true

# Kiểm tra
bm agent status
# Output sẽ hiển thị: "compatibility_mode": true
```

### 6.3 Settings trong GUI

Trong `Settings > Advanced`:
```
─── API Compatibility Mode ────────────────────
[ ] Enable MoreLogin-style endpoints (/api/env/*)
    ⚠ Only enable if your backend uses MoreLogin API style.
    Native /api/profiles/* endpoints remain unaffected.
[💾 Save]
```

---

## 7. Supported Endpoints Matrix

| Category | MoreLogin Path | Status | Ghi chú |
|---|---|---|---|
| Profile | `POST /api/env/create/quick` | ✅ Implemented | |
| Profile | `POST /api/env/create/advanced` | ✅ Implemented | Extra fields stored in metadata |
| Profile | `POST /api/env/list` | ✅ Implemented | |
| Profile | `POST /api/env/page` | ✅ Implemented | |
| Profile | `POST /api/env/detail` | ✅ Implemented | |
| Profile | `POST /api/env/update` | ✅ Implemented | |
| Profile | `POST /api/env/removeToRecycleBin/batch` | ✅ Implemented | Soft delete (goes to trash) |
| Session | `POST /api/env/start` | ✅ Implemented | Returns CDP debug port in MoreLogin format |
| Session | `POST /api/env/close` | ✅ Implemented | |
| Session | `POST /api/env/active` | ✅ Implemented | |
| Session | `POST /api/env/reopen` | ✅ Implemented | Same as start |
| Session | `POST /api/env/getAllDebugInfo` | ✅ Implemented | |
| Session | `POST /api/env/getAllProcessIds` | ✅ Implemented | |
| Session | `POST /api/env/getAllScreen` | ✅ Implemented | |
| Session | `POST /api/env/closeAll` | ✅ Implemented | |
| Group | `POST /api/envgroup/list` | ✅ Implemented | Mapped to group filter |
| Proxy | `POST /api/proxyInfo/add` | ✅ Implemented | |
| Proxy | `POST /api/proxyInfo/list` | ✅ Implemented | |
| Proxy | `POST /api/proxyInfo/delete` | ✅ Implemented | |
| Cache | `POST /api/env/clearCache` (local) | ✅ Implemented | Maps to `/api/profiles/{id}/clear-cache` |
| **Not Supported** | Any fingerprint/anti-detect endpoints | ❌ Not implemented | Out of scope |
| **Not Supported** | `POST /api/env/arrangeWindows` | ❌ Not implemented | Phase 2 optionally |
| **Not Supported** | Cloud cache endpoints | ❌ Not applicable | Self-hosted only |

---

## 8. Migration Guide: từ MoreLogin Backend sang BrowserManager

### Bước 1: Chuẩn bị

```bash
# Bật Compatibility Layer trong BrowserManager
bm config set compatibility.enabled true

# Kiểm tra mapping endpoint hoạt động
curl -X POST http://127.0.0.1:40000/api/env/list \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "pageSize": 10}'
```

### Bước 2: Thay đổi URL trong backend

```python
# Trước (MoreLogin — cài trên cùng máy, dùng port 40000 mặc định):
BASE_URL = "http://127.0.0.1:40000"  # MoreLogin default

# Sau (BrowserManager — cũng dùng port 40000 mặc định, MoreLogin-compatible):
BASE_URL = "http://127.0.0.1:40000"  # BrowserManager default (MoreLogin-compatible)
# Thêm token auth header (MoreLogin dùng query param; BrowserManager dùng Bearer header)
HEADERS = {"Authorization": "Bearer YOUR_BM_TOKEN"}
# Lưu ý: Nếu MoreLogin và BrowserManager đồng thời chạy trên cùng máy,
# cần đổi một trong hai sang port khác (vd: BrowserManager dùng port 19000 hoặc 41000).
```

### Bước 3: Kiểm tra response format

Responses từ BrowserManager Compatibility Layer **khớp 1-1** với MoreLogin format (`code: 0, msg, data`).  
Không cần thay đổi code parse response trong backend.

### Bước 4: Xử lý chênh lệch nhỏ

| Điểm khác biệt | MoreLogin | BrowserManager (Compat Mode) | Cách xử lý |
|---|---|---|---|
| Token auth | Query param `?local_api_key=...` hoặc header | Header `Authorization: Bearer ...` | Sửa backend thêm header |
| Fingerprint fields | Trả đầy đủ UA, resolution... | Fields trong `metadata` JSON blob | Parse `metadata` nếu cần |
| `delete` → permanent | Xoá ngay | Soft delete → trash | Sử dụng `/api/env/removeToRecycleBin/batch` (không hỗ trợ xóa vĩnh viễn ngay lập tức) |

---

## 9. Definition of Done (DoD) — Compatibility Layer

- [ ] Tất cả endpoints trong "Implemented" matrix hoạt động đúng.
- [ ] Response format khớp MoreLogin (`code: 0, msg, data`).
- [ ] Backend MoreLogin-style gọi `create_quick → start → getAllDebugInfo → close` thành công end-to-end.
- [ ] Compatibility mode tắt mặc định; bật qua config mà không restart agent (hot-reload).
- [ ] Log request/response khi `compatibility.log_requests = true`.
- [ ] Native `/api/profiles/*` endpoints không bị ảnh hưởng khi Compatibility Mode bật.
- [ ] Integration test: chạy MoreLogin-style script mẫu với BrowserManager backend.

---

## 7. Ghi chú: Browser Synchronizer

**MoreLogin** có tính năng batch control / multi-browser sync cho phép điều khiển nhiều browser profile cùng lúc từ một nguồn.

**BrowserManager** implement tương đương qua **CDP relay mechanism**:

| Tính năng | MoreLogin | BrowserManager |
|---|---|---|
| Multi-browser sync | Proprietary batch control | CDP relay qua `POST /api/sync/event` |
| Mouse/Keyboard sync | Built-in | `Input.dispatchMouseEvent` / `Input.dispatchKeyEvent` via CDP |
| Navigation sync | Built-in | `Page.navigate` via CDP |
| Leader/Follower model | Có | ✅ Có — spec tại `08-desktop-gui.md` §4E |
| API control | Private API | `POST /api/sync/start`, `/stop`, `/status`, `/event` |

Xem spec đầy đủ tại:
- **GUI spec**: `08-desktop-gui.md` §4E
- **API spec**: `openapi.yaml` `/api/sync/*`
- **Scope**: `scope.md` §M12

---

*Tài liệu kết thúc bộ spec BrowserManager v1.0*
