# Data Dictionary — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **SSOT cho**: Tất cả bảng DB và field definitions  
> **Người phê duyệt**: Tech Lead  
> **Database**: SQLite (embedded, file: `browsermanager.db`)

---

## 1. Tổng quan Schema

### 1.1 Danh sách bảng

| Bảng | Mô tả | Migration |
|---|---|---|
| `profiles` | Browser profiles (core entity) | 001 |
| `env_groups` | Profile groups | 006 |
| `env_tags` | Tags (labels) | 006 |
| `profile_tags` | Many-to-many: profile ↔ tag | 006 |
| `proxy_info` | Proxy configurations | 001 |
| `jobs` | Background job queue | 001 |
| `job_logs` | Job execution logs | 001 |
| `audit_logs` | Security audit trail | 003 |
| `settings` | App-level key-value settings | 001 |
| `migrations` | Migration history (DbUp managed) | 001 |

### 1.2 Quan hệ (ERD rút gọn)

```
env_groups (1) ──< (N) profiles
profiles (N) >──< (N) env_tags   [via profile_tags]
proxy_info (1) ──< (N) profiles
profiles (1) ──< (N) jobs
jobs (1) ──< (N) job_logs
profiles (N) ──< (N) audit_logs
```

### 1.3 Quy ước chung

- **ID**: `INTEGER PRIMARY KEY AUTOINCREMENT` — tất cả bảng dùng `id` integer
- **Timestamps**: `created_at` và `updated_at` dạng `TEXT` (ISO 8601: `2026-02-20T10:00:00Z`)
- **Soft delete**: trường `deleted_at TEXT` (NULL = active; non-NULL = deleted)
- **Boolean**: lưu dạng `INTEGER` (0 = false, 1 = true)
- **JSON**: lưu dạng `TEXT` với valid JSON string

---

## 2. Bảng: `profiles`

**Mô tả**: Core entity cho browser profiles. Mỗi row = 1 browser profile độc lập.

### Schema

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `env_id` | TEXT | NOT NULL | — | UNIQUE | Stable public ID (UUID v4), dùng trong API |
| `name` | TEXT | NOT NULL | — | UNIQUE (name) | Tên profile, max 200 ký tự |
| `group_id` | INTEGER | NULL | NULL | FK(env_groups.id) | Group ID; NULL = no group |
| `remark` | TEXT | NULL | NULL | — | Ghi chú tự do, max 500 ký tự |
| `status` | TEXT | NOT NULL | `'stopped'` | INDEX | Trạng thái: `stopped`, `running`, `error` |
| `proxy_id` | INTEGER | NULL | NULL | FK(proxy_info.id) | Proxy; NULL = no proxy |
| `proxy_config` | TEXT | NULL | NULL | — | JSON inline proxy (ưu tiên hơn proxy_id nếu cả hai có) |
| `user_agent` | TEXT | NULL | NULL | — | Custom User-Agent; NULL = browser default |
| `extensions` | TEXT | NOT NULL | `'[]'` | — | JSON array of extension paths |
| `startup_url` | TEXT | NULL | NULL | — | URL mở khi start; NULL = new tab |
| `window_width` | INTEGER | NULL | 1280 | — | Cửa sổ browser width (px) |
| `window_height` | INTEGER | NULL | 800 | — | Cửa sổ browser height (px) |
| `data_dir` | TEXT | NOT NULL | — | UNIQUE | Absolute path tới profile data directory |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp tạo (ISO 8601) |
| `updated_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp cập nhật gần nhất |
| `deleted_at` | TEXT | NULL | NULL | INDEX | NULL = active; non-NULL = soft deleted (in recycle bin) |
| `last_opened_at` | TEXT | NULL | NULL | — | Timestamp mở lần gần nhất |
| `open_count` | INTEGER | NOT NULL | 0 | — | Số lần đã mở |
| `browser_type` | TEXT | NOT NULL | `'chromium'` | INDEX | `chromium`, `firefox`, `webkit` |
| `extra_config` | TEXT | NOT NULL | `'{}'` | — | JSON: cấu hình mở rộng (future fields) |
| `fingerprint_config` | TEXT | NULL | NULL | — | JSON: Fingerprint Engine config (xem `15-fingerprint-engine.md` §3.2). Migration 009. |

### Validation Rules

| Column | Rule |
|---|---|
| `name` | maxLength=200; không được trống; unique per non-deleted profiles |
| `env_id` | format UUID v4; system-generated; readonly sau create |
| `status` | enum: `stopped`, `running`, `error` |
| `browser_type` | enum: `chromium`, `firefox`, `webkit` |
| `window_width` | min=200, max=7680 |
| `window_height` | min=200, max=4320 |
| `data_dir` | absolute path; unique; tạo tự động khi create profile |
| `extensions` | valid JSON array; mỗi item là absolute path |
| `proxy_config` | valid JSON object hoặc NULL; format xem bảng proxy_info |
| `remark` | maxLength=500 |
| `open_count` | min=0; tăng 1 mỗi khi profile được open |

### Computed Fields

| Column | Công thức | Trigger cập nhật |
|---|---|---|
| `open_count` | Increment +1 | Mỗi lần `POST /api/env/start` thành công |
| `last_opened_at` | `datetime('now')` | Mỗi lần `POST /api/env/start` thành công |
| `updated_at` | `datetime('now')` | Mọi UPDATE operation trên row |
| `data_dir` | `{dataRoot}/{env_id}` | Một lần khi INSERT |
| `env_id` | UUID v4 generated | Một lần khi INSERT |

### Indexes

```sql
CREATE UNIQUE INDEX idx_profiles_env_id ON profiles(env_id);
CREATE UNIQUE INDEX idx_profiles_name ON profiles(name) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_profiles_data_dir ON profiles(data_dir);
CREATE INDEX idx_profiles_group_id ON profiles(group_id);
CREATE INDEX idx_profiles_status ON profiles(status);
CREATE INDEX idx_profiles_deleted_at ON profiles(deleted_at);
```

---

## 3. Bảng: `env_groups`

**Mô tả**: Groups để tổ chức profiles.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `group_id` | TEXT | NOT NULL | — | UNIQUE | Public ID (UUID v4) |
| `name` | TEXT | NOT NULL | — | UNIQUE | Tên group, max 100 ký tự |
| `remark` | TEXT | NULL | NULL | — | Ghi chú |
| `sort_order` | INTEGER | NOT NULL | 0 | INDEX | Thứ tự hiển thị |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp tạo |
| `updated_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp cập nhật |

