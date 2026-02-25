# 05 — CLI Specification

> **Phiên bản**: 1.1 | **Ngày**: 2026-02-18 | **Trạng thái**: Review  
> **EPIC tương ứng**: G — CLI

---

## 1. Mục tiêu tài liệu

Đặc tả đầy đủ CLI tool `bm`:
- Danh sách lệnh (commands).
- Tham số (flags/options).
- Output format (JSON chuẩn).
- Exit codes.
- Cách cấu hình kết nối đến Agent.
- Packaging và phân phối.

---

## 2. Tổng quan CLI

CLI tool `bm` (BrowserManager CLI):
- Là `.NET single-file executable` đóng gói thành `bm.exe`.
- Giao tiếp với **Background Agent** qua Local API HTTP.
- Output mặc định: **JSON** (machine-readable).
- Có flag `--pretty` để in JSON đẹp (human-readable).
- Có flag `--raw` để in response thô không wrapped.

---

## 3. Cấu hình kết nối Agent

### 3.1 Ưu tiên cấu hình (cao → thấp)

1. **CLI flags**: `--agent-url`, `--token`
2. **Environment variables**: `BM_AGENT_URL`, `BM_TOKEN`
3. **Config file**: `%APPDATA%\BrowserManager\config.json`

### 3.2 Config file format

```json
{
  "agent_url": "http://127.0.0.1:40000",
  "token": "<DPAPI-encrypted-at-rest>"
}
```

> **Lưu ý bảo mật**: Trường `token` được DPAPI-encrypted at rest khi lưu vào file. CLI tự động encrypt/decrypt transparently — plain token không bao giờ xuất hiện dạng plaintext trong file.

### 3.3 Lệnh cấu hình

```bash
# Cài đặt kết nối
bm config set-url http://127.0.0.1:40000
bm config set-token <token>

# Xem config hiện tại (token được mask)
bm config show

# Test kết nối
bm config test
```

---

## 4. Danh Sách Lệnh Đầy Đủ

### 4.1 Global flags

```
Global Options:
  --agent-url <url>    Agent URL (default: http://127.0.0.1:40000)
  --token <token>      API token
  --pretty             Pretty-print JSON output
  --raw                Raw JSON output (no envelope)
  --no-color           Disable color output
  --timeout <sec>      Request timeout (default: 30)
  -h, --help           Show help
  -v, --version        Show version
```

---

### 4.2 `bm health` — Kiểm tra agent

```bash
bm health
```

Output:
```json
{
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "sessions": {"active": 2, "max": 10},
    "jobs": {"queued": 0, "running": 2}
  }
}
```

Exit code: `0` nếu healthy, `1` nếu không thể kết nối.

---

### 4.3 `bm profiles` — Quản lý Profile

#### `bm profiles create`

```bash
bm profiles create \
  --name "Profile A" \
  --group "Group 1" \
  --proxy-type socks5 \
  --proxy-host proxy.example.com \
  --proxy-port 1080 \
  --proxy-user user \
  --proxy-pass secret \
  --start-url https://example.com \
  --tag ecommerce \
  --tag test
```

**Flags:**

| Flag | Type | Required | Mô tả |
|---|---|---|---|
| `--name` | string | ✅ | Tên profile (unique) |
| `--group` | string | | Nhóm |
| `--tag` | string[] | | Tags (dùng nhiều lần) |
| `--proxy-type` | enum | | `http\|https\|socks5\|ssh` |
| `--proxy-host` | string | | Proxy host |
| `--proxy-port` | int | | Proxy port |
| `--proxy-user` | string | | Proxy username |
| `--proxy-pass` | string | | Proxy password |
| `--start-url` | string | | Start URL |
| `--headless` | bool | | Headless mặc định |
| `--ext` | string[] | | Extension IDs |

Output: Profile object JSON + `"status": "created"`.

#### `bm profiles list`

```bash
bm profiles list [--group GROUP] [--tag TAG] [--q QUERY] [--page 1] [--page-size 20]
```

Output:
```json
{
  "data": {
    "items": [
      {"id": "uuid", "name": "Profile A", "group_name": "Group 1", "status": "inactive", ...}
    ],
    "total": 42,
    "page": 1
  }
}
```

#### `bm profiles get <id>`

