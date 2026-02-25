# 14 — Parity Matrix: MoreLogin ↔ BrowserManager

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-18 | **Trạng thái**: Review  
> **Mục đích**: Ma trận đối chiếu 1-1 tất cả tính năng MoreLogin (baseline từ `13-baseline-morelogin-public.md`) với trạng thái coverage của BrowserManager.

---

## 1. Hướng dẫn đọc bảng

| Cột | Ý nghĩa |
|---|---|
| **MoreLogin Item** | Endpoint / UX operation / Field từ baseline |
| **Status** | `Full` / `Partial` / `Missing` / `Restricted` / `N/A` |
| **BrowserManager Coverage** | File + Section reference |
| **Gap Description** | Mô tả khoảng cách còn lại |

### Status Legend

| Status | Ý nghĩa |
|---|---|
| ✅ **Full** | Đã có spec đầy đủ, 1-1 coverage |
| ⚠️ **Partial** | Có spec nhưng chưa đầy đủ field/behavior |
| ❌ **Missing** | Chưa có spec |
| 🔒 **Restricted** | Chỉ mô tả interface, không implement kỹ thuật nội bộ |
| 🚫 **N/A** | Không áp dụng (feature cloud-only) |

---

## 2. Parity Matrix — API Endpoints

### 2.1 Group A: `/api/env/*` — Profile & Session

| MoreLogin Endpoint | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| `POST /api/env/create/quick` | ✅ Full | `04-local-api.md` §4 (compat), `12-api-compatibility.md` | Mapped tới `POST /api/profiles` |
| `POST /api/env/create/advanced` | ✅ Full | `04-local-api.md` §4, `12-api-compatibility.md` | Fields `remark` (Migration 007) và `groupId` (UUID FK → `env_groups`) đã spec đầy đủ |
| `POST /api/env/start` | ✅ Full | `04-local-api.md` §4, `12-api-compatibility.md` | Response có `debugPort`, `webdriver`, `version` |
| `POST /api/env/close` | ✅ Full | `04-local-api.md` §4 | Mapped tới `POST /api/sessions/{id}/stop` |
| `POST /api/env/closeAll` | ✅ Full | `04-local-api.md` §4 | Mapped tới `POST /api/sessions/close-all` |
| `POST /api/env/active` | ✅ Full | `04-local-api.md` §4A.1a, `openapi.yaml` | Window focus behavior + session list — **Plan 4** |
| `POST /api/env/reopen` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Alias restart session — **Plan 4** |
| `POST /api/env/page` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Paginated filter endpoint |
| `POST /api/env/list` | ✅ Full | `04-local-api.md` §4 (`GET /api/profiles`) | Filter params theo MoreLogin format |
| `POST /api/env/detail` | ✅ Full | `04-local-api.md` §4 (`GET /api/profiles/{id}`) | — |
| `POST /api/env/update` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Alias PATCH /api/profiles/{id} — **Plan 4** |
| `POST /api/env/removeToRecycleBin/batch` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Soft delete → trash (correct MoreLogin endpoint name) |
| `POST /api/env/getAllDebugInfo` | ✅ Full | `04-local-api.md` §4 | Mapped tới `POST /api/sessions/debug-info` |
| `POST /api/env/getAllProcessIds` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | PID tất cả session |
| `POST /api/env/getAllScreen` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Screen info |
| `POST /api/env/removeLocalCache` | ✅ Full | `04-local-api.md` §4A.1 (`POST /api/profiles/{id}/clear-cache`) | Compat alias có |
| `POST /api/env/cache/cleanCloud` | 🚫 N/A | `scope-exceptions.md` §2 (E1) | Cloud-only endpoint — xem scope exception E1 cho chi tiết |
| `POST /api/env/arrangeWindows` | ✅ Full | `04-local-api.md` §4A.1, `openapi.yaml` | Sắp xếp cửa sổ |

**G2 Score — `/api/env/*`**: 17/18 Full + 0/18 Partial + 0/18 Missing + 1/18 N/A = **~94% coverage**

---

### 2.2 Group B: `/api/envgroup/*` — Group Management

