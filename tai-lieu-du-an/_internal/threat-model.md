# Threat Model — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Đặc tả threat model, attack surfaces, và security controls.  
> **Phương pháp**: STRIDE  
> **Người phê duyệt**: Security Lead + Tech Lead

---

## 1. Assets (Cần bảo vệ)

| Asset | Loại | Độ nhạy cảm | Mô tả |
|---|---|---|---|
| Bearer token (API auth) | Credential | 🔴 Critical | Token để xác thực Local API; nếu bị lộ → full API access |
| Proxy credentials | Credential | 🔴 Critical | Username/password của proxy servers |
| Profile data directories | Data | 🟠 High | Browser data (cookies, saved passwords, localStorage) |
| SQLite database (`browsermanager.db`) | Data | 🟠 High | Tất cả profile configs, job history, settings |
| Audit logs | Data | 🟡 Medium | Security audit trail |
| Job logs | Data | 🟡 Medium | Execution logs có thể chứa sensitive data |
| Automation scripts | Code | 🟡 Medium | Scripts chạy trên browser |
| App configuration | Config | 🟡 Medium | Port, paths, feature flags |

---

## 2. Attack Surfaces

### 2.1 Local API (HTTP localhost:40000)

**Mô tả**: HTTP server lắng nghe trên `127.0.0.1:40000`.  
**Accessible by**: Bất kỳ process nào chạy trên máy local.

| Threat | STRIDE | Mô tả | Control |
|---|---|---|---|
| Unauthorized API access | S (Spoofing) | Process khác trên máy gọi API không có token | Bearer token authentication |
| Token theft via log | I (Info Disclosure) | Token bị log ra stdout/file | Token không được log; masked trong audit |
| SSRF/local network pivot | E (Elevation) | API bị dùng để probe local network qua proxy endpoints | Input validation; proxy URL whitelist (optional) |
| Rate limit bypass | D (Denial of Service) | Flood requests làm agent không phản hồi | Rate limit: 100 req/s; configurable |
| Replay attack | S (Spoofing) | Capture và replay valid requests | `requestId` unique per request; idempotency keys |
| Privilege escalation via token scope | E (Elevation) | Token với role thấp hơn cố truy cập endpoint yêu cầu role cao hơn | Phase 2: validate token `role` claim on every request; reject with 403 if scope insufficient; log all 403 events in audit trail; token scope cannot be self-escalated |

### 2.2 CLI

**Mô tả**: Command-line tool chạy với quyền user.  
**Accessible by**: User đang đăng nhập vào Windows session.

| Threat | STRIDE | Mô tả | Control |
|---|---|---|---|
| Token leakage via CLI | I (Info Disclosure) | Token visible trong command history | Token không pass qua args; dùng env var hoặc config file |
| Privilege escalation | E (Elevation) | CLI chạy với elevated privileges không cần thiết | CLI chạy với user context; không cần admin |
| Config file tampering | T (Tampering) | Attacker sửa CLI config file | Config file permissions: read/write chỉ owner |

### 2.3 Desktop GUI

**Mô tả**: WPF/Electron app chạy trong Windows desktop session.  
**Accessible by**: User đang đăng nhập.

| Threat | STRIDE | Mô tả | Control |
|---|---|---|---|
| UI redress (clickjacking) | S (Spoofing) | Overlay GUI để lừa user click | Native desktop app; không embed web content |
| Sensitive data in memory | I (Info Disclosure) | Credentials visible trong process memory dump | DPAPI encryption; zero sensitive strings in memory khi có thể |
| Auto-update injection | T (Tampering) | Malicious update package | Code signing cho installer và updates |

### 2.4 Windows Service (Background Agent)

**Mô tả**: Windows Service hoặc System Tray process.  
**Accessible by**: Service control manager; user với LocalSystem hoặc user account.

| Threat | STRIDE | Mô tả | Control |
|---|---|---|---|
| Service account abuse | E (Elevation) | Agent chạy với over-privileged account | Principle of least privilege; chạy với dedicated user account |
| Service tampering | T (Tampering) | Attacker thay agent executable | Binary signed; Windows service config ACL |
| Malicious automation script | E (Elevation) | Script injection qua API/CLI | Script sandbox; no exec of user-supplied code directly |

### 2.5 SQLite Database File

**Mô tả**: File `browsermanager.db` trên disk.  
**Accessible by**: Bất kỳ process nào có read access đến file path.

| Threat | STRIDE | Mô tả | Control |
|---|---|---|---|
| DB file theft | I (Info Disclosure) | Copy DB file → đọc credentials | DPAPI encrypt tất cả credentials trong DB |
| DB tampering | T (Tampering) | Sửa DB file trực tiếp | File permissions; agent validate DB integrity |
| SQL injection | T (Tampering) | API input được dùng trong raw SQL | Parameterized queries only; ORM |

---

## 3. Security Controls

### 3.1 Authentication

| Control | Chi tiết | Scope |
|---|---|---|
| Bearer token | 256-bit random token; hash stored (SHA-256) in DB | Local API |
| Token auto-generated | Tạo ngẫu nhiên khi install; không hardcode | Installer |
| Token không expired | Valid vô thời hạn (local trust model); có thể rotate thủ công | Local API |
| Token rotation | `POST /api/agent/token/rotate`; old token invalid ngay lập tức | Local API |

