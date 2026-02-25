# Scope — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **SSOT cho**: Phạm vi dự án, KPI, định nghĩa hoàn thành  
> **Người phê duyệt**: Product Owner

---

## 1. Mục đích tài liệu

Tài liệu này là **Single Source of Truth (SSOT)** cho phạm vi dự án BrowserManager v1.0.  
Mọi quyết định về "feature này có trong scope không" đều phải tham chiếu tài liệu này.

**Nguyên tắc**: Nếu một tính năng không được liệt kê ở mục "In-Scope" → tự động là Out-of-Scope cho v1.0.

---

## 2. Phạm vi v1.0 — In-Scope (BẮT BUỘC)

### 2.1 Module danh sách

| # | Module | File Spec | Trạng thái |
|---|---|---|---|
| M01 | Profile System | `02-he-thong-profile.md` | ✅ Trong scope |
| M02 | Background Agent & Job System | `03-background-agent.md`, `job-spec.md` | ✅ Trong scope |
| M03 | Local API (HTTP localhost:40000) | `04-local-api.md` | ✅ Trong scope |
| M04 | CLI Tool | `05-cli-spec.md` | ✅ Trong scope |
| M05 | Browser Runtime (Playwright) | `06-browser-runtime.md` | ✅ Trong scope |
| M06 | Automation Framework | `07-automation-framework.md` | ✅ Trong scope |
| M07 | Desktop GUI (Windows 10+) | `08-desktop-gui.md` | ✅ Trong scope |
| M08 | Security & Storage | `09-bao-mat-va-luu-tru.md` | ✅ Trong scope |
| M09 | Installer (MSI/EXE) | `11-installer-spec.md` | ✅ Trong scope |
| M10 | MoreLogin Compat Layer (30 endpoints) | `12-api-compatibility.md` | ✅ Trong scope |
| M11 | Fingerprint Engine | `15-fingerprint-engine.md` | ✅ Trong scope |
| M12 | Browser Synchronizer (v1.1) | `08-desktop-gui.md` | 🔜 v1.1 |

### 2.2 Chi tiết từng module

#### M01 — Profile System
- Tạo/sửa/xoá/clone browser profile
- Cấu hình proxy per-profile
- Cấu hình extension per-profile
- Profile data isolation (tách biệt data dir)
- Recycle Bin (soft delete → restore → permanent delete)
- **Giới hạn**: tối đa 500 profiles active cùng lúc trên máy 16 GB RAM

#### M02 — Background Agent & Job System
- Windows Service hoặc System Tray background process
- Job queue: queued → running → succeeded/failed/canceled
- Retry policy với exponential backoff
- Concurrency: tối đa 20 jobs song song
- Health-check endpoint: `GET /health`

#### M03 — Local API
- HTTP server tại `127.0.0.1:40000`
- Bearer token authentication
- Tất cả 30 compat endpoints (xem `13-baseline-morelogin-public.md`)
- Native endpoints (xem `04-local-api.md`)
- Compat envelope: `{code, msg, data, requestId}`

#### M04 — CLI Tool
- Global npm/dotnet tool
- Tất cả commands liệt kê trong `05-cli-spec.md`
- Output modes: `--json` và human-readable
- Auth lookup: env var → config file → prompt

#### M05 — Browser Runtime
- Playwright-based browser launching
- Profile isolation (separate user-data-dir)
- Proxy injection per-profile
- Extension loading

#### M06 — Automation Framework
- Script runner via Playwright API
- Pre-built script templates
- Error handling & retry

#### M07 — Desktop GUI
- WPF hoặc Electron (Windows 10+)
- Profile list management
- Job monitoring với live log streaming
- Settings management
- Tất cả screens liệt kê trong `08-desktop-gui.md`

#### M08 — Security & Storage
- Local storage với DPAPI encryption cho secrets
- Token rotation
- Audit log
- Rate limiting trên Local API
- Threat model hoàn chỉnh (xem `threat-model.md`)
- RBAC / Scope-based token spec đầy đủ (Phase 2 implementation) — xem `09-bao-mat-va-luu-tru.md` §8F
- Operation Authorization GUI spec đầy đủ — xem `08-desktop-gui.md` §4F

#### M09 — Installer
- MSI/NSIS installer cho Windows 10+
- Upgrade không mất dữ liệu
- Silent install/uninstall
- Service registration tự động

#### M10 — MoreLogin Compat Layer
- 30 endpoints từ MoreLogin public baseline
- 1-1 field mapping (xem `12-api-compatibility.md`)
- Idempotency headers support

#### M11 — Fingerprint Engine
- Danh sách 14+ fingerprint properties per-profile
- Inject via CDP addInitScript trước page load
- Randomize strategy với seed-based consistency
- GUI: Fingerprint tab trong Create/Edit Profile wizard
- API: get/update/randomize fingerprint endpoints

#### M12 — Browser Synchronizer (v1.1)
- Leader/Follower model: 1 leader browser → N follower browsers
- CDP relay mechanism: `Input.dispatchMouseEvent`, `Input.dispatchKeyEvent`, `Page.navigate`
- Sync operations: mouse click, keyboard input, scroll, navigation, tab open/close
- API: `POST /api/sync/start`, `POST /api/sync/stop`, `GET /api/sync/status`, `POST /api/sync/event`
- GUI: Browser Synchronizer screen — spec tại `08-desktop-gui.md` §4E
- **Phát hành v1.1** (không phải v1.0)

---

## 3. Out-of-Scope (KHÔNG làm trong v1.0)