| MoreLogin Endpoint | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| `POST /api/envgroup/page` | ✅ Full | `04-local-api.md` §4A.2, `openapi.yaml` | Paginated group list |
| `POST /api/envgroup/create` | ✅ Full | `04-local-api.md` §4A.2, `openapi.yaml` | Tạo group |
| `POST /api/envgroup/edit` | ✅ Full | `04-local-api.md` §4A.2, `openapi.yaml` | Sửa group |
| `POST /api/envgroup/delete` | ✅ Full | `04-local-api.md` §4A.2, `openapi.yaml` | Xóa group |

**G2 Score — `/api/envgroup/*`**: 4/4 Full = **100% coverage**

---

### 2.3 Group C: `/api/envtag/*` — Tag Management

| MoreLogin Endpoint | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| `GET /api/envtag/all` | ✅ Full | `04-local-api.md` §4A.3, `openapi.yaml` | Tất cả tags |
| `POST /api/envtag/create` | ✅ Full | `04-local-api.md` §4A.3, `openapi.yaml` | Tạo tag |
| `POST /api/envtag/edit` | ✅ Full | `04-local-api.md` §4A.3, `openapi.yaml` | Sửa tag |
| `POST /api/envtag/delete` | ✅ Full | `04-local-api.md` §4A.3, `openapi.yaml` | Xóa tag |

**G2 Score — `/api/envtag/*`**: 4/4 Full = **100% coverage**

---

### 2.4 Group D: `/api/proxyInfo/*` — Proxy Management

| MoreLogin Endpoint | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| `POST /api/proxyInfo/page` | ✅ Full | `04-local-api.md` §4A.4, `openapi.yaml` | Request/response spec đầy đủ; compat alias → `GET /api/proxies` đã có |
| `POST /api/proxyInfo/add` | ✅ Full | `04-local-api.md` §4 (`POST /api/proxies`) | — |
| `POST /api/proxyInfo/update` | ✅ Full | `04-local-api.md` §4 (`PATCH /api/proxies/{id}`), `openapi.yaml` | Compat alias có |
| `POST /api/proxyInfo/delete` | ✅ Full | `04-local-api.md` §4 (`DELETE /api/proxies/{id}`) | — |

**G2 Score — `/api/proxyInfo/*`**: 4/4 Full + 0/4 Partial = **100% coverage**

---

### 2.5 Group E: `/api/sync/*` — Profile synchronization

| MoreLogin Endpoint | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| `GET /api/sync/capabilities` | ✅ Full | `24-browser-sync-contract.md` §2; `openapi.yaml` | Returns schema version and conflict strategy |
| `POST /api/sync/push` | ✅ Full | same | Accepts SyncUnit, applies LWW conflict, logs audit |
| `GET /api/sync/pull` | ✅ Full | same | Returns units since given version |

**G2 Score — `/api/sync/*`**: 3/3 Full = **100% coverage**

---

### 📊 G2 API Parity Score Tổng hợp

| Group | Total Endpoints | Full | Partial | Missing | N/A | Score |
|---|---|---|---|---|---|---|
| `/api/env/*` | 18 | 17 | 0 | 0 | 1 | **94%** |
| `/api/envgroup/*` | 4 | 4 | 0 | 0 | 0 | **100%** |
| `/api/envtag/*` | 4 | 4 | 0 | 0 | 0 | **100%** |
| `/api/proxyInfo/*` | 4 | 4 | 0 | 0 | 0 | **100%** |
| `/api/sync/*` | 3 | 3 | 0 | 0 | 0 | **100%** |
| **Tổng** | **33** | **32** | **0** | **0** | **1** | **~97%** |

> **G2 Gate Verdict**: ✅ **PASS** — Coverage ~97% (32/33 Full; 1 N/A là cloud-only endpoint), đạt ngưỡng 90%.
> Ghi chú: 2 gaps Partial trước đây (`create/advanced`, `proxyInfo/page`) đã đóng — fields `remark`/`groupId` spec'd trong Migration 007/006; `proxyInfo/page` alias đã có trong `04-local-api.md` §4A.4.

---

## 3. Parity Matrix — Data Model

### 3.1 Profile / Environment Object Fields

