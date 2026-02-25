# Configuration Keys Reference

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-18  
> **Mục đích**: Tài liệu tham chiếu chuẩn hóa về các configuration keys trong BrowserManager

---

## 1. MoreLogin Compatibility Mode Configuration

### 1.1 Canonical Configuration Keys

Sử dụng các key sau đây trong `appsettings.json` hoặc qua CLI:

```json
{
  "compatibility": {
    "enabled": true,
    "log_requests": true,
    "response_format": "morelogin"
  }
}
```

| Key | Type | Default | Mô tả |
|---|---|---|---|
| `compatibility.enabled` | boolean | `false` | Bật/tắt MoreLogin compatibility layer (30 compat endpoints) |
| `compatibility.log_requests` | boolean | `true` | Ghi log requests/responses khi compat mode active |
| `compatibility.response_format` | string | `"morelogin"` | Format response envelope: `"morelogin"` hoặc `"native"` |

### 1.2 CLI Commands

```bash
# Bật compat mode
bm config set compatibility.enabled true

# Tắt compat mode
bm config set compatibility.enabled false

# Bật logging cho compat requests
bm config set compatibility.log_requests true

# Kiểm tra trạng thái
bm agent status
# Output sẽ hiển thị: "compatibility_mode": true
```

---

## 2. Deprecated / Legacy Keys (KHÔNG dùng)

Các key sau đây **KHÔNG được sử dụng** trong code mới. Chúng chỉ được liệt kê để tránh nhầm lẫn:

| ❌ Deprecated Key | ✅ Canonical Key | Ghi chú |
|---|---|---|
| ~~`compat.morelogin_mode`~~ | `compatibility.enabled` | Tên cũ, không dùng |
| ~~`compat.morelogin_endpoints`~~ | `compatibility.enabled` | Tên cũ, không dùng |
| ~~`settings.compat_morelogin_mode`~~ | `compatibility.enabled` | Database column, không dùng trong code |
| ~~`compat.morelogin_envelope`~~ | `compatibility.response_format` | Tên cũ, không dùng |

### Migration từ legacy keys

Nếu code cũ sử dụng legacy keys, thay thế như sau:

```csharp
// ❌ Cũ (KHÔNG dùng)
if (config.GetValue<bool>("compat:morelogin_mode"))

// ✅ Mới (Canonical)
if (config.GetValue<bool>("compatibility:enabled"))
```

---

## 3. Các Configuration Keys Khác

### 3.1 Server & Port

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://127.0.0.1:40000"
      }
    }
  }
}
```

| Key | Type | Default | Mô tả |
|---|---|---|---|
| `Kestrel.Endpoints.Http.Url` | string | `"http://127.0.0.1:40000"` | Địa chỉ bind của Local API |

**Lưu ý**: Port 40000 là chuẩn để tương thích MoreLogin 1-1. Chỉ đổi sang port khác (19000, 41000...) nếu MoreLogin và BrowserManager chạy cùng lúc trên cùng máy.

### 3.2 Authentication

```json
{
  "auth": {
    "token": "your-secret-token-here",
    "require_auth": true
  }
}
```

| Key | Type | Default | Mô tả |
|---|---|---|---|
| `auth.token` | string | (auto-generated) | Bearer token để authenticate requests |
| `auth.require_auth` | boolean | `true` | Bắt buộc token auth (KHÔNG nên tắt) |

### 3.3 Security

```json
{
  "security": {
    "localhost_only": true,
    "rate_limit_enabled": true,
    "rate_limit_requests_per_minute": 100
  }
}
```

| Key | Type | Default | Mô tả |
|---|---|---|---|
| `security.localhost_only` | boolean | `true` | Chỉ cho phép requests từ localhost (KHÔNG nên tắt) |
| `security.rate_limit_enabled` | boolean | `true` | Bật rate limiting |
| `security.rate_limit_requests_per_minute` | integer | `100` | Số requests tối đa mỗi phút |

---

## 4. Configuration trong Code

### 4.1 Đọc Config (ASP.NET Core)

```csharp
// Trong Startup.cs / Program.cs
var compatEnabled = builder.Configuration.GetValue<bool>("compatibility:enabled", false);

if (compatEnabled)
{
    app.MapGroup("/api/env").MapCompatibilityEnvEndpoints();
    app.MapGroup("/api/envgroup").MapCompatibilityEnvGroupEndpoints();
    app.MapGroup("/api/envtag").MapCompatibilityEnvTagEndpoints();
    app.MapGroup("/api/proxyInfo").MapCompatibilityProxyEndpoints();
}
```

### 4.2 Hot-Reload Config Changes

Compatibility mode **có thể bật/tắt mà không cần restart agent** nếu sử dụng `IOptionsMonitor<T>`:

```csharp
public class CompatibilityService
{
    private readonly IOptionsMonitor<CompatibilityOptions> _options;
    
    public CompatibilityService(IOptionsMonitor<CompatibilityOptions> options)
    {
        _options = options;
    }
    
    public bool IsEnabled => _options.CurrentValue.Enabled;
}
```

---

## 5. Validation Rules

### 5.1 Bắt buộc

- ✅ `compatibility.enabled` phải là boolean
- ✅ `Kestrel.Endpoints.Http.Url` phải bắt đầu với `http://127.0.0.1:`
- ✅ `auth.token` phải có độ dài ≥ 32 ký tự

### 5.2 Khuyến nghị

- ⚠️ `security.localhost_only` nên giữ `true` (security)
- ⚠️ `auth.require_auth` nên giữ `true` (security)
- ⚠️ Port nên là 40000 (MoreLogin parity) trừ khi conflict

---

## 6. Environment Variables Override

Có thể override config qua environment variables (ASP.NET Core convention):

```bash
# Override compatibility.enabled
export compatibility__enabled=true

# Override Kestrel URL
export Kestrel__Endpoints__Http__Url=http://127.0.0.1:19000

# Override auth token
export auth__token=my-secret-token
```

**Lưu ý**: Dùng `__` (double underscore) để phân cấp (thay cho `:` hoặc `.`).

---

## 7. Configuration File Locations

| Platform | Location |
|---|---|
| Windows | `%ProgramData%\BrowserManager\config\appsettings.json` |
| Development | `<project-root>/appsettings.Development.json` |
| Production | `<install-dir>/config/appsettings.json` |

---

## 8. Checklist Standardization

Khi viết code hoặc documentation:

- [ ] Sử dụng `compatibility.enabled` (KHÔNG dùng `compat.morelogin_mode`)
- [ ] Sử dụng `compatibility.log_requests` (KHÔNG dùng `compat.log_requests`)
- [ ] Sử dụng `compatibility.response_format` (KHÔNG dùng `compat.morelogin_envelope`)
- [ ] Không tham chiếu database column `settings.compat_morelogin_mode` trong code
- [ ] CLI command luôn dùng `bm config set compatibility.enabled true`

---

*Tài liệu này là chuẩn chính thức về configuration keys. Mọi tài liệu khác phải tuân theo chuẩn này.*
