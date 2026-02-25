# 10 — QA Plan & Release Checklist

> **Phiên bản**: 1.2 | **Ngày**: 2026-02-18 | **Trạng thái**: Review  
> **EPIC tương ứng**: I (Installer & Update) + J (QA, Security, Release)

---

## 1. Mục tiêu tài liệu

Định nghĩa đầy đủ:
- Test plan (unit / integration / e2e).
- Performance test targets.
- Security test checklist.
- Installer spec.
- Release checklist.
- Tài liệu bàn giao.

---

## 2. Test Strategy

```
Unit Tests      ← Test từng class/method riêng lẻ (mock dependencies)
Integration     ← Test tương tác giữa các module (DB, API, Agent)
E2E Tests       ← Test luồng đầy đủ từ CLI/API → Agent → Browser
Performance     ← Stress test, concurrency test
Security Tests  ← Auth, masking, DPAPI, rate limit
```

---

## 3. Unit Tests

### 3.1 Coverage target: ≥ 80% cho Core + Agent

#### ProfileService tests

```
✅ CreateProfile_WithValidData_ReturnsProfile
✅ CreateProfile_WithDuplicateName_Throws409
✅ CreateProfile_CreatesDataDirectory
✅ DeleteProfile_WithActiveSession_Throws409
✅ DeleteProfile_RemovesDataDirectory
✅ CloneProfile_MetadataOnly_CreatesNewDir
✅ CloneProfile_FullCopy_CopiesDataDir
✅ ExportProfile_ExcludeSecrets_NoPasswordInZip
✅ ImportProfile_ValidZip_CreatesProfile
✅ ImportProfile_CorruptedZip_Returns400
```

#### ProxyManager tests

```
✅ EncryptPassword_RoundTrip_MatchesOriginal
✅ DecryptPassword_WrongEntropy_ThrowsException
✅ TestConnectivity_ValidProxy_ReturnsOk
✅ TestConnectivity_InvalidProxy_ReturnsError
✅ TestConnectivity_Timeout_ReturnsTimeout
```

#### TokenService tests

```
✅ GenerateToken_Length48_Chars
✅ HashToken_DeterministicForSameInput
✅ VerifyToken_CorrectToken_ReturnsTrue
✅ VerifyToken_WrongToken_ReturnsFalse
✅ VerifyToken_ConstantTime_NoTimingLeak
```

#### JobQueue tests

```
✅ EnqueueJob_AddsToQueue
✅ Worker_DequeuesAndExecutes
✅ Worker_MaxConcurrency_Enforced
✅ Job_Timeout_MarksAsFailed
✅ Job_Retry_RequeuesOnFailure
✅ Job_MaxRetries_StopsAfterLimit
```

#### LogMasking tests

```
✅ MaskJson_Password_Masked
✅ MaskJson_Token_Masked
✅ MaskJson_NormalField_NotMasked
✅ MaskAuthHeader_Bearer_Masked
```

#### CacheManager tests (mới — v1.1)

```
✅ ClearCache_Cookies_DeletesCookieFile
✅ ClearCache_LocalStorage_DeletesLevelDB
✅ ClearCache_IndexedDB_DeletesIndexedDBDir
✅ ClearCache_All_DeletesAllCacheTypes
✅ ClearCache_RunningProfile_Throws409
✅ ClearCache_RecordsHistoryInDB
✅ ClearCache_AuditsAction
```

#### TrashService tests (mới — v1.1)

```
✅ SoftDelete_SetsStatusDeleted
✅ SoftDelete_CreatesProfileTrashRecord
✅ SoftDelete_DataDirPreserved
✅ Restore_WithinDeadline_SetsStatusInactive
✅ Restore_AfterDeadline_Returns404
✅ PermanentDelete_RemovesDataDir
✅ PermanentDelete_RemovesDBRecord
✅ CleanupJob_DeletesExpiredTrashAfter7Days
```

#### WebhookDispatcher tests (mới — v1.1)

```
✅ Dispatch_ValidEvent_SendsHTTPPost
✅ Dispatch_SignsPayloadWithSecret
✅ Dispatch_Failure_IncrementsFailureCount
✅ Dispatch_MaxFailures_DeactivatesWebhook
✅ Dispatch_LocalhostURL_Rejected (SSRF protection)
✅ Register_DuplicateURL_Returns409
```

