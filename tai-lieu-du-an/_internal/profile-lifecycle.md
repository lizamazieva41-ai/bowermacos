# Profile Lifecycle — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Đặc tả đầy đủ vòng đời của Profile: tạo, chạy, xóa mềm, khôi phục, xóa vĩnh viễn.  
> **SSOT cho**: Profile state machine và lifecycle events.

---

## 1. Trạng thái Profile

### 1.1 State Machine

```
         CREATE
           │
           ▼
      ┌─────────┐
      │  active │◄──────────────────────────┐
      │ stopped │                           │ RESTORE
      └─────────┘                           │
           │                           ┌──────────────┐
           │ START                     │   recycle_bin │
           ▼                           │  (soft deleted)│
      ┌─────────┐   STOP / CLOSE       └──────────────┘
      │  active │──────────────────►        ▲
      │ running │                           │
      └─────────┘                 REMOVE_TO_RECYCLE_BIN
           │                           │
           │ ERROR                     │
           ▼                           │
      ┌─────────┐──────────────────────┘
      │  active │
      │  error  │
      └─────────┘
           │
           │ REMOVE_TO_RECYCLE_BIN
           ▼
      ┌──────────────┐
      │  recycle_bin  │──────────────► PERMANENT_DELETE ──► [row deleted]
      │ (soft deleted)│
      └──────────────┘
```

### 1.2 Bảng trạng thái

| Trạng thái | `status` (DB) | `deleted_at` (DB) | Mô tả |
|---|---|---|---|
| **active/stopped** | `stopped` | NULL | Profile tồn tại, chưa chạy |
| **active/running** | `running` | NULL | Browser đang mở |
| **active/error** | `error` | NULL | Browser lỗi khi launch/chạy |
| **recycle_bin** | `stopped` | non-NULL | Đã xóa mềm; trong recycle bin |
| **permanently deleted** | — | — | Row bị xóa khỏi DB; data dir bị xóa |

---

## 2. Transitions — Chi tiết

### 2.1 CREATE Profile

**Trigger**: `POST /api/env/create/quick` hoặc `POST /api/env/create/advanced`  
**Điều kiện**: name unique (trong non-deleted profiles)  
**Actions**:
1. Generate `env_id` (UUID v4)
2. Tạo `data_dir`: `{dataRoot}/{env_id}/`
3. INSERT row vào `profiles` với `status = 'stopped'`, `deleted_at = NULL`
4. Log audit event: `profile_created`
5. Trả về profile object

**Side effects**:
- Tạo thư mục `data_dir` trên disk
- Tạo default browser profile structure trong `data_dir`

**Error cases**:
- Name trùng → `-1002`
- Disk đầy → `-1704`
- Invalid proxy config → `-1008`

---

### 2.2 START Profile (Open Browser)

**Trigger**: `POST /api/env/start`  
**Điều kiện**: profile tồn tại (`deleted_at IS NULL`); `status != 'running'`  
**Actions**:
1. Enqueue job type `browser_start` với payload `{env_id, ...options}`
2. Job executor: launch Playwright browser với `data_dir` và proxy config
3. Cập nhật `status = 'running'`, `last_opened_at = now()`, `open_count += 1`
4. Lấy debug port từ browser process
5. Trả về `{envId, debugPort, wsEndpoint}`

**Side effects**:
- Tạo browser process (Chromium/Firefox/WebKit)
- Chiếm port debug (ngẫu nhiên 9222+)
- Tăng memory usage

**Error cases**:
- Profile đang running → `-1005` (return current debug port)
- Profile trong recycle bin → `-1004`
- Max concurrent reached (20) → `-1007`
- Browser fail to launch → `-1006`

---

### 2.3 STOP / CLOSE Profile

**Trigger**: `POST /api/env/close` hoặc `POST /api/env/closeAll`  
**Điều kiện**: profile đang `running`  
**Actions**:
1. Enqueue job type `browser_stop`
2. Graceful browser close (Playwright close)
3. Cập nhật `status = 'stopped'`
4. Giải phóng debug port

**Side effects**:
- Kill browser process nếu graceful close timeout (5s)
- Giải phóng RAM

**Error cases**:
- Profile không running → no-op, return success (idempotent)
- Kill failed → `-1006`, agent tries force kill

---

### 2.4 REMOVE TO RECYCLE BIN (Soft Delete)

**Trigger**: `POST /api/env/removeToRecycleBin/batch`  
**Điều kiện**: profile tồn tại; có thể đang running  
**Actions**:
1. Nếu `status = 'running'`: close browser trước (chạy stop flow)
2. Cập nhật `deleted_at = datetime('now')`
3. `status` vẫn giữ là `stopped`
4. Log audit event: `profile_soft_deleted`
5. Profile biến mất khỏi `/api/env/list` và `/api/env/page`
6. Profile xuất hiện trong recycle bin listing

