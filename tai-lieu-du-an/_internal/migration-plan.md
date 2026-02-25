# migration-plan.md — Database Migration Plan

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-18 | **Trạng thái**: Draft  
> **Mục đích**: Kế hoạch chi tiết migration schema DB từ v1.0 → v1.1 → v1.2, kèm rollback procedure và test matrix.

---

## 1. Tổng quan

### 1.1 Nguyên tắc migration

- **Forward-only migrations**: mỗi migration chỉ thêm cột/bảng, không xoá.
- **Idempotent**: có thể chạy lại mà không gây lỗi (`IF NOT EXISTS`).
- **Auto-run on startup**: Agent chạy migration trước khi start API.
- **Transactional**: mỗi migration wrapped trong `BEGIN TRANSACTION / COMMIT`.
- **Versioned**: mỗi migration có số thứ tự và timestamp.

### 1.2 Migration runner

Dùng **DbUp** (hoặc EF Core Migrations):

```csharp
var upgrader = DeployChanges.To
    .SQLiteDatabase(connectionString)
    .WithScriptsEmbeddedInAssembly(Assembly.GetExecutingAssembly())
    .WithTransaction()
    .LogToConsole()
    .Build();

var result = upgrader.PerformUpgrade();
if (!result.Successful)
{
    logger.LogCritical("DB migration failed: {Error}", result.Error);
    Environment.Exit(1);  // Agent không start nếu migration fail
}
```

### 1.3 Migration file naming

```
migrations/
  001_initial_schema.sql           ← v1.0 baseline
  002_add_extensions_column.sql    ← v1.0.1
  003_add_audit_logs.sql           ← v1.0.2
  004_add_recycle_bin.sql          ← v1.0.3
  005_add_webhooks.sql             ← v1.0.4
  006_add_group_tag_entities.sql   ← v1.1.0  ← MỚI
  007_add_profile_e2e_lock.sql     ← v1.1.0  ← MỚI
  008_add_proxy_profile_count.sql  ← v1.1.0  ← MỚI
```

---

## 2. Migration v1.0 → v1.1

### 2.1 Overview of changes

| Change | Bảng | Mô tả |
|---|---|---|
| Tạo mới | `env_groups` | Group entity (thay string `group_name`) |
| Tạo mới | `env_tags` | Tag entity (thay string array `tags`) |
| Tạo mới | `profile_tags` | Junction table n-n profiles ↔ tags |
| Thêm cột | `profiles.group_id` | FK → env_groups.id |
| Thêm cột | `profiles.remark` | Free-text note |
| Thêm cột | `profiles.e2e_encryption_enabled` | Restricted interface field |
| Thêm cột | `profiles.lock_status` | Restricted interface field |
| Thêm cột | `profiles.last_used_at` | Last session start timestamp |
| Thêm cột | `proxies.profile_count` | Computed cache (denormalized) |

### 2.2 Migration 006: `006_add_group_tag_entities.sql`

```sql
-- ============================================================
-- Migration 006: Add env_groups, env_tags, profile_tags
-- Version: 1.1.0
-- Date: 2026-02-18
-- ============================================================

BEGIN TRANSACTION;

-- === Bảng env_groups ===
CREATE TABLE IF NOT EXISTS env_groups (
    id           TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || 
                   lower(hex(randomblob(2))) || '-4' || 
                   substr(lower(hex(randomblob(2))),2) || '-' || 
                   substr('89ab',abs(random()) % 4 + 1, 1) || 
                   substr(lower(hex(randomblob(2))),2) || '-' || 
                   lower(hex(randomblob(6)))),
    name         TEXT NOT NULL UNIQUE,
    sort_order   INTEGER DEFAULT 0,
    color        TEXT,                    -- hex color e.g. "#FF5733"
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_env_groups_name ON env_groups(name);

-- === Bảng env_tags ===
CREATE TABLE IF NOT EXISTS env_tags (
    id           TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || 
                   lower(hex(randomblob(2))) || '-4' || 
                   substr(lower(hex(randomblob(2))),2) || '-' || 
                   substr('89ab',abs(random()) % 4 + 1, 1) || 
                   substr(lower(hex(randomblob(2))),2) || '-' || 
                   lower(hex(randomblob(6)))),
    name         TEXT NOT NULL UNIQUE,
    color        TEXT NOT NULL DEFAULT '#808080',
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_env_tags_name ON env_tags(name);

-- === Bảng profile_tags (n-n junction) ===
CREATE TABLE IF NOT EXISTS profile_tags (
    profile_id   TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    tag_id       TEXT NOT NULL REFERENCES env_tags(id) ON DELETE CASCADE,
    assigned_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (profile_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_profile_tags_profile ON profile_tags(profile_id);
CREATE INDEX IF NOT EXISTS idx_profile_tags_tag     ON profile_tags(tag_id);

-- === Thêm cột group_id vào profiles ===
ALTER TABLE profiles ADD COLUMN group_id TEXT REFERENCES env_groups(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_group_id ON profiles(group_id);

-- === Data migration: chuyển group_name string → entity ===
-- Tạo group entities từ unique group_name values
INSERT OR IGNORE INTO env_groups (name)
SELECT DISTINCT group_name FROM profiles
WHERE group_name IS NOT NULL AND group_name <> '';

-- Set group_id FK từ group_name string
UPDATE profiles
SET group_id = (SELECT id FROM env_groups WHERE env_groups.name = profiles.group_name)
WHERE group_name IS NOT NULL AND group_name <> '';

-- === Data migration: chuyển tags JSON array → env_tags + profile_tags ===
-- NOTE: SQLite JSON functions may not be available in older versions.
-- This migration script uses application-layer migration for tag data.
-- Tags JSON array in profiles.tags sẽ được xử lý bởi migration service khi khởi động.
-- (Xem TagMigrationService.cs)

COMMIT;
```