#### BatchOperations tests (mới — v1.1)

```
✅ Batch_SetGroup_UpdatesAllProfiles
✅ Batch_SetProxy_UpdatesAllProfiles
✅ Batch_AddTag_AppendsToExistingTags
✅ Batch_RemoveTag_RemovesFromExistingTags
✅ Batch_PartialFailure_ReturnsErrorsPerProfile
✅ Batch_EmptyProfileIds_Returns400
```

#### ExtensionRegistry tests (mới — v1.1)

```
✅ Register_ValidStoreURL_ExtractsExtensionId
✅ Register_DuplicateExtension_Returns409
✅ Assign_AddAction_CreatesProfileExtensionRecord
✅ Assign_RemoveAction_DeletesProfileExtensionRecord
✅ Assign_ToRunningProfile_SucceedsButNeedsRelaunch
✅ Delete_FromRegistry_PreservesAssignedProfiles
```

#### CompatibilityLayer tests (mới — v1.1)

```
✅ Compat_CreateQuick_MapsToCreateProfile
✅ Compat_Start_ReturnsCDPInMoreLoginFormat
✅ Compat_Close_StopsSession
✅ Compat_GetAllDebugInfo_ReturnsMappedFormat
✅ Compat_CloseAll_StopsAllSessions
✅ Compat_DisabledByDefault_Returns404
✅ Compat_EnabledViaConfig_ActivatesRoutes
```

---

## 4. Integration Tests

### 4.1 Scope

Test với real SQLite DB (in-memory), mock Playwright.

#### API Integration Tests

```
✅ POST /api/profiles → 201 + profile in DB
✅ GET /api/profiles → list with pagination
✅ PATCH /api/profiles/{id} → updated in DB
✅ DELETE /api/profiles/{id} → removed from DB + dir deleted
✅ POST /api/proxies/{id}/test → calls connectivity check
✅ POST /api/sessions/start → job created + session in DB
✅ POST /api/sessions/{id}/stop → session status updated
✅ GET /api/jobs/{id} → job with logs
✅ POST /api/scripts/run → job queued + result after await
✅ GET /health → 200 without auth
✅ Request without token → 401
✅ Request with wrong token → 401
✅ Rate limit exceeded → 429
```

#### API Integration Tests — Tính năng mới (v1.1)

```
✅ POST /api/profiles/{id}/clear-cache → cache cleared, history recorded
✅ POST /api/profiles/{id}/clear-cache (running session) → 409
✅ DELETE /api/profiles/{id} → soft delete, profile in trash
✅ GET /api/profiles/trash → list trashed profiles with deadlines
✅ POST /api/profiles/{id}/restore → profile active again, removed from trash
✅ DELETE /api/profiles/{id}/permanent → data_dir deleted immediately
✅ POST /api/profiles/batch → all profiles updated in single call
✅ GET /api/extensions → list central registry
✅ POST /api/extensions → extension registered
✅ POST /api/extensions/{id}/assign (add) → profile_extensions records created
✅ POST /api/extensions/{id}/assign (remove) → profile_extensions records removed
✅ POST /api/sessions/close-all → all running sessions stopped
✅ GET /api/sessions/debug-info → CDP ports for all running sessions
✅ POST /api/webhooks → webhook registered
✅ Webhook fires on job.completed → HTTP POST to registered URL
✅ GET /api/scripts → list scripts from registry
✅ POST /api/scripts → script registered
✅ DELETE /api/scripts/{id} → script removed
✅ GET /api/jobs/{id}/artifacts → list screenshots/logs
✅ POST /api/env/create/quick (compat mode on) → profile created via compat layer
✅ POST /api/env/start (compat mode on) → session started, MoreLogin format response
✅ POST /api/env/getAllDebugInfo (compat mode on) → mapped response
```

#### CLI Integration Tests

```
✅ bm health → JSON output, exit 0
✅ bm profiles create ... → profile created, exit 0
✅ bm profiles list → JSON array
✅ bm sessions start --profile ... → session JSON
✅ bm sessions stop {id} → exit 0
✅ bm jobs run --wait → waits for completion, exit 0
✅ bm jobs run --follow → streams logs to stdout
✅ bm invalid-command → exit 1, error in JSON
✅ bm profiles create (agent offline) → exit 3
```