| MoreLogin Field | Status | BrowserManager Field | Gap Description |
|---|---|---|---|
| `id` (UUID) | ✅ Full | `id` | — |
| `name` | ✅ Full | `name` | — |
| `groupId` (UUID FK) | ✅ Full | `group_id` (UUID FK → `env_groups`) | Bảng `env_groups` đã có |
| `groupName` (denorm) | ✅ Full | `group_name` (denorm) | Giữ denorm cho tốc độ |
| `tagIds` (array UUID) | ✅ Full | Junction `profile_tags` | Bảng `env_tags` + `profile_tags` đã có |
| `remark` | ✅ Full | `remark` | Đã thêm Migration 007 |
| `status` (0/1/2) | ✅ Full | `status` (enum string) | Format khác nhau nhưng semantics giống |
| `proxyId` (UUID FK) | ✅ Full | `proxy_id` | — |
| `e2e_encryption_enabled` | ✅ Full | `e2e_encryption_enabled` (BOOLEAN) [Restricted] | Đã thêm, xem `09-bao-mat-va-luu-tru.md` §8C |
| `lock_status` | ✅ Full | `lock_status` (TEXT CHECK) [Restricted] | Đã thêm, xem `09-bao-mat-va-luu-tru.md` §8D |
| `startUrl` | ✅ Full | `start_url` | — |
| `browserVersion` | ✅ Full | `kernel_ver` | — |
| `userAgent` | ✅ Full | `user_agent` | — |
| `osVersion` | ✅ Full | `os_version` | — |
| `screenResolution` | ✅ Full | `screen_res` | — |
| `timezone` | ✅ Full | `timezone` | — |
| `language` | ✅ Full | `language` | — |
| `createdAt` | ✅ Full | `created_at` | — |
| `updatedAt` | ✅ Full | `updated_at` | — |
| `lastUsedAt` | ✅ Full | `last_used_at` | Update khi session start — xem `02-he-thong-profile.md` §3A.2 |

**D4 Score — Profile fields**: 20/20 Full + 0/20 Partial + 0/20 Missing = **100% coverage**

---

### 3.2 Group Entity

| MoreLogin Field | Status | BrowserManager Entity | Gap Description |
|---|---|---|---|
| `id` | ✅ Full | `id` UUID PK | Bảng `env_groups` đã có |
| `name` | ✅ Full | `name` TEXT | — |
| `sortOrder` | ✅ Full | `sort_order` INTEGER | — |
| `color` | ✅ Full | `color` TEXT | — |
| `profileCount` | ✅ Full | Denormalized cached field (see `migration-plan.md` §2.4) | Application-layer compute + 24h refresh job |
| `createdAt` | ✅ Full | `created_at` DATETIME | — |

**D4 Score — Group entity**: 6/6 Full + 0/6 Partial = **100% coverage**

---

### 3.3 Tag Entity

| MoreLogin Field | Status | BrowserManager Entity | Gap Description |
|---|---|---|---|
| `id` | ✅ Full | `id` UUID PK | Bảng `env_tags` đã có |
| `name` | ✅ Full | `name` TEXT | — |
| `color` | ✅ Full | `color` TEXT | — |
| `profileCount` | ✅ Full | Denormalized cached field (see `migration-plan.md` §2.4) | Application-layer compute + 24h refresh job |
| `createdAt` | ✅ Full | `created_at` DATETIME | — |

**D4 Score — Tag entity**: 5/5 Full + 0/5 Partial = **100% coverage**

---

### 3.4 ProxyInfo Object

| MoreLogin Field | Status | BrowserManager Field | Gap Description |
|---|---|---|---|
| `id` | ✅ Full | `id` | — |
| `label` | ✅ Full | `label` | — |
| `type` | ✅ Full | `type` | — |
| `host` | ✅ Full | `host` | — |
| `port` | ✅ Full | `port` | — |
| `username` | ✅ Full | `username` | — |
| `refreshUrl` | ✅ Full | `refresh_url` | — |
| `lastStatus` | ✅ Full | `last_status` | — |
| `lastChecked` | ✅ Full | `last_checked` | — |
| `profileCount` | ✅ Full | Denormalized cached field (see `migration-plan.md` §2.4) | Application-layer compute + 24h refresh job |

**D4 Score — ProxyInfo fields**: 10/10 Full + 0/10 Partial = **100% coverage**

---

### 📊 G4 Data Model Score Tổng hợp

| Entity | Fields | Full | Partial | Missing | Score |
|---|---|---|---|---|-|
| Profile | 20 | 20 | 0 | 0 | **100%** |
| Group | 6 | 6 | 0 | 0 | **100%** |
| Tag | 5 | 5 | 0 | 0 | **100%** |
| ProxyInfo | 10 | 10 | 0 | 0 | **100%** |
| **Tổng** | **41** | **41** | **0** | **0** | **100%** |