```bash
bm profiles get 550e8400-e29b-41d4-a716-446655440000
```

#### `bm profiles update <id>`

```bash
bm profiles update <id> --name "New Name" --proxy-host new.proxy.com
```

Chỉ cần truyền các field muốn thay đổi (PATCH semantic).

#### `bm profiles delete <id>`

```bash
bm profiles delete <id> [--force]
```

- `--force`: xoá kể cả khi đang có session (dừng session trước).
- Mặc định: xoá mềm (đưa vào Recycle Bin, khôi phục được trong 7 ngày).

Prompt xác nhận: `"Delete profile 'Profile A'? It will be moved to trash (recoverable for 7 days). [y/N]:"` (bypass với `-y`/`--yes`).

#### `bm profiles permanent-delete <id>`

```bash
bm profiles permanent-delete <id> [-y]
```

Xoá vĩnh viễn, không qua trash. Prompt: `"Permanently delete 'Profile A'? This is IRREVERSIBLE. [y/N]:"`.

#### `bm profiles restore <id>`

```bash
bm profiles restore <id>
```

Khôi phục profile từ thùng rác. Chỉ khả dụng trong vòng 7 ngày kể từ khi xoá.

#### `bm profiles trash`

```bash
bm profiles trash [--show-deadline]
```

Danh sách profiles trong Recycle Bin kèm ngày hết hạn khôi phục.

#### `bm profiles clear-cache <id>`

```bash
bm profiles clear-cache <id> \
  [--type cookies] \
  [--type local_storage] \
  [--type indexeddb] \
  [--type extension_data] \
  [--all]
```

Xoá cache dữ liệu của profile. Dùng `--all` để xoá tất cả loại.

**Flags:**

| Flag | Mô tả |
|---|---|
| `--type` | Loại cache cần xoá (dùng nhiều lần). Giá trị: `cookies`, `local_storage`, `indexeddb`, `extension_data` |
| `--all` | Xoá tất cả loại cache |

Output:
```json
{
  "data": {
    "cleared": ["cookies", "local_storage"],
    "bytes_freed": 1048576,
    "cleared_at": "2026-02-18T10:30:00Z"
  }
}
```

#### `bm profiles batch-update`

```bash
bm profiles batch-update \
  --profiles uuid1,uuid2,uuid3 \
  [--set-group "New Group"] \
  [--set-proxy proxy-uuid] \
  [--add-tag campaign-x] \
  [--remove-tag old-tag] \
  [--set-start-url https://example.com]
```

Cập nhật hàng loạt nhiều profiles trong một lệnh.

**Flags:**

| Flag | Mô tả |
|---|---|
| `--profiles` | Danh sách profile IDs cách nhau bởi dấu phẩy |
| `--set-group` | Đặt group mới |
| `--set-proxy` | Gán proxy ID |
| `--add-tag` | Thêm tag (dùng nhiều lần) |
| `--remove-tag` | Xoá tag (dùng nhiều lần) |
| `--set-start-url` | Đặt start URL |

#### `bm profiles clone <id>`

```bash
bm profiles clone <id> [--name "Profile A Copy"] [--mode metadata_only|full_copy]
```

#### `bm profiles export <id>`

```bash
bm profiles export <id> \
  --output ./exports/profile-a.bm-profile.zip \
  [--include-data] \
  [--include-secrets]
```

#### `bm profiles import <file>`

```bash
bm profiles import ./exports/profile-a.bm-profile.zip [--name-override "New Name"]
```

---

### 4.4 `bm sessions` — Quản lý Session

#### `bm sessions start`

```bash
bm sessions start --profile <id|name> [--headless] [--wait-ready]
```

**Flags:**

| Flag | Mô tả |
|---|---|
| `--profile` | Profile ID hoặc name |
| `--headless` | Chạy headless (không UI) |
| `--wait-ready` | Block cho đến khi session `running` |

Output:
```json
{
  "data": {
    "session_id": "uuid",
    "profile_id": "uuid",
    "status": "launching",
    "debug_port": 9222,
    "pid": 12345
  }
}
```

#### `bm sessions stop <id>`

```bash
bm sessions stop <session_id> [--force]
```

#### `bm sessions close-all`

```bash
bm sessions close-all [--force]
```