---

## 5. End-to-End Tests

### 5.1 E2E Test Scenarios

#### E2E-01: Full Profile Lifecycle

```
1. Tạo profile mới qua API
2. Verify thư mục data_dir tồn tại
3. Launch session (headless)
4. Verify debug_port respond
5. Attach Playwright qua CDP
6. Navigate to https://example.com
7. Assert page title = "Example Domain"
8. Stop session
9. Verify session status = "stopped"
10. Delete profile
11. Verify thư mục data_dir đã xoá
```

#### E2E-02: Script Execution

```
1. Tạo profile
2. Add script "health-check" vào registry
3. Launch session
4. Run script via API {url: "https://example.com", expected_title: "Example"}
5. Wait for job completion
6. Verify job status = "completed"
7. Verify result.status = "ok"
8. Verify result.data.status_code = 200
```

#### E2E-03: CLI Pipeline

```bash
PROFILE_ID=$(bm profiles create --name "E2E Test" --raw | jq -r '.id')
SESSION=$(bm sessions start --profile $PROFILE_ID --headless --wait-ready --raw)
DEBUG_PORT=$(echo $SESSION | jq -r '.debug_port')
JOB=$(bm jobs run --script health-check --profile E2E Test --param url=https://example.com --wait --raw)
# Assert: JOB.status == "completed"
bm sessions stop $(echo $SESSION | jq -r '.session_id')
bm profiles delete $PROFILE_ID --yes
```

#### E2E-04: Proxy Test (mock proxy)

```
1. Start mock SOCKS5 proxy server (test fixture)
2. Tạo profile với proxy config trỏ đến mock proxy
3. Test proxy connectivity → verify status "ok"
4. Launch session với proxy
5. Navigate → verify traffic đi qua mock proxy
6. Stop session
```

#### E2E-05: Crash Recovery

```
1. Launch session
2. Force kill browser process (PID) từ outside
3. Wait 10 giây
4. Verify session status = "crashed"
5. Verify job status = "failed" (nếu có job đang chạy)
6. Verify semaphore slot released
7. Verify agent vẫn healthy (GET /health = 200)
```

#### E2E-06: Import / Export Round-trip

```
1. Tạo profile "Original"
2. Cấu hình proxy
3. Export → file .bm-profile.zip (exclude_secrets=true)
4. Xoá profile "Original"
5. Import từ ZIP
6. Verify profile "Original" được tái tạo
7. Verify proxy config đúng (không có password)
8. Verify data_dir mới được tạo
```

#### E2E-07: Recycle Bin Lifecycle (mới — v1.1)

```
1. Tạo profile "TrashTest"
2. DELETE /api/profiles/{id} → soft delete
3. Verify profile vẫn còn trong list trash (GET /api/profiles/trash)
4. Verify data_dir còn tồn tại trên disk
5. POST /api/profiles/{id}/restore → restore
6. Verify profile xuất hiện lại trong GET /api/profiles
7. DELETE /api/profiles/{id} lần 2
8. DELETE /api/profiles/{id}/permanent → permanent delete
9. Verify data_dir đã bị xoá khỏi disk
10. Verify profile không có trong trash list
```

#### E2E-08: Cache Clear Flow (mới — v1.1)

```
1. Tạo profile và launch session (headless)
2. Navigate to a site (tạo cookies)
3. Stop session
4. POST /api/profiles/{id}/clear-cache {types: ["cookies"]}
5. Verify response: bytes_freed > 0
6. Verify GET /api/profiles/{id}/cache-history có entry mới
7. Launch session lại → verify cookies bị xoá (no prior session cookies)
```

#### E2E-09: Batch Operations (mới — v1.1)

```
1. Tạo 5 profiles với group khác nhau
2. POST /api/profiles/batch {profile_ids: [all 5], operations: [{op: "set_group", value: "BatchGroup"}]}
3. Verify tất cả 5 profiles có group_name = "BatchGroup"
4. POST /api/profiles/batch với {op: "add_tag", value: "bulk-test"}
5. Verify tất cả 5 profiles có tag "bulk-test"
6. Cleanup: xoá 5 profiles
```

#### E2E-10: Extension Assign Flow (mới — v1.1)