### Validation Rules

| Column | Rule |
|---|---|
| `name` | maxLength=100; không được trống; unique |
| `group_id` | UUID v4; system-generated; readonly |
| `sort_order` | min=0; default=0 |

### Computed Fields

| Column | Công thức | Trigger |
|---|---|---|
| `group_id` | UUID v4 | Khi INSERT |
| `updated_at` | `datetime('now')` | Mọi UPDATE |

### Quan hệ

- `profiles.group_id` → `env_groups.id` (FK, SET NULL on delete)
- Xóa group: profiles trong group có `group_id` set về NULL (không xóa profiles)

---

## 4. Bảng: `env_tags`

**Mô tả**: Tags (labels) để phân loại profiles.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `tag_id` | TEXT | NOT NULL | — | UNIQUE | Public ID (UUID v4) |
| `name` | TEXT | NOT NULL | — | UNIQUE | Tên tag, max 50 ký tự |
| `color` | TEXT | NULL | `'#808080'` | — | Hex color code (#RRGGBB) |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp tạo |
| `updated_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp cập nhật |

### Validation Rules

| Column | Rule |
|---|---|
| `name` | maxLength=50; không được trống; unique |
| `color` | format `#RRGGBB`; default `#808080` |

---

## 5. Bảng: `profile_tags`

**Mô tả**: Junction table cho many-to-many relation giữa profiles và tags.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `profile_id` | INTEGER | NOT NULL | — | FK(profiles.id) | Profile ID |
| `tag_id` | INTEGER | NOT NULL | — | FK(env_tags.id) | Tag ID |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp assign |

**Primary Key**: `(profile_id, tag_id)` composite.

### Cascade Rules

- DELETE profile → DELETE FROM profile_tags WHERE profile_id = ?
- DELETE tag → DELETE FROM profile_tags WHERE tag_id = ?

---

## 6. Bảng: `proxy_info`

**Mô tả**: Reusable proxy configurations.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `proxy_id` | TEXT | NOT NULL | — | UNIQUE | Public ID (UUID v4) |
| `name` | TEXT | NOT NULL | — | INDEX | Tên proxy, max 100 ký tự |
| `proxy_type` | TEXT | NOT NULL | `'http'` | — | `http`, `https`, `socks4`, `socks5` |
| `proxy_host` | TEXT | NOT NULL | — | — | Hostname hoặc IP |
| `proxy_port` | INTEGER | NOT NULL | — | — | Port (1–65535) |
| `proxy_user` | TEXT | NULL | NULL | — | Username (nếu có auth) |
| `proxy_password` | TEXT | NULL | NULL | — | Password (encrypted với DPAPI) |
| `remark` | TEXT | NULL | NULL | — | Ghi chú, max 200 ký tự |
| `last_check_at` | TEXT | NULL | NULL | — | Timestamp kiểm tra kết nối lần gần nhất |
| `last_check_ok` | INTEGER | NULL | NULL | — | 1 = check pass; 0 = check fail; NULL = chưa check |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp tạo |
| `updated_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp cập nhật |

### Validation Rules

| Column | Rule |
|---|---|
| `proxy_type` | enum: `http`, `https`, `socks4`, `socks5` |
| `proxy_host` | max 253 ký tự; valid hostname hoặc IPv4/IPv6 |
| `proxy_port` | min=1, max=65535 |
| `proxy_password` | encrypted at-rest; never logged; never returned in API response |

---

## 7. Bảng: `jobs`

**Mô tả**: Background job queue. Xem chi tiết trong `job-spec.md`.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `job_id` | TEXT | NOT NULL | — | UNIQUE | Public ID (UUID v4) |
| `profile_id` | INTEGER | NULL | NULL | FK(profiles.id) | Profile liên quan (nếu có) |
| `job_type` | TEXT | NOT NULL | — | INDEX | Loại job: `browser_start`, `browser_stop`, `script_run`, `cache_clear`, v.v. |
| `status` | TEXT | NOT NULL | `'queued'` | INDEX | `queued`, `running`, `succeeded`, `failed`, `canceled` |
| `priority` | INTEGER | NOT NULL | 5 | INDEX | 1 (highest) — 10 (lowest) |
| `payload` | TEXT | NOT NULL | `'{}'` | — | JSON: input parameters cho job |
| `result` | TEXT | NULL | NULL | — | JSON: output khi succeeded |
| `error_message` | TEXT | NULL | NULL | — | Error message khi failed |
| `idempotency_key` | TEXT | NULL | NULL | UNIQUE | Client-provided key để tránh duplicate |
| `retry_count` | INTEGER | NOT NULL | 0 | — | Số lần đã retry |
| `max_retries` | INTEGER | NOT NULL | 3 | — | Max retry attempts |
| `timeout_seconds` | INTEGER | NOT NULL | 60 | — | Job timeout (seconds) |
| `scheduled_at` | TEXT | NULL | NULL | INDEX | Thời gian lên lịch chạy (NULL = chạy ngay) |
| `started_at` | TEXT | NULL | NULL | — | Timestamp bắt đầu chạy |
| `finished_at` | TEXT | NULL | NULL | INDEX | Timestamp kết thúc |
| `created_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp tạo |
| `created_by` | TEXT | NULL | NULL | — | Source: `api`, `cli`, `gui`, `scheduler` |

### Computed Fields

| Column | Công thức | Trigger |
|---|---|---|
| `started_at` | `datetime('now')` | Khi status → `running` |
| `finished_at` | `datetime('now')` | Khi status → `succeeded`, `failed`, hoặc `canceled` |
| `retry_count` | +1 | Mỗi lần retry |

---

## 8. Bảng: `job_logs`

**Mô tả**: Log lines từ job execution.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `job_id` | TEXT | NOT NULL | — | FK+INDEX | Job ID |
| `level` | TEXT | NOT NULL | `'info'` | — | `debug`, `info`, `warn`, `error` |
| `message` | TEXT | NOT NULL | — | — | Log message |
| `timestamp` | TEXT | NOT NULL | `datetime('now')` | INDEX | Timestamp log line |

---

## 9. Bảng: `audit_logs`

**Mô tả**: Security audit trail. Không được xóa.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `id` | INTEGER | NOT NULL | AUTOINCREMENT | PK | Primary key |
| `event_type` | TEXT | NOT NULL | — | INDEX | `profile_created`, `profile_deleted`, `token_issued`, `auth_failed`, v.v. |
| `actor` | TEXT | NULL | NULL | — | `api`, `cli`, `gui` |
| `resource_type` | TEXT | NULL | NULL | INDEX | `profile`, `group`, `tag`, `proxy`, `job` |
| `resource_id` | TEXT | NULL | NULL | — | ID của resource bị tác động |
| `details` | TEXT | NOT NULL | `'{}'` | — | JSON: chi tiết event |
| `ip_address` | TEXT | NULL | NULL | — | IP của caller (luôn là 127.0.0.1 với local API) |
| `timestamp` | TEXT | NOT NULL | `datetime('now')` | INDEX | Timestamp event |

### Retention Policy

- Audit logs **không được xóa thủ công**.
- Auto-archive sau 30 ngày vào `audit_logs_archive` table.
- Giữ tối thiểu 90 ngày tổng cộng.

---

## 10. Bảng: `settings`

**Mô tả**: App-level configuration key-value store.

| Column | Type | Nullable | Default | Index | Mô tả |
|---|---|---|---|---|---|
| `key` | TEXT | NOT NULL | — | PK | Setting key (namespaced: `section.key`) |
| `value` | TEXT | NOT NULL | — | — | Setting value (JSON hoặc string) |
| `description` | TEXT | NULL | NULL | — | Mô tả cho setting |
| `updated_at` | TEXT | NOT NULL | `datetime('now')` | — | Timestamp cập nhật |

### Canonical Setting Keys (xem `15-config-keys-reference.md` cho đầy đủ)

| Key | Type | Default | Mô tả |
|---|---|---|---|
| `api.port` | integer | `40000` | Local API port |
| `api.token` | string | auto-generated | Bearer token (encrypted) |
| `api.rate_limit_rps` | integer | `50` | Rate limit requests/second |
| `agent.max_concurrent_jobs` | integer | `20` | Max parallel jobs |
| `agent.max_concurrent_browsers` | integer | `20` | Max parallel browsers |
| `agent.log_retention_days` | integer | `30` | Job log retention |
| `compat.enabled` | boolean | `true` | Enable compat layer |
| `compat.base_path` | string | `"/api"` | Compat API base path |

---

## 11. Soft Delete / Trash Lifecycle

Xem chi tiết trong `profile-lifecycle.md`. Tóm tắt:

| Trạng thái | `deleted_at` | Hành vi |
|---|---|---|
| Active | NULL | Hiển thị trong list; có thể open |
| Soft Deleted (Recycle Bin) | non-NULL | Ẩn khỏi list thường; hiện trong recycle bin |
| Permanently Deleted | row bị xóa | Không còn trong DB; data dir được xóa |

**Retention**: Profile trong recycle bin được tự động permanent delete sau 30 ngày (configurable).

---

## 12. Migration 009 — `fingerprint_config` Column

**File**: `migrations/009_add_fingerprint_config.sql`  
**Mục đích**: Thêm cột `fingerprint_config` vào bảng `profiles` để lưu trữ cấu hình Fingerprint Engine per-profile.

```sql
-- Migration 009: add fingerprint_config to profiles
ALTER TABLE profiles ADD COLUMN fingerprint_config TEXT; -- JSON, nullable
```

### Cột mới: `profiles.fingerprint_config`

| Thuộc tính | Giá trị |
|---|---|
| Bảng | `profiles` |
| Cột | `fingerprint_config` |
| Kiểu | `TEXT` |
| Nullable | Có (NULL = dùng template mặc định `windows_chrome_1080p`) |
| Default | NULL |
| Format | Valid JSON string theo schema trong `15-fingerprint-engine.md` §3.2 |

#### JSON Schema tóm tắt

```json
{
  "user_agent": "string",
  "platform": "string",
  "screen_width": "integer",
  "screen_height": "integer",
  "timezone": "string",
  "language": "string",
  "languages": ["string"],
  "hardware_concurrency": "integer",
  "device_memory": "integer",
  "webgl_vendor": "string",
  "webgl_renderer": "string",
  "canvas_noise_seed": "integer",
  "audio_noise_seed": "integer",
  "webrtc_mode": "disabled|replace|real",
  "font_list_override": ["string"] | null,
  "do_not_track": "boolean",
  "color_depth": "integer",
  "pixel_ratio": "number"
}
```

> Spec đầy đủ: xem [`15-fingerprint-engine.md`](15-fingerprint-engine.md) §3.

---

## 13. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
| 1.1 | 2026-02-20 | Thêm Migration 009 — fingerprint_config column |