Dừng tất cả sessions đang chạy. Hữu ích khi cần giải phóng tài nguyên nhanh.

Output:
```json
{
  "data": {
    "stopped_count": 5,
    "errors": []
  }
}
```

#### `bm sessions debug-info`

```bash
bm sessions debug-info [--format table|json]
```

Lấy thông tin CDP debug port của tất cả sessions đang chạy.

Output (table format):
```
SESSION_ID   PROFILE         PID     DEBUG_PORT  CDP_URL
abc123...    Profile A       12345   9222        http://127.0.0.1:9222
def456...    Profile B       12346   9223        http://127.0.0.1:9223
```

Output (JSON format):
```json
{
  "data": [
    {"session_id": "abc123", "profile_name": "Profile A", "pid": 12345, "debug_port": 9222, "cdp_url": "http://127.0.0.1:9222"}
  ]
}
```

#### `bm sessions list`

```bash
bm sessions list [--status running|stopped|crashed]
```

#### `bm sessions get <id>`

```bash
bm sessions get <session_id>
```

---

### 4.5 `bm jobs` — Quản lý Jobs

#### `bm jobs list`

```bash
bm jobs list [--status queued|running|completed|failed] [--profile <id>] [--limit 20]
```

#### `bm jobs get <id>`

```bash
bm jobs get <job_id> [--with-logs] [--log-level INFO]
```

Output (với `--with-logs`):
```json
{
  "data": {
    "id": "uuid",
    "type": "run_script",
    "status": "completed",
    "started_at": "...",
    "completed_at": "...",
    "result": {"status": "ok"},
    "logs": [
      {"timestamp": "...", "level": "INFO", "message": "Script started"},
      {"timestamp": "...", "level": "INFO", "message": "Done"}
    ]
  }
}
```

#### `bm jobs cancel <id>`

```bash
bm jobs cancel <job_id>
```

#### `bm jobs run`

```bash
bm jobs run \
  --script <script_id> \
  --profile <profile_id|name> \
  [--param key=value] \
  [--param another=value] \
  [--timeout 120] \
  [--wait]
```

Flags:

| Flag | Mô tả |
|---|---|
| `--script` | Script ID (từ registry) |
| `--profile` | Profile ID hoặc name |
| `--param` | Key=value params (có thể dùng nhiều lần) |
| `--timeout` | Timeout giây |
| `--wait` | Block cho đến khi job hoàn thành |
| `--follow` | Stream logs realtime khi đang chạy |

Ví dụ với `--follow`:
```bash
bm jobs run --script login-script --profile "Profile A" --wait --follow

# Output (streaming):
# [10:30:00] INFO  Script started
# [10:30:01] INFO  Navigating to https://example.com
# [10:30:03] INFO  Login successful
# [10:30:03] INFO  Script completed
# {"data": {"job_id": "uuid", "status": "completed", "result": {...}}}
```

---

### 4.6 `bm scripts` — Quản lý Scripts

#### `bm scripts list`

```bash
bm scripts list
```

Output: danh sách scripts trong registry.

#### `bm scripts add`

```bash
bm scripts add \
  --id login-script \
  --name "Login Script" \
  --file ./scripts/login.js \
  [--description "Performs login flow"] \
  [--timeout 120] \
  [--max-retries 2]
```

#### `bm scripts remove <id>`

```bash
bm scripts remove login-script
```

#### `bm scripts show <id>`

```bash
bm scripts show login-script
```

---

### 4.7 `bm proxies` — Quản lý Proxies

```bash
# Thêm proxy
bm proxies add \
  --label "US Proxy 1" \
  --type socks5 \
  --host proxy.example.com \
  --port 1080 \
  --user user \
  --pass secret

# Test proxy
bm proxies test <proxy_id>

# Danh sách
bm proxies list

# Xoá
bm proxies delete <proxy_id>
```

---

### 4.8 `bm extensions` — Quản lý Extensions

#### `bm extensions list`

```bash
bm extensions list
```

Danh sách extensions trong registry trung tâm.

#### `bm extensions add`

```bash
bm extensions add \
  --source "https://chrome.google.com/webstore/detail/adblock/..." \
  [--name "AdBlock"]
```

Thêm extension vào registry từ Chrome Web Store URL.