```
1. POST /api/extensions {source: "chrome.google.com/...", name: "Test Ext"}
2. Tạo 3 profiles
3. POST /api/extensions/{ext_id}/assign {profile_ids: [3 ids], action: "add"}
4. Verify GET /api/profiles/{id} có extension trong list (cho tất cả 3 profiles)
5. Launch 1 profile → verify extension loaded qua Playwright page.evaluate
6. POST /api/extensions/{ext_id}/assign {profile_ids: [1 id], action: "remove"}
7. Verify extension không còn trong profile_extensions cho profile đó
```

#### E2E-11: Webhook Notification (mới — v1.1)

```
1. Khởi động mock webhook receiver (localhost test server)
2. POST /api/webhooks {url: "http://127.0.0.1:{mock_port}/cb", events: ["job.completed"]}
3. Tạo profile + run script
4. Wait for job completion
5. Verify mock receiver đã nhận POST với payload {event: "job.completed", data: {...}}
6. Verify HMAC signature (nếu secret được cấu hình)
```

#### E2E-12: API Compatibility Layer (mới — v1.1)

```
1. Bật compat mode: bm config set compatibility.enabled true
2. POST /api/env/create/quick {name: "CompatTest", proxyType: null}
3. Verify response: {code: 0, msg: "success", data: {id: "...", name: "CompatTest"}}
4. POST /api/env/start {envId: "{id từ step 2}"}
5. Verify response: {code: 0, data: {id, http: "127.0.0.1:{port}", ws: "ws://..."}}
6. POST /api/env/getAllDebugInfo
7. Verify response: {code: 0, data: [{id, http, ws}]}
8. POST /api/env/close {id: "{session_id}"}
9. Verify session stopped
10. POST /api/env/removeToRecycleBin/batch {envIds: ["{profile_id}"]}
11. Verify profile in trash
```

---

## 6. Performance Tests

### 6.1 Targets

| Metric | Target | Test scenario |
|---|---|---|
| Agent startup time | < 3 giây | Đo từ process start → `GET /health = 200` |
| Profile create (100 profiles) | < 1s mỗi profile | 100 sequential POST /profiles |
| Session launch (headless) | < 8 giây | Launch với proxy, headless |
| Session stop | < 5 giây | Graceful stop |
| Crash detection | < 10 giây | Kill process → detect crashed |
| Concurrent sessions (10) | Tất cả launch trong < 30s | 10 concurrent launch |
| Log streaming latency | < 1 giây | Script log line → GUI nhận |
| API throughput | ≥ 100 req/s | Locust load test cho GET endpoints |

### 6.2 Stress Test: 100 sessions

```bash
# Script: start 100 headless sessions liên tiếp (1 tại 1 thời điểm)
for i in $(seq 1 100); do
    PROFILE_ID=$(bm profiles create --name "Stress-$i" --raw | jq -r '.id')
    SESSION=$(bm sessions start --profile $PROFILE_ID --headless --wait-ready --raw)
    SESSION_ID=$(echo $SESSION | jq -r '.session_id')
    bm sessions stop $SESSION_ID
    bm profiles delete $PROFILE_ID --yes
done

# Pass criteria:
# - 0 orphaned processes sau khi kết thúc
# - 0 leaked semaphore slots
# - Memory không tăng liên tục (no leak)
```

### 6.3 Concurrency Test: max_concurrent enforcement

```
1. Set max_concurrent_sessions = 3
2. Gửi 5 concurrent launch requests
3. Verify: chỉ 3 launch; 2 còn lại queued (hoặc 409)
4. Stop 1 → slot released → queued job chạy
```

---

## 7. Security Tests

### 7.1 Authentication

```
✅ POST /api/profiles (no token) → 401
✅ POST /api/profiles (wrong token) → 401
✅ POST /api/profiles (valid token) → 201
✅ GET /health (no token) → 200 (public)
✅ 200 rapid requests với wrong token → không leak timing info
```

### 7.2 Rate Limiting

```
✅ Send 200 req/s → requests 101-200 receive 429
✅ After 1 second cooldown → requests accepted again
```

### 7.3 Data Masking

```
✅ Create profile with proxy password → check log file: no password
✅ Export profile → check ZIP manifest: no password (exclude_secrets=true)
✅ GET /api/profiles/{id} → response: no password_enc field
✅ Run script with sensitive param → check job_logs: param masked
```