> **G4 Gate Verdict**: ✅ **PASS** — Coverage 100%. Tất cả fields đã có spec đầy đủ: bảng `env_groups`, `env_tags`, `profile_tags` trong Migration 006; fields `e2e_encryption_enabled`, `lock_status`, `remark`, `last_used_at` trong Migration 007; computed field `profileCount` được document trong `migration-plan.md` §2.4.

---

## 4. Parity Matrix — UX Operations

| MoreLogin UX Operation | Status | BrowserManager Coverage | Gap Description |
|---|---|---|---|
| Launch browser | ✅ Full | `08-desktop-gui.md` §4.1 (Launch button trong Actions ▶) | — |
| Stop browser | ✅ Full | `08-desktop-gui.md` §4.1 (Stop button ⏹ trong Actions ▶) | — |
| Create profile (wizard) | ✅ Full | `08-desktop-gui.md` §4.2 (3-step wizard incl. Advanced step 2b) | — |
| Edit profile (side panel) | ✅ Full | `08-desktop-gui.md` §4.3 (Detail panel incl. Advanced tab) | — |
| Delete profile → trash | ✅ Full | `08-desktop-gui.md` §4.1 Actions menu (⋮) | — |
| Restore from trash | ✅ Full | `08-desktop-gui.md` §4.5 | — |
| Clone profile | ✅ Full | `08-desktop-gui.md` §4.1 Actions menu (⋮) | — |
| Export profile | ✅ Full | `08-desktop-gui.md` §4.1 Actions menu (⋮) | — |
| **Copy Profile ID** | ✅ Full | `08-desktop-gui.md` §4.1 Actions menu (⋮) — "Copy Profile ID" → clipboard | — |
| **Refresh Fingerprint** [Restricted — v1.3+] | 🔒 Restricted | `08-desktop-gui.md` §4.1 Actions menu (⋮), nhãn `[Restricted — v1.3+]` | Hiển thị placeholder trong menu; không implement logic trong v1 |
| Filter by Group | ✅ Full | `08-desktop-gui.md` §4.1 filter bar `[Group ▼]` | — |
| Filter by Tag | ✅ Full | `08-desktop-gui.md` §4.1 filter bar `[Tag ▼]` (multi-select, dùng tag entity từ `env_tags`) | — |
| Filter by Status | ✅ Full | `08-desktop-gui.md` §4.1 filter bar `[Status ▼]` — All/Active/Idle/Error/Locked | — |
| Filter by Proxy Type | ✅ Full | `08-desktop-gui.md` §4.1 filter bar `[Proxy Type ▼]` — All/HTTP/SOCKS5/SSH/None | — |
| Filter by Date Created | ✅ Full | `08-desktop-gui.md` §4.1 filter bar `[Date Created ▼]` — Today/7d/30d/Custom range | — |
| Column Settings | ✅ Full | `08-desktop-gui.md` §4.1a — `[⚙ Columns ▼]` dropdown với checkboxes + Reset | — |
| Bulk: Set Group | ✅ Full | `08-desktop-gui.md` §4.4 | — |
| Bulk: Set Proxy | ✅ Full | `08-desktop-gui.md` §4.4 | — |
| Bulk: Add Tag | ✅ Full | `08-desktop-gui.md` §4.4 | — |
| Bulk: Remove Tag | ✅ Full | `08-desktop-gui.md` §4.4 | — |
| Bulk: Delete Selected | ✅ Full | `08-desktop-gui.md` §4.4 | — |
| Clear Local Cache | ✅ Full | `08-desktop-gui.md` §4.3 (multi-type cache selector) | — |
| Group Management screen | ✅ Full | `08-desktop-gui.md` §4B — CRUD groups, inline edit, delete confirm, filter-by-group link | — |
| Tag Management screen | ✅ Full | `08-desktop-gui.md` §4C — CRUD tags, color picker, profile count, New Tag dialog | — |
| E2E Encryption setting [Restricted — v1.2+] | 🔒 Restricted | `08-desktop-gui.md` §4.1 Actions menu; `09-bao-mat-va-luu-tru.md` §8C.4 (GUI toggle + encryptKey dialog) | UI spec đầy đủ; implementation v1.2+ theo §8E |
| arrangeWindows UI | ✅ Full | `08-desktop-gui.md` §3.4 — dialog layout/cascade/tile, session selection, POST compat endpoint | — |
| Operation Authorization GUI | ✅ Full | `08-desktop-gui.md` §4F — Token Management screen, Create Token dialog, permission behavior, audit log view | Spec hoàn chỉnh §4F |
| Browser Synchronizer | ✅ Full | `08-desktop-gui.md` §4E — wireframe, CDP relay, API endpoints `/api/sync/*` | Spec hoàn chỉnh §4E (v1.1) |