**Side effects**:
- Browser bị close (nếu đang chạy)
- Data dir KHÔNG bị xóa (data still on disk)
- Profile không còn nhận được job mới

**Error cases**:
- Một số IDs không tồn tại: bỏ qua; chỉ xử lý IDs hợp lệ
- Trả về `{succeeded: [...], failed: [...]}`

---

### 2.5 RESTORE (từ Recycle Bin)

**Trigger**: `POST /api/profiles/{id}/restore` (native endpoint)  
**Điều kiện**: `deleted_at IS NOT NULL` (profile trong recycle bin)  
**Actions**:
1. Kiểm tra name unique trong active profiles (nếu trùng: thêm suffix ` (restored)`)
2. Cập nhật `deleted_at = NULL`
3. `status = 'stopped'`
4. Log audit event: `profile_restored`

**Side effects**:
- Profile xuất hiện lại trong list
- Data dir vẫn nguyên vẹn
- Không tạo lại browser profile data

**Error cases**:
- Profile không trong recycle bin → `-1010`

---

### 2.6 PERMANENT DELETE

**Trigger**: `POST /api/profiles/{id}/delete/permanent` (native endpoint); hoặc auto sau retention period  
**Điều kiện**: `deleted_at IS NOT NULL` (phải trong recycle bin trước)  
**Actions**:
1. Xóa row `profile_tags` liên quan
2. Xóa row `profiles`
3. **Xóa `data_dir` trên disk** (recursive delete)
4. Log audit event: `profile_permanent_deleted`
5. Archive jobs liên quan (mark as `archived`)

**⚠️ Cảnh báo**: Không thể undo. Data dir bị xóa vĩnh viễn.

**Side effects**:
- Xóa toàn bộ browser data (cookies, localStorage, downloads, extensions data)
- Giải phóng disk space
- Jobs liên quan bị archive

**Error cases**:
- Profile chưa trong recycle bin → `-1003` (must soft-delete first)
- Disk delete failed → `-1701` (row đã xóa, disk cleanup scheduled for retry)

---

### 2.7 AUTO-EXPIRE Recycle Bin

**Trigger**: Scheduler job (mặc định: chạy mỗi 24 giờ)  
**Điều kiện**: `deleted_at < datetime('now', '-30 days')` (configurable: `settings.recycle_bin_retention_days`)  
**Actions**: Chạy PERMANENT DELETE flow cho tất cả profiles thỏa điều kiện.

---

## 3. Events & Audit Log

Mỗi transition phát ra audit event:

| Event | Khi nào | Fields trong `details` |
|---|---|---|
| `profile_created` | CREATE | `{name, group_id, proxy_id, browser_type}` |
| `profile_updated` | UPDATE | `{changed_fields: [...]}` |
| `profile_opened` | START | `{env_id, debug_port}` |
| `profile_closed` | STOP | `{env_id, duration_seconds}` |
| `profile_soft_deleted` | REMOVE TO RECYCLE BIN | `{env_id, name}` |
| `profile_restored` | RESTORE | `{env_id, name}` |
| `profile_permanent_deleted` | PERMANENT DELETE | `{env_id, name, data_dir_size_bytes}` |

---

## 4. API Endpoints liên quan

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/env/create/quick` | POST | Create profile (quick mode) |
| `/api/env/create/advanced` | POST | Create profile (advanced mode) |
| `/api/env/start` | POST | Open browser |
| `/api/env/close` | POST | Close browser |
| `/api/env/closeAll` | POST | Close all browsers |
| `/api/env/removeToRecycleBin/batch` | POST | Soft delete (batch) |
| `/api/env/list` | POST | List active profiles (excludes deleted) |
| `/api/env/page` | POST | Paginated list of active profiles |
| `/api/env/detail` | POST | Get profile detail |
| `/api/env/update` | POST | Update profile |
| `/api/profiles/{id}/restore` | POST | Restore from recycle bin (native) |
| `/api/profiles/{id}/delete/permanent` | POST | Permanent delete (native) |

---

## 5. Configuration

| Setting | Default | Mô tả |
|---|---|---|
| `recycle_bin_retention_days` | `30` | Ngày trước khi auto-permanent-delete |
| `auto_close_on_soft_delete` | `true` | Tự động close browser khi soft delete |
| `data_root` | `%APPDATA%\BrowserManager\profiles` | Root directory cho profile data dirs |

---

## 6. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