| # | Tính năng | Lý do | Exception ID |
|---|---|---|---|
| O01 | Cloud storage / cloud sync | Self-hosted only, không có cloud infra | EX-001 |
| O02 | Multi-user SaaS / Open API public cloud | Không phải use-case | — |
| O03 | Fingerprint spoofing / anti-detect nâng cao | Compliance + ethics | EX-002 |
| O04 | Android cloud phone | Ngoài phạm vi desktop | — |
| O05 | `/api/env/cache/cleanCloud` | Cloud-only endpoint | EX-001 |
| O06 | Multi-machine profile sync | Yêu cầu cloud infra | EX-001 |
| O07 | Public-facing REST API (internet-facing) | Security risk, out-of-scope | — |
| O08 | Mobile client | Desktop only | — |

> Xem chi tiết từng exception tại `scope-exceptions.md`.

---

## 4. Định nghĩa "100% Hoàn Thành"

### 4.1 Theo API Parity

| Tiêu chí | Ngưỡng Pass | Cách đo | SSOT |
|---|---|---|---|
| Endpoint coverage | ≥ 97% (29/30 Full; 1 N/A) | Bảng G2 trong `14-parity-matrix.md` | `14-parity-matrix.md` |
| Field parity | ≥ 95% Full across all entities | Bảng G4 trong `14-parity-matrix.md` | `14-parity-matrix.md` |
| Error codes | 100% mapped | `error-catalog.md` | `error-catalog.md` |

### 4.2 Theo Module

| Module | Tiêu chí Done | Evidence |
|---|---|---|
| M01 Profile | Spec đầy đủ form fields, validation, lifecycle | `02-he-thong-profile.md`, `profile-lifecycle.md` |
| M02 Agent | Job states/retry/timeout spec đầy đủ | `job-spec.md` |
| M03 Local API | Tất cả 30 compat + native endpoints có schema | `openapi.yaml`, `04-local-api.md` |
| M04 CLI | Tất cả commands có flags + examples + exit codes | `05-cli-spec.md` |
| M05 Browser | Browser launch/proxy/extension spec | `06-browser-runtime.md` |
| M06 Automation | Script templates + error handling spec | `07-automation-framework.md` |
| M07 GUI | Tất cả screens + flows + empty/error states | `08-desktop-gui.md` |
| M08 Security | Threat model + controls spec đầy đủ | `threat-model.md`, `09-bao-mat-va-luu-tru.md` |
| M09 Installer | Install/upgrade/uninstall/runbook | `11-installer-spec.md`, `runbook.md` |
| M10 Compat | 1-1 mapping đủ field + side-effects | `12-api-compatibility.md` |
| M11 Fingerprint | 14+ properties spec, inject logic, API + GUI | `15-fingerprint-engine.md` |

### 4.3 Theo Docs Gate

| Gate | Tiêu chí | SSOT |
|---|---|---|
| G0 | Artefact đầy đủ | `00-tong-quan-du-an.md` §3A |
| G1 | Nhất quán nội bộ (port, envelope) | `doc-consistency-check` CI |
| G2 | API parity ≥ 97% | `14-parity-matrix.md` G2 |
| G3 | UX parity ≥ 95% | `14-parity-matrix.md` G3 |
| G4 | Data model parity ≥ 95% | `14-parity-matrix.md` G4 |
| G5 | Security spec pass | `threat-model.md` |
| G6 | No restricted content without governance | `scope-exceptions.md` |

---

## 5. KPI Kỹ thuật

### 5.1 Performance

| KPI | Target | Điều kiện đo |
|---|---|---|
| API latency P95 | < 200ms | Local HTTP call, không có browser launch |
| API latency P99 | < 500ms | Local HTTP call |
| Browser launch time | < 3s | Profile đã tồn tại, proxy configured |
| Job enqueue → start | < 100ms | System idle, < 10 jobs in queue |
| GUI render list | < 1s | ≤ 200 profiles |

### 5.2 Concurrency

| KPI | Target | Ghi chú |
|---|---|---|
| Max concurrent browsers | 20 | Trên hardware 16 GB RAM, i7 |
| Max concurrent jobs | 20 | Worker pool size configurable |
| Max profiles stored | 500 | Tested và documented |
| Max profiles active | 20 | Concurrent browser instances |
| API request concurrency | 50 req/s | Rate limit default |

### 5.3 Resource Caps

| Resource | Cap | Hành động khi vượt |
|---|---|---|
| RAM per browser instance | 512 MB soft / 1 GB hard | Log warning / kill instance |
| Disk per profile | 2 GB (cache) | Cảnh báo, auto-clean nếu bật |
| Log retention | 30 ngày / 1 GB | Rotate tự động |
| Job history | 10,000 records | Auto-archive cũ nhất |

### 5.4 Availability

| KPI | Target |
|---|---|
| Agent uptime | 99.5% (restart < 5s sau crash) |
| API availability | 99.9% khi agent running |
| Max restart attempts | 5 lần, sau đó alert và stop |

---

## 6. Tài liệu liên quan

| File | Vai trò |
|---|---|
| `gates-and-dod.md` | Chi tiết Gate conditions và DoD |
| `14-parity-matrix.md` | Bảng parity API/Data/UX |
| `scope-exceptions.md` | Chi tiết các N/A và lý do |
| `00-tong-quan-du-an.md` | Tổng quan và trạng thái hiện tại |
| `openapi.yaml` | SSOT cho tất cả endpoints |

---

*Tài liệu này được phê duyệt bởi Product Owner. Mọi thay đổi scope phải cập nhật tài liệu này và thông qua review.*