### 2.3 Migration 007: `007_add_profile_e2e_lock.sql`

```sql
-- ============================================================
-- Migration 007: Add e2e_encryption, lock_status, remark, last_used_at
-- Version: 1.1.0
-- Date: 2026-02-18
-- ============================================================

BEGIN TRANSACTION;

-- Thêm remark (free-text note)
ALTER TABLE profiles ADD COLUMN remark TEXT DEFAULT NULL;

-- E2E Encryption flag [Restricted - interface only]
ALTER TABLE profiles ADD COLUMN e2e_encryption_enabled BOOLEAN NOT NULL DEFAULT 0;

-- Lock Status [Restricted - interface only]
ALTER TABLE profiles ADD COLUMN lock_status TEXT NOT NULL DEFAULT 'unlocked'
    CHECK (lock_status IN ('unlocked', 'locked'));

-- Last used timestamp
ALTER TABLE profiles ADD COLUMN last_used_at DATETIME DEFAULT NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_lock_status ON profiles(lock_status);
CREATE INDEX IF NOT EXISTS idx_profiles_last_used_at ON profiles(last_used_at);

COMMIT;
```

### 2.4 Migration 008: `008_add_proxy_computed_fields.sql`

```sql
-- ============================================================
-- Migration 008: Add denormalized profile_count to proxies
-- Version: 1.1.0
-- Date: 2026-02-18
-- ============================================================

BEGIN TRANSACTION;

-- Note: profile_count là cached value, được cập nhật bởi application layer
-- Không dùng trigger để tránh performance issue
ALTER TABLE proxies ADD COLUMN profile_count INTEGER NOT NULL DEFAULT 0;

-- Initialize from actual data
UPDATE proxies
SET profile_count = (
    SELECT COUNT(*) FROM profiles
    WHERE profiles.proxy_id = proxies.id
      AND profiles.status <> 'deleted'
);

COMMIT;
```

#### Computed Fields — `profileCount`

**Định nghĩa**: `profileCount` là **denormalized cached field** xuất hiện trong 3 entities:

1. **Group entity** (`env_groups`): Số profiles thuộc group đó
2. **Tag entity** (`env_tags`): Số profiles có tag đó
3. **ProxyInfo entity** (`proxies`): Số profiles sử dụng proxy đó

**Cách tính**:

```sql
-- For env_groups
SELECT COUNT(*) FROM profiles 
WHERE group_id = :group_id 
  AND status <> 'deleted'

-- For env_tags (via junction table)
SELECT COUNT(DISTINCT profile_id) FROM profile_tags
WHERE tag_id = :tag_id
  AND profile_id IN (SELECT id FROM profiles WHERE status <> 'deleted')

-- For proxies
SELECT COUNT(*) FROM profiles
WHERE proxy_id = :proxy_id
  AND status <> 'deleted'
```

**Update strategy**:

- **Không dùng DB trigger** (để tránh performance overhead)
- **Application-layer update** khi:
  - Profile được tạo → increment count của group/tags/proxy
  - Profile được xóa (soft delete) → decrement count
  - Profile được restore từ trash → increment count
  - Profile chuyển group → decrement old group, increment new group
  - Profile add/remove tag → update tag count
  - Profile đổi proxy → decrement old proxy, increment new proxy

**Caching strategy**:

- Lưu trong DB column để tránh query phức tạp mỗi lần list
- Refresh toàn bộ cache mỗi 24h (background job) để đảm bảo consistency
- API endpoint `POST /api/admin/recount` để force refresh (dev/debug)

**API response**:

```json
// GET /api/groups
{
  "data": [
    {
      "id": "uuid",
      "name": "Work",
      "profileCount": 15,  // ← computed field
      "color": "#FF5733"
    }
  ]
}
```

---

## 3. Migration v1.1 → v1.2 (Planned)

### 3.1 Overview of planned changes

| Change | Bảng | Mô tả |
|---|---|---|
| Tạo mới | `screen_settings` | Per-profile window position/size preferences |
| Thêm cột | `settings.compatibility_enabled` | Toggle MoreLogin compat mode (canonical key, xem 15-config-keys-reference.md) |
| Thêm cột | `settings.compatibility_port` | Port khi compat mode active (deprecated - dùng Kestrel config thay) |
| Thêm cột | `env_groups.description` | Optional group description |
| Thêm cột | `jobs.priority` | Job priority queue |

**Lưu ý**: `settings.compatibility_*` columns là fallback cho DB-based config. Khuyến nghị dùng `appsettings.json` với keys `compatibility.enabled` (xem [`15-config-keys-reference.md`](15-config-keys-reference.md)).

### 3.2 Migration 009 (Planned): `009_add_screen_settings.sql`

```sql
-- ============================================================
-- Migration 009: Add screen_settings table (PLANNED — v1.2.0)
-- ============================================================

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS screen_settings (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    monitor_idx  INTEGER NOT NULL DEFAULT 0,
    x            INTEGER NOT NULL DEFAULT 0,
    y            INTEGER NOT NULL DEFAULT 0,
    width        INTEGER NOT NULL DEFAULT 1280,
    height       INTEGER NOT NULL DEFAULT 800,
    is_maximized BOOLEAN NOT NULL DEFAULT 0,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, monitor_idx)
);

ALTER TABLE env_groups ADD COLUMN description TEXT DEFAULT NULL;

COMMIT;
```

---

## 4. Rollback Procedure

### 4.1 Rollback strategy

SQLite **không hỗ trợ `DROP COLUMN`** natively (trước SQLite 3.35.0).  
Rollback strategy được thực hiện theo cơ chế **database snapshot**:

```
Trước khi upgrade:
  1. Agent tạo backup: COPY profiles.db → profiles.db.bak.{version}
  2. Chạy migrations
  3. Nếu migration fail → restore từ backup

Rollback thủ công:
  1. Stop agent
  2. Copy profiles.db.bak.{version} → profiles.db
  3. Start agent với version cũ
```

### 4.2 Rollback script

```bash
# Stop agent
sc stop BrowserManagerAgent

# Backup hiện tại
copy "%APPDATA%\BrowserManager\data\profiles.db" ^
     "%APPDATA%\BrowserManager\data\profiles.db.rollback.%date%"

# Restore từ pre-upgrade backup
copy "%APPDATA%\BrowserManager\data\profiles.db.bak.v1.0" ^
     "%APPDATA%\BrowserManager\data\profiles.db"

# Start agent cũ
sc start BrowserManagerAgent
```

### 4.3 Rollback per migration

| Migration | Rollback Action |
|---|---|
| `006_add_group_tag_entities` | Restore từ snapshot; data `group_id`, `group_name` vẫn còn |
| `007_add_profile_e2e_lock` | Restore từ snapshot; cột `e2e_encryption_enabled`, `lock_status` bị bỏ |
| `008_add_proxy_computed_fields` | Restore từ snapshot; `profile_count` computed bị bỏ |

### 4.4 Data preservation guarantees

| Data | Bảo đảm |
|---|---|
| Profile records | ✅ Không xoá trong migration |
| Group names (string) | ✅ Giữ nguyên cột `group_name`; `group_id` là addition |
| Tags (string array) | ✅ Giữ nguyên cột `tags`; `profile_tags` là addition |
| Proxy passwords (encrypted) | ✅ Không thay đổi |
| Session/Job history | ✅ Không liên quan |

---

## 5. Test Matrix — Upgrade Scenarios

### 5.1 Upgrade paths

| From | To | Test Status | Notes |
|---|---|---|---|
| Fresh install | v1.0 | ✅ Required | Migration 001–005 |
| Fresh install | v1.1 | ✅ Required | Migration 001–008 |
| v1.0 | v1.1 | ✅ Required | Migration 006–008 |
| v1.1 | v1.2 | 📋 Planned | Migration 009 |