### 7.4 Bind Address

```
✅ netstat -a | findstr 40000 → chỉ kết quả "127.0.0.1:40000"
✅ Try connect từ external IP → connection refused
✅ Try connect từ local IP (non-loopback) → connection refused
```

### 7.5 DPAPI

```
✅ Encrypt proxy password → lưu DB → đọc DB → decrypt → match original
✅ Copy DB sang máy khác → decrypt fails (DPAPI machine-bound)
```

### 7.6 Group & Tag Tests (mới — v1.2)

```
✅ TC-GROUP-CRUD: POST /api/envgroup/create → 201, group trong DB
✅ TC-GROUP-LIST: POST /api/envgroup/page → list có phân trang
✅ TC-GROUP-EDIT: POST /api/envgroup/edit → tên đổi trong DB
✅ TC-GROUP-DEL: POST /api/envgroup/delete → group xóa, profiles → Ungrouped
✅ TC-TAG-CRUD: POST /api/envtag/create → 201, tag có color
✅ TC-TAG-ALL: GET /api/envtag/all → danh sách tags với envCount
✅ TC-TAG-DEL: POST /api/envtag/delete → tag xóa, profile_tags CASCADE
✅ TC-BATCH-GROUP: batch set_group (UUID) → profiles cập nhật group_id
✅ TC-BATCH-TAG: batch add_tag (tag UUID) → profile_tags records created
```

### 7.7 API Parity Tests (mới — v1.2)

```
✅ TC-API-ENV-PAGE: POST /api/env/page {page:1, pageSize:5} → list có pagination
✅ TC-API-ENV-PAGE-FILTER: POST /api/env/page {groupId, tagId, envName} → filter đúng
✅ TC-API-ENV-START: POST /api/env/start {envId} → response có debugPort, webdriver, browserVersion
✅ TC-API-ENV-SCREEN: POST /api/env/getAllScreen → list màn hình với width/height
✅ TC-API-ENV-ARRANGE: POST /api/env/arrangeWindows {envIds, cols, screenId} → 200
✅ TC-API-ENV-PIDS: POST /api/env/getAllProcessIds → list pids cho sessions đang chạy
✅ TC-CACHE-LOCAL: POST /api/env/removeLocalCache {envId} → alias đến clear-cache
✅ TC-CACHE-CLOUD: POST /api/env/cache/cleanCloud → 501 Not Implemented
✅ TC-PROXY-PAGE: POST /api/proxyInfo/page {page:1} → danh sách proxy có profileCount
✅ TC-ENV-LIST: POST /api/env/list → 200, compat alias rước
✅ TC-ENV-DETAIL: POST /api/env/detail {"envId":"uuid"} → profile object đúng format
```

### 7.8 E2E Encryption Tests (mới — v1.2) [Restricted]

```
✅ TC-E2E-ENABLED: Profile có e2e_encryption_enabled=true, start không có key → 400
✅ TC-E2E-WITH-KEY: Start với encryptKey hợp lệ → 200, session started
✅ TC-E2E-SHORT-KEY: encryptKey < 32 chars → 400
✅ TC-E2E-NOT-STORED: encryptKey không xuất hiện trong DB, logs, response
✅ TC-E2E-MASK: encryptKey trong job_logs → hiển thị "***"
```

### 7.9 Lock Status Tests (mới — v1.2) [Restricted]

```
✅ TC-LOCK-START: Profile có lock_status="locked", start session → 403
✅ TC-LOCK-UNLOCK: PATCH profile lock_status="unlocked", start session → 200
✅ TC-LOCK-GUI: Profile locked → GUI hiển thị 🔒, disable Launch nút
✅ TC-LOCK-MSG: 403 response có message rõ ràng về locked status
```

---

## 7A. Gate Verification Checklist (G0–G6)

> Checklist này dùng để xác nhận Gate status trước khi release. Tham chiếu chi tiết: [`14-parity-matrix.md`](14-parity-matrix.md).

### G0 — Artefacts Complete

- [ ] `13-baseline-morelogin-public.md` tồn tại và có đủ 30 endpoints
- [ ] `14-parity-matrix.md` tồn tại và có Gate score cho G2–G6
- [ ] `openapi.yaml` tồn tại và pass `npx @redocly/cli lint openapi.yaml`
- [ ] `migration-plan.md` tồn tại với Migration 006, 007, 008
- [ ] Tất cả file tài liệu `00-14` tồn tại trong `tai-lieu-du-an/`