#### `bm extensions remove <id>`

```bash
bm extensions remove <ext_registry_id>
```

Xoá extension khỏi registry (không ảnh hưởng profiles đã assign).

#### `bm extensions assign`

```bash
bm extensions assign <ext_registry_id> \
  --profiles uuid1,uuid2,uuid3 \
  [--action add|remove]
```

Gán hoặc gỡ extension cho nhiều profiles cùng lúc.

---

### 4.9 `bm agent` — Điều khiển Agent

```bash
# Status
bm agent status

# Token rotate
bm agent token rotate

# Shutdown
bm agent shutdown [--graceful] [--timeout 30]
```

---

## 5. Exit Codes

| Code | Nghĩa |
|---|---|
| `0` | Thành công |
| `1` | Lỗi chung / không xác định |
| `2` | Lỗi tham số / validation |
| `3` | Không kết nối được Agent |
| `4` | Unauthorized (401) |
| `5` | Not Found (404) |
| `6` | Conflict (409) |
| `255` | Lỗi không xử lý được (unexpected) |

---

## 6. Output Format Examples

### Success (default)

```json
{
  "data": { "id": "uuid", "name": "Profile A", "status": "inactive" },
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

### Error

```json
{
  "error": "conflict",
  "message": "Profile name 'Profile A' already exists",
  "request_id": "req-abc123",
  "timestamp": "2026-02-18T10:30:00Z"
}
```

### List

```json
{
  "data": {
    "items": [...],
    "total": 42,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 7. Pipeline Integration Examples

### Bash pipeline

```bash
# Tạo profile và lấy ID
PROFILE_ID=$(bm profiles create --name "Bot Profile" --proxy-type socks5 ... --raw | jq -r '.id')

# Launch session và lấy debug port
SESSION=$(bm sessions start --profile $PROFILE_ID --headless --wait-ready --raw)
DEBUG_PORT=$(echo $SESSION | jq -r '.debug_port')

# Chạy script và follow logs
bm jobs run --script my-script --profile $PROFILE_ID --wait --follow

# Cleanup
bm sessions stop $(echo $SESSION | jq -r '.session_id')
```

### PowerShell pipeline

```powershell
$profile = bm profiles create --name "Bot Profile" --raw | ConvertFrom-Json
$session = bm sessions start --profile $profile.id --headless --wait-ready --raw | ConvertFrom-Json
Write-Host "Debug port: $($session.debug_port)"
```

---

## 8. Packaging

### 8.1 Build

```bash
dotnet publish ./src/BrowserManager.Cli \
  -c Release \
  -r win-x64 \
  --self-contained \
  /p:PublishSingleFile=true \
  -o ./dist/cli
```

Output: `bm.exe` (~15MB self-contained).

### 8.2 Distribution

- **Cùng installer**: `bm.exe` được include trong MSI, thêm vào `%ProgramFiles%\BrowserManager\`.
- **PATH**: installer tự động thêm vào PATH.
- **Standalone**: user có thể download `bm.exe` riêng, configure qua `bm config set-url`.

### 8.3 Update

CLI tự check version khi chạy (một lần/ngày):
```
[INFO] New version 1.1.0 available. Run 'bm update' to upgrade.
```

---

## 9. Help system

```bash
bm --help
bm profiles --help
bm profiles create --help
bm jobs run --help
```

Mỗi command có:
- Mô tả ngắn.
- Ví dụ sử dụng.
- Danh sách flags với type, default, description.

---

## 10. Definition of Done (DoD) — EPIC G

- [ ] Tất cả commands trong spec hoạt động đúng.
- [ ] Output JSON hợp lệ cho mọi command.
- [ ] Exit codes chính xác theo bảng trên.
- [ ] `--help` đầy đủ cho mọi command.
- [ ] Integration test: pipeline bash/PS gọi CLI → agent → verify kết quả.
- [ ] `bm.exe` chạy không cần cài đặt thêm gì (self-contained).
- [ ] Config file `%APPDATA%\BrowserManager\config.json` hoạt động đúng.
- [ ] Token không xuất hiện trong `--help` output hoặc logs.

---

*Tài liệu tiếp theo: [06-browser-runtime.md](06-browser-runtime.md)*