### 5.2 Test cases per upgrade path

#### TC-MIG-01: Fresh install → v1.1

```
1. Start với database trống
2. Chạy tất cả migrations 001–008
3. Verify tất cả bảng tồn tại
4. Verify FK constraints hoạt động
5. Verify indexes được tạo
6. Create profile → Verify không lỗi
7. Create group → Verify FK hoạt động
8. Assign tag → Verify junction table
Expected: PASS — tất cả operations thành công
```

#### TC-MIG-02: Upgrade v1.0 → v1.1 với dữ liệu cũ

```
1. Tạo database v1.0 với:
   - 10 profiles (có group_name strings, tags JSON arrays)
   - 5 proxies
2. Chạy migrations 006–008
3. Verify tất cả 10 profiles vẫn accessible
4. Verify group_name strings được migrate sang env_groups entities
5. Verify group_id FK được set đúng
6. Verify profile_count trong proxies đúng
7. Verify không có data loss
Expected: PASS — dữ liệu cũ được preserve + migrate
```

#### TC-MIG-03: Rollback v1.1 → v1.0

```
1. Start với database v1.1
2. Stop agent
3. Restore profiles.db.bak.v1.0
4. Start agent v1.0
5. Verify agent starts thành công
6. Verify profiles accessible
Expected: PASS — agent v1.0 hoạt động với DB cũ
```

#### TC-MIG-04: Migration idempotency

```
1. Chạy migration 006 lần 1 → PASS
2. Chạy migration 006 lần 2 (IF NOT EXISTS) → PASS (no error)
Expected: PASS — `IF NOT EXISTS` prevents duplicate errors
```

#### TC-MIG-05: Migration với concurrent access

```
1. Start agent (migration chạy ngầm)
2. Gửi API request ngay khi migration đang chạy
3. Verify API request được queue/reject đúng cách, không crash
Expected: API returns 503 Service Unavailable trong khi migration running
```

#### TC-MIG-06: Corrupt DB recovery

```
1. Tạo corrupt SQLite file
2. Start agent → migration fail
3. Verify agent exit với error code 1
4. Verify backup file được tạo trước khi migration
5. Restore từ backup → agent starts correctly
Expected: PASS — fail-safe behavior, no data corruption
```

### 5.3 Performance test

| Scenario | Data | Target |
|---|---|---|
| Migration 006 với 1000 profiles | 1000 rows | < 5 giây |
| Migration 006 với 10000 profiles | 10000 rows | < 30 giây |
| Fresh install migrations 001–008 | Empty DB | < 2 giây |

---

## 6. Migration Service Architecture

```csharp
public class DatabaseMigrationService
{
    private readonly ILogger<DatabaseMigrationService> _logger;
    private readonly string _connectionString;
    
    public async Task<bool> RunMigrationsAsync()
    {
        // 1. Create backup trước migration
        await CreateBackupAsync();
        
        // 2. Chạy SQL migrations qua DbUp
        var success = RunSqlMigrations();
        
        // 3. Chạy application-layer migrations (tag data)
        if (success)
            await RunTagDataMigrationAsync();
        
        return success;
    }
    
    private async Task RunTagDataMigrationAsync()
    {
        // Chuyển profiles.tags (JSON array strings)
        // sang env_tags + profile_tags (entities)
        var profiles = await GetProfilesWithStringTagsAsync();
        foreach (var profile in profiles)
        {
            var tagNames = ParseTagsJson(profile.Tags);
            foreach (var tagName in tagNames)
            {
                var tag = await GetOrCreateTagAsync(tagName, defaultColor: "#808080");
                await AssignTagToProfileAsync(profile.Id, tag.Id);
            }
        }
    }
    
    private async Task CreateBackupAsync()
    {
        var dbPath = GetDatabasePath();
        var backupPath = dbPath + $".bak.{GetCurrentVersion()}";
        File.Copy(dbPath, backupPath, overwrite: true);
        _logger.LogInformation("Database backup created: {Path}", backupPath);
    }
}
```

---

## 7. Definition of Done — Migration Plan

- [ ] Tất cả migration scripts được code review.
- [ ] TC-MIG-01 đến TC-MIG-06 pass trên CI.
- [ ] Performance test pass (migrations < 5s cho 1000 rows).
- [ ] Rollback procedure được test thực tế.
- [ ] Data preservation guarantee được verify.
- [ ] Migration scripts được include trong installer package.

---

*Tài liệu liên quan: [01-kien-truc-he-thong.md](01-kien-truc-he-thong.md) §4 (Database Schema) | [11-installer-spec.md](11-installer-spec.md)*