**Vờợt G0**: Tất cả checkboxes trên = PASS.

### G1 — Internal Consistency

- [ ] Default port phải là `40000` nhất quán trong tất cả files (lệnh: `grep -r "agent_url.*40000" tai-lieu-du-an/` — phải có kết quả; `grep -rE "default.*19000|19000.*default" tai-lieu-du-an/` — không có kết quả)
  - `19000` chỉ được phép xuất hiện trong ngữ cảnh "alt-port khi conflict" hoặc "workaround" (ví dụ trong `openapi.yaml` servers list và ADR-007)
  - Ví dụ lệnh QA: `grep -r "19000" tai-lieu-du-an/ | grep -v "alt-port\|conflict\|workaround"` — phải rỗng (không có nơi nào mô tả 19000 là default)
- [ ] Version trong tất cả files được số đúng (1.2 cho các file đã cập nhật)
- [ ] ADR-007 trong `01-kien-truc-he-thong.md` có quyết định về port + compat
- [ ] `group_id` (UUID FK) nhất quán, `group_name` string được deprecate
- [ ] Compat endpoints trong `04-local-api.md` trại với MoreLogin baseline

**Vờợt G1**: 4/5 checkboxes = PASS.

### G2 — API Parity ≥90%

Kiểm tra bằng cách gọi từng endpoint trong `13-baseline-morelogin-public.md`:

- [ ] `POST /api/env/create` → 200/201
- [ ] `POST /api/env/update` → 200
- [ ] `POST /api/env/detail` → 200
- [ ] `POST /api/env/removeToRecycleBin/batch` → 200
- [ ] `POST /api/env/list` → 200 có danh sách
- [ ] `POST /api/env/page` → 200 có `list` + `total` + pagination
- [ ] `POST /api/env/start` → 200 có `debugPort` + `webdriver` + `browserVersion`
- [ ] `POST /api/env/close` → 200
- [ ] `POST /api/env/closeAll` → 200
- [ ] `POST /api/env/active` → 200 có danh sách
- [ ] `POST /api/env/removeLocalCache` → 200
- [ ] `POST /api/env/cache/cleanCloud` → **501** với message hướng dẫn
- [ ] `POST /api/env/getAllScreen` → 200 có list màn hình
- [ ] `POST /api/env/arrangeWindows` → 200
- [ ] `POST /api/env/getAllProcessIds` → 200 có list pids
- [ ] `POST /api/envgroup/page` → 200 có groups
- [ ] `POST /api/envgroup/create` → 201
- [ ] `POST /api/envgroup/edit` → 200
- [ ] `POST /api/envgroup/delete` → 200
- [ ] `GET /api/envtag/all` → 200 có tags + `envCount`
- [ ] `POST /api/envtag/create` → 201
- [ ] `POST /api/envtag/edit` → 200
- [ ] `POST /api/envtag/delete` → 200
- [ ] `POST /api/proxyInfo/page` → 200 có `profileCount`
- [ ] `POST /api/proxyInfo/update` → 200

**Vượt G2**: ≥23/25 = PASS (≥90%).

### G3 — UX Parity

- [ ] "Copy Profile ID" trong menu Actions (⋮) có chức năng
- [ ] Filter bar có `[Group ▼] [Tag ▼] [Status ▼] [Proxy Type ▼] [Date ▼] [⚙ Columns ▼]`
- [ ] Column Settings dropdown hoạt động (hiển/ẩn cột)
- [ ] Group Management screen có CRUD
- [ ] Tag Management screen có CRUD + color picker
- [ ] Profile List hiển thị tag dưới dạng badge màu
- [ ] Profile List hiển thị 🔒 cho locked profiles
- [ ] Create Profile Wizard có trường Group (dropdown, không phải text)

**Vượt G3**: ≥6/8 = PASS.

### G4 — Data Model Parity