**Token storage**:
- Agent: `settings` table, key `api_token_hash`, value = SHA-256 hex hash of plain token (verify only; plain token never stored)
- CLI: `%APPDATA%\BrowserManager\config.json` với DPAPI encryption (stores plain token for sending)
- GUI: Đọc từ agent API; không lưu riêng

### 3.2 Authorization

| Control | Chi tiết |
|---|---|
| Single-token model | Một token = full access (v1.0; multi-role in roadmap) |
| Localhost-only | API chỉ bind `127.0.0.1`; không bao giờ `0.0.0.0` |
| No unauthenticated endpoints | Chỉ `GET /health` là public |

### 3.3 Encryption

| Asset | Mechanism | Key source |
|---|---|---|
| API token (at rest) | SHA-256 hash in DB (agent); DPAPI-encrypted in config file (CLI) | Windows user credentials (CLI) |
| Proxy passwords (at rest) | DPAPI | Windows user credentials |
| DB file (at rest) | DPAPI-encrypted fields (individual columns) | Windows user credentials |
| Data in transit | HTTP localhost (không TLS trong v1.0; TLS optional v1.1+) | — |

**DPAPI Usage**:
```csharp
// Encrypt
byte[] encrypted = ProtectedData.Protect(
    Encoding.UTF8.GetBytes(plaintext),
    null,
    DataProtectionScope.CurrentUser
);

// Decrypt
byte[] decrypted = ProtectedData.Unprotect(
    encrypted,
    null,
    DataProtectionScope.CurrentUser
);
```

### 3.4 Rate Limiting

| Scope | Default | Config Key |
|---|---|---|
| Global requests/second | 100 | `api.rate_limit_rps` |
| Per IP requests/second | 100 (all local) | — |
| Burst allowance | 2× for 5s | — |

Rate limit exceeded → HTTP 429, code `-1505`, header `Retry-After: 1`.

### 3.5 Audit Logging

Tất cả security-relevant events được log vào `audit_logs` table:

| Event | Khi nào |
|---|---|
| `auth_success` | Token authentication thành công |
| `auth_failed` | Token authentication thất bại |
| `token_rotated` | Token bị rotate |
| `profile_created` | Profile được tạo |
| `profile_soft_deleted` | Profile bị xóa mềm |
| `profile_permanent_deleted` | Profile bị xóa vĩnh viễn |
| `rate_limit_triggered` | Rate limit được kích hoạt |
| `service_started` | Agent/service khởi động |
| `service_stopped` | Agent/service dừng |

**Audit log format**:
```json
{
  "id": 1,
  "event_type": "auth_failed",
  "actor": "api",
  "resource_type": null,
  "resource_id": null,
  "details": {
    "ip": "127.0.0.1",
    "reason": "invalid_token"
  },
  "ip_address": "127.0.0.1",
  "timestamp": "2026-02-20T10:00:00Z"
}
```

### 3.6 Input Validation

- Tất cả request body được validate theo `openapi.yaml` schema trước khi xử lý
- Parameterized queries cho tất cả DB operations
- Path traversal prevention: `data_dir` và file paths được sanitize
- Max request body size: 1 MB

### 3.7 Secrets in Logs

| Rule |
|---|
| Token không bao giờ xuất hiện trong logs |
| Proxy passwords không bao giờ xuất hiện trong logs |
| Audit logs KHÔNG log request body (chỉ log event metadata) |
| Job logs không được log sensitive environment variables |

---

## 4. Secure Defaults

Danh sách các cài đặt mặc định an toàn:

| Setting | Default value | Lý do |
|---|---|---|
| `api.bind_address` | `127.0.0.1` | Không expose ra mạng |
| `api.port` | `40000` | Fixed; không conflict với common services |
| `api.rate_limit_rps` | `100` | Ngăn flood |
| `api.require_auth` | `true` | Auth required by default |
| `agent.max_concurrent_browsers` | `20` | Ngăn resource exhaustion |
| `agent.log_retention_days` | `30` | Balance privacy/debugging |
| `recycle_bin_retention_days` | `30` | Không giữ data vô hạn |
| Auto-start service on boot | `true` | User-expected; không cần manual start |
| Allow remote connections | `false` | Local-only by default |
| TLS on local API | `false` (v1.0) | localhost; TLS optional in v1.1+ |

---

## 5. Out-of-Scope Security (v1.0)

| Tính năng | Lý do out-of-scope | Kế hoạch |
|---|---|---|
| TLS trên local API | localhost trust model đủ cho v1.0 | v1.1+ optional |
| Multi-user access control | Single-user local app | Future SaaS roadmap |
| Hardware security key (YubiKey) | Over-engineering cho local app | Not planned |
| Remote attestation | Out of scope | Not planned |
| Fingerprint/anti-detect features | Ethical + compliance exclusion | Permanently excluded |

---

## 6. Incident Response

### 6.1 Nếu Token bị lộ

1. Rotate token ngay: `POST /api/agent/token/rotate` hoặc `bm agent token rotate`
2. Kiểm tra audit logs để xem có unauthorized access không
3. Nếu có unauthorized access: xem `runbook.md` §security-incident

### 6.2 Nếu DB file bị copy

1. Dữ liệu nhạy cảm (token, proxy passwords) được DPAPI encrypt → safe nếu attacker không có Windows credentials của user
2. Non-sensitive data (profile configs, names) có thể đọc được
3. Action: Rotate token; review proxy credentials; notify user

---

## 7. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