**G3 Score — UX Operations**: 25/28 Full + 0/28 Partial + 0/28 Missing + 3/28 Restricted = **~100% coverage** (Restricted items đã có spec đầy đủ, không implement v1)

> **G3 Gate Verdict**: ✅ **PASS** — Coverage 100%. Tất cả UX operations đã có spec trong `08-desktop-gui.md`. Operation Authorization spec đầy đủ §4F; Browser Synchronizer spec đầy đủ §4E (v1.1). 3 items Restricted (`Refresh Fingerprint`, `E2E Encryption setting`, `Lock Status`) hiển thị placeholder trong UI với nhãn Phase/Restricted rõ ràng.

---

## 5. Parity Matrix — Response Envelope

| Item | MoreLogin Format | BrowserManager Status | Gap |
|---|---|---|---|
| Success envelope | `{code, msg, data, requestId}` | ✅ Full | Compat mode trả `{code: 0, msg: "success", data: {...}, requestId: "..."}` — spec'd trong `12-api-compatibility.md` §4 |
| Error envelope | `{code, msg, data: null}` (code≠0) | ✅ Full | Compat mode trả `{code: -1, msg: "error message", data: null}` — `CompatibilityResponseTransformer` trong `12-api-compatibility.md` §4 |
| `code = 0` for success | Required in compat | ✅ Full | `CompatibilityResponseTransformer.ToMoreLoginFormat()` trả `code = 0` khi success — xem `12-api-compatibility.md` §4 |
| `requestId` field | camelCase | ✅ Full | Compat middleware thêm `requestId` (camelCase) vào response — xem `12-api-compatibility.md` §4 (đã cập nhật) |

**G1 Score — Envelope**: 4/4 Full = **100% coverage**

> **G1 Gate Verdict**: ✅ **PASS** — Compat envelope `{code, msg, data, requestId}` được spec đầy đủ trong `12-api-compatibility.md` §4. Native envelope `{data, request_id, timestamp}` giữ nguyên cho native mode.

---

## 6. Parity Matrix — Security / Interface

| MoreLogin Security Feature | Status | BrowserManager Coverage | Gap |
|---|---|---|---|
| API token authentication | ✅ Full | `09-bao-mat-va-luu-tru.md` §3, `04-local-api.md` §2 | — |
| Proxy password encryption | ✅ Full | `09-bao-mat-va-luu-tru.md` §4 (DPAPI) | — |
| Rate limiting | ✅ Full | `04-local-api.md` §2.3, `09-bao-mat-va-luu-tru.md` §7 | — |
| localhost-only binding | ✅ Full | `03-background-agent.md` §5, `09-bao-mat-va-luu-tru.md` §7 | — |
| Log masking | ✅ Full | `09-bao-mat-va-luu-tru.md` §5 | — |
| E2E Encryption interface [Restricted] | ✅ Full | `09-bao-mat-va-luu-tru.md` §8C | Đã có spec field + behavior đầy đủ |
| Lock Status interface [Restricted] | ✅ Full | `09-bao-mat-va-luu-tru.md` §8D | Đã có spec field + behavior đầy đủ |
| Threat model documented | ✅ Full | `09-bao-mat-va-luu-tru.md` §8, `01-kien-truc-he-thong.md` §8 | — |
| RBAC / Scope-based token spec | ✅ Full | `09-bao-mat-va-luu-tru.md` §8F — Role model, Permission matrix, Token management API | Phase 2 implementation spec đầy đủ |

**G5 Score — Security**: 9/9 Full = **100% coverage**

> **G5 Gate Verdict**: ✅ **PASS** — E2E Encryption + Lock Status interface spec được bổ sung trong `09-bao-mat-va-luu-tru.md` §8C/8D.

---

## 7. Tổng hợp Gate Score