- [ ] Bảng `env_groups` tồn tại trong DB (Migration 006)
- [ ] Bảng `env_tags` tồn tại trong DB (Migration 006)
- [ ] Bảng `profile_tags` tồn tại trong DB (Migration 006)
- [ ] `profiles.group_id` là UUID FK vào `env_groups.id` (Migration 006)
- [ ] `profiles.remark` tồn tại (Migration 007)
- [ ] `profiles.last_used_at` tồn tại và được cập nhật khi session start (Migration 007)
- [ ] `proxies.profile_count` là computed/denorm (Migration 008)

**Vượt G4**: 7/7 = PASS.

### G5 — Security Parity

- [ ] `e2e_encryption_enabled` field có trong DB schema
- [ ] `lock_status` field có trong DB schema
- [ ] Start session với locked profile → 403
- [ ] Start session với e2e enabled, không có key → 400
- [ ] `encryptKey` không xuất hiện trong logs

**Vượt G5**: 5/5 = PASS.

### G6 — Restricted Governance

- [ ] `e2e_encryption_enabled` và `lock_status` có nhãn `[Restricted]` trong tài liệu
- [ ] `Refresh Fingerprint` có nhãn `[Restricted — v1.3+]` trong tài liệu
- [ ] `openapi.yaml` có `x-min-agent-version` trên tất cả endpoints
- [ ] Restricted features có version check + 501 response nếu agent version thấp hơn

**Vượt G6**: 4/4 = PASS.

---

## 8. Installer Specification

### 8.1 Components

```
BrowserManagerSetup.exe (NSIS / WiX)
  ├── BrowserManager.exe          ← GUI app
  ├── agent.exe                   ← Windows Service / background agent
  ├── bm.exe                      ← CLI tool
  ├── Playwright/
  │   └── chromium/               ← Bundled Chromium
  ├── runtimes/
  │   └── dotnet-runtime/         ← .NET 8 runtime (self-contained option)
  └── vcredist/                   ← Visual C++ redistributable nếu cần
```

### 8.2 Install steps

```
1. Kiểm tra Windows version (10 x64 minimum)
2. Kiểm tra .NET 8 runtime (hoặc bundle)
3. Copy files vào %ProgramFiles%\BrowserManager\
4. Tạo %APPDATA%\BrowserManager\ structure
5. Install Windows Service: BrowserManagerAgent
6. Thêm bm.exe vào PATH
7. Tạo Desktop shortcut
8. Tạo Start Menu shortcut
9. Register uninstaller
10. Start agent service (nếu option checked)
11. Launch GUI (nếu option checked)
```

### 8.3 Uninstall steps

```
1. Stop agent service
2. Prompt: "Keep user data (profiles, jobs)? [Yes/No]"
3. Nếu No: xoá %APPDATA%\BrowserManager\
4. Remove Windows Service
5. Remove bm.exe từ PATH
6. Remove Program Files\BrowserManager\
7. Remove shortcuts
8. Remove registry entries
```

### 8.4 Upgrade steps

```
1. Stop agent service
2. Backup DB (copy profiles.db → profiles.db.backup)
3. Overwrite binaries
4. Chạy DB migrations (schema upgrade)
5. Restart agent service
6. Verify: GET /health = 200
7. Nếu fail: rollback binaries, restore backup DB
```

---

## 9. Release Checklist

### Pre-release

- [ ] Tất cả unit tests pass (≥ 80% coverage).
- [ ] Tất cả integration tests pass.
- [ ] Tất cả E2E tests pass (môi trường clean Windows 10/11 x64).
- [ ] Performance tests đạt targets trong mục 6.1.
- [ ] Security tests pass (mục 7 toàn bộ).
- [ ] Log review: không có secret nào trong logs từ test run.
- [ ] Audit log: mọi action E2E đều có bản ghi audit.
- [ ] Memory leak test: 100 sessions start/stop không leak.

### Build & Package

- [ ] Version bump (semantic versioning: `MAJOR.MINOR.PATCH`).
- [ ] Changelog được viết (`CHANGELOG.md`).
- [ ] Build pipeline chạy clean (CI).
- [ ] Installer build thành công.
- [ ] Installer test: clean install trên Windows 10.
- [ ] Installer test: upgrade từ phiên bản trước → không mất profile data.
- [ ] Installer test: uninstall sạch.
- [ ] Virus scan trên installer binary.

### Documentation

- [ ] OpenAPI YAML cập nhật và match implementation.
- [ ] CLI `--help` đầy đủ và đúng.
- [ ] Readme / Getting Started guide.
- [ ] Troubleshooting guide.
- [ ] Changelog đầy đủ.

### Final sign-off

- [ ] Product review: các tính năng cốt lõi demo pass.
- [ ] Security review: checklist `09-bao-mat-va-luu-tru.md` pass.
- [ ] QA sign-off.
- [ ] Release tag trên git: `v1.0.0`.

---

## 10. Tài Liệu Bàn Giao Bắt Buộc

| # | Tài liệu | File |
|---|---|---|
| 1 | PRD + Tổng quan dự án | `00-tong-quan-du-an.md` |
| 2 | Kiến trúc hệ thống + ADR + DB Schema | `01-kien-truc-he-thong.md` |
| 3 | Profile System spec | `02-he-thong-profile.md` |
| 4 | Background Agent spec | `03-background-agent.md` |
| 5 | OpenAPI YAML (Local API) | `04-local-api.md` |
| 6 | CLI command reference | `05-cli-spec.md` |
| 7 | Browser Runtime spec | `06-browser-runtime.md` |
| 8 | Automation Framework + 3 sample scripts | `07-automation-framework.md` |
| 9 | GUI spec + wireframes | `08-desktop-gui.md` |
| 10 | Bảo mật + Threat model | `09-bao-mat-va-luu-tru.md` |
| 11 | QA plan + Release checklist (tài liệu này) | `10-qa-release-checklist.md` |
| 12 | Test report (điền khi release) | `test-report-v{version}.md` |
| 13 | Hướng dẫn cài đặt & vận hành | `docs/install-guide.md` |
| 14 | Troubleshooting guide | `docs/troubleshooting.md` |
| 15 | Changelog | `CHANGELOG.md` |

---

## 11. Môi Trường Test

### 11.1 Minimum test environment

- Windows 10 x64 (build 19044+)
- 8 GB RAM
- 20 GB disk free
- Không cài Chrome/Chromium ngoài (test bundled Playwright)
- Fresh user account (không có prior BrowserManager install)

### 11.2 Recommended test matrix

| OS | Kết quả cần |
|---|---|
| Windows 10 21H2 x64 | Pass |
| Windows 11 23H2 x64 | Pass |
| Windows Server 2022 | Pass (headless only) |

### 11.3 CI/CD Pipeline

```yaml
# GitHub Actions / Azure DevOps

on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - checkout
      - setup-dotnet: 8.x
      - run: dotnet test --configuration Release --filter "Category=Unit"
      - run: dotnet test --configuration Release --filter "Category=Integration"
      - run: dotnet test --configuration Release --filter "Category=E2E"
      - upload-artifact: test-results/
  
  build:
    needs: test
    runs-on: windows-latest
    steps:
      - build-agent
      - build-gui
      - build-cli
      - build-installer
      - upload-artifact: dist/BrowserManagerSetup.exe
```

---

## 12. Definition of Done (DoD) — EPIC I + J

- [ ] Tất cả test categories pass.
- [ ] Installer: install/upgrade/uninstall đều pass.
- [ ] Release checklist hoàn thành 100%.
- [ ] Tài liệu bàn giao đầy đủ (mục 10).
- [ ] Build phát hành signed (optional: code signing certificate).
- [ ] Version tagging trên source control.

---

## 13. Known Limitations (Phase 1)

| # | Limitation | Workaround | Phase target |
|---|---|---|---|
| L1 | Chỉ hỗ trợ Windows | N/A | Phase 2: macOS |
| L2 | Chỉ `playwright-js` runtime | Dùng JS scripts | Phase 2: Python, C# |
| L3 | Không có multi-user | Chạy nhiều instance | Phase 3 |
| L4 | Không có TLS cho Local API | Localhost only, OS firewall | Phase 2 |
| L5 | SSH proxy cần manual setup | Document cách setup | Phase 2 |
| L6 | Script sandbox giới hạn | Document restrictions | Phase 2 |
| L7 | Không có Open API (cloud) | Chỉ Local API | Phase 3 |

---

*Tài liệu này hoàn thành bộ 10 tài liệu kỹ thuật cho dự án BrowserManager.*  
*Xem [00-tong-quan-du-an.md](00-tong-quan-du-an.md) để có tổng quan toàn bộ.*