| Gate | Name | Score | Verdict | Ghi chú |
|---|---|---|---|---|
| **G0** | Artefact completeness | 100% | ✅ **PASS** | `openapi.yaml`, `migration-plan.md`, `scripts/`, `REVIEW-REPORT.md` đầy đủ |
| **G1** | Internal consistency | 100% | ✅ **PASS** | Port 40000 nhất quán; compat envelope `{code,msg,data,requestId}` spec đầy đủ trong `12-api-compatibility.md` §4 |
| **G2** | API parity 1-1 | ~97% | ✅ **PASS** | 29/30 Full; 1 N/A (cloud-only); 0 Missing |
| **G3** | UX parity 1-1 | 100% | ✅ **PASS** | 25/28 Full; 3 Restricted (spec đầy đủ cho tất cả operations, implement Phase 2+) |
| **G4** | Data model parity | 100% | ✅ **PASS** | Tất cả fields đã có spec đầy đủ: bảng entities, restricted fields, computed fields (xem `migration-plan.md` §2.4 và `scope-exceptions.md`) |
| **G5** | Security parity | 100% | ✅ **PASS** | E2E Encryption + Lock Status interface spec đầy đủ trong §8C/8D; v1 enforcement scope được chốt rõ trong `09-bao-mat-va-luu-tru.md` §8E |
| **G6** | Restricted governance | 100% | ✅ **PASS** | Out-of-scope gắn nhãn đúng, không có bypass docs |

---

## 8. Roadmap để Pass G0–G6 (Cập nhật sau Plan 4)

> **Trạng thái hiện tại (2026-02-18)**: **Tất cả G0–G6 đạt ✅ PASS** ở mức spec/documentation. Implementation cần thực hiện theo roadmap dưới.

### Để giữ G2 PASS (API parity) — Priority: 🟡 Maintain

1. Implement 28 endpoints theo `openapi.yaml` (native mode + compat layer)
2. Integration test: chạy MoreLogin-style script với BrowserManager backend
3. ~~Chuyển `proxyInfo/page` alias vào `04-local-api.md`~~ — **Đã đóng** (alias có tại §4A.4)
4. ~~Bổ sung field `remark`, `groupId` cho `create/advanced`~~ — **Đã đóng** (spec đầy đủ tại Migration 007/006)

### Để giữ G3 PASS (UX parity) — Priority: 🟡 Maintain

1. Implement Group Management screen (CRUD groups) — spec tại `08-desktop-gui.md` §4B
2. Implement Tag Management screen (CRUD tags + color picker) — spec tại `08-desktop-gui.md` §4C
3. Implement Bookmarks Management screen — spec tại `08-desktop-gui.md` §4D
4. Implement arrangeWindows dialog — spec tại `08-desktop-gui.md` §3.4
5. Implement Advanced Profile Settings (Step 2b + Edit tab Advanced) — spec tại `08-desktop-gui.md` §4.2
6. Implement Column Settings `[⚙ Columns ▼]` — spec tại `08-desktop-gui.md` §4.1a
7. Implement full filter bar (Status/Proxy Type/Date Created) — spec tại `08-desktop-gui.md` §4.1
8. Implement Copy Profile ID trong Actions menu (⋮) — spec tại `08-desktop-gui.md` §4.1
9. Implement Restricted items placeholder (Refresh Fingerprint, E2E toggle, Operation Authorization) — hiển thị disabled + tooltip "Phase 2" không cần logic
10. Browser Synchronizer — spec đầy đủ tại `08-desktop-gui.md` §4E (v1.1 implementation)

### Để giữ G4 PASS (Data model) — Priority: 🟡 Maintain

1. Chạy Migration 006 (env_groups, env_tags, profile_tags, group_id FK)
2. Chạy Migration 007 (remark, e2e_encryption_enabled, lock_status, last_used_at)
3. Chạy Migration 008 (proxy profile_count)

### Để giữ G5 PASS (Security) — Priority: 🟡 Maintain

1. Implement E2E Encryption check khi session start (theo `09-bao-mat-va-luu-tru.md` §8C)
2. Implement Lock Status enforcement (theo `09-bao-mat-va-luu-tru.md` §8D)
3. Security audit theo `09-bao-mat-va-luu-tru.md` §8B threat model

---

*Tài liệu liên quan: [13-baseline-morelogin-public.md](13-baseline-morelogin-public.md) | [04-local-api.md](04-local-api.md)*
