# Gates & Definition of Done — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Định nghĩa điều kiện PASS/FAIL cho từng Gate và DoD cho từng module.  
> **Người phê duyệt**: Product Owner + Tech Lead

---

## 1. Tổng quan

Tài liệu này định nghĩa chính xác các điều kiện để mỗi Gate được chấm **PASS** hoặc **FAIL**, kèm evidence cần cung cấp và người phê duyệt.

**Nguyên tắc**: Mọi Gate phải có evidence cụ thể (file + section), không chấp nhận "done by feeling".

---

## 2. Gates G0–G6

### Gate G0 — Bộ tài liệu đầy đủ Artefact

**Mục đích**: Đảm bảo tất cả artefact bắt buộc tồn tại trước khi review.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| `openapi.yaml` tồn tại và valid YAML | File `tai-lieu-du-an/openapi.yaml` + CI schema validation | Tech Lead |
| `14-parity-matrix.md` tồn tại với G2/G4 tables | File tồn tại, không trống | Tech Lead |
| `13-baseline-morelogin-public.md` tồn tại | File tồn tại | Tech Lead |
| `migration-plan.md` tồn tại | File tồn tại | Tech Lead |
| `threat-model.md` tồn tại | File tồn tại | Tech Lead + Security |
| `test-plan.md` tồn tại | File tồn tại | QA Lead |
| `scope.md` tồn tại | File tồn tại | Product Owner |
| `error-catalog.md` tồn tại | File tồn tại | Tech Lead |
| `data-dictionary.md` tồn tại | File tồn tại | Tech Lead |
| `job-spec.md` tồn tại | File tồn tại | Tech Lead |
| `runbook.md` tồn tại | File tồn tại | Ops Lead |

**FAIL condition**: Bất kỳ file nào trong danh sách trên không tồn tại.

**CI check**: `doc-consistency-check` (kiểm tra file tồn tại + nội dung nhất quán).

---

### Gate G1 — Nhất quán nội bộ

**Mục đích**: Không có mâu thuẫn giữa các docs (port, envelope, endpoint names).

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| Port `40000` nhất quán ở tất cả docs | `grep "40000"` trong tất cả `*.md` + `openapi.yaml` | Tech Lead |
| Compat envelope `{code,msg,data,requestId}` nhất quán | `12-api-compatibility.md` §4 + `openapi.yaml` response schemas | Tech Lead |
| Endpoint `removeToRecycleBin/batch` (không phải `delete`) | CI check `checkDeprecatedEndpointsAllDocs()` PASS | CI / Tech Lead |
| Không có deprecated config keys | CI check `checkConfigKeysConsistency()` PASS | CI / Tech Lead |
| Phương thức HTTP đúng (POST cho detail/getAllDebugInfo/etc.) | CI check `checkQAChecklist()` PASS | CI / Tech Lead |

**FAIL condition**: CI `doc-consistency-check` fail; hoặc manual review phát hiện mâu thuẫn.

**CI check**: `npm run check` trong `scripts/doc-consistency-check/`.

---

### Gate G2 — API Parity ≥ 97%

**Mục đích**: BrowserManager hỗ trợ ≥ 97% endpoints của MoreLogin public baseline.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| ≥ 29/30 endpoints có status ✅ Full | `14-parity-matrix.md` §2 — G2 Summary table, dòng **Tổng** | Tech Lead |
| N/A endpoints có đầy đủ exception doc | `scope-exceptions.md` với entry tương ứng | Product Owner |
| Không có missing endpoints (0 Missing) | `14-parity-matrix.md` G2 Summary — cột Missing = 0 | Tech Lead |
| Tất cả Full endpoints có spec trong openapi.yaml | `openapi.yaml` có path + schema + example | Tech Lead |
| G2 numbers trong `00-tong-quan-du-an.md` khớp `14-parity-matrix.md` | CI check `checkOverviewG2Numbers()` PASS | CI |

**FAIL condition**: < 29/30 Full; hoặc Missing > 0; hoặc CI fail.

**Ngưỡng**: 29/30 = 96.7% ≥ 90% threshold. Target: 29/30 Full + 1 N/A (cloud-only).

---

### Gate G3 — UX Parity ≥ 95%

**Mục đích**: Tất cả UX operations có spec đầy đủ trong GUI docs.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| ≥ 23/26 UX operations có status Full trong GUI spec | `14-parity-matrix.md` §3 — G3 UX Parity table | UX Lead |
| Restricted UX operations có governance placeholder | `08-desktop-gui.md` — mỗi Restricted screen có `[Restricted]` tag + governance note | UX Lead |
| Empty/error/loading states được spec cho mọi screen | `08-desktop-gui.md` — từng screen có states section | UX Lead |
| Bulk action flows được spec | `08-desktop-gui.md` §bulk-actions | UX Lead |
| Browser Synchronizer spec tồn tại | `08-desktop-gui.md` §4E — wireframe + API + CDP mechanism | UX Lead |

**FAIL condition**: < 23/26 UX Full; hoặc screen thiếu state documentation.

---

### Gate G4 — Data Model Parity ≥ 95%

**Mục đích**: Schema DB đủ cho implementation.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| Bảng `env_groups`, `env_tags`, `profile_tags` tồn tại trong migrations | `migration-plan.md` migration 006 | Tech Lead |
| Tất cả fields của Profile/Group/Tag/ProxyInfo có type/nullable/default/index | `data-dictionary.md` — mọi field có đủ 4 thuộc tính | Tech Lead |
| Field parity ≥ 95% (bảng G4 trong parity matrix) | `14-parity-matrix.md` §4 — G4 Summary, cột Full ≥ 95% | Tech Lead |
| Computed fields có formula và trigger rõ ràng | `data-dictionary.md` — section computed fields | Tech Lead |
| Soft delete lifecycle được spec | `profile-lifecycle.md` | Tech Lead |
| G4 summary numbers nhất quán với bảng chi tiết | CI check `checkG4SummaryCounts()` PASS | CI |

**FAIL condition**: Bảng quan trọng thiếu; field thiếu type/nullable; CI fail.

---

### Gate G5 — Security Spec Pass

**Mục đích**: Security được thiết kế từ đầu, không phải thêm sau.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| Threat model hoàn chỉnh với tất cả attack surfaces | `threat-model.md` — asset list + attack surface + controls | Security Lead |
| DPAPI encryption cho secrets spec đầy đủ | `09-bao-mat-va-luu-tru.md` §3, `threat-model.md` §controls | Security Lead |
| Token rotation mechanism có spec | `09-bao-mat-va-luu-tru.md` §5 | Security Lead |
| Rate limiting spec có giá trị cụ thể | `04-local-api.md` §rate-limit, `threat-model.md` | Security Lead |
| Audit log spec có đủ fields | `09-bao-mat-va-luu-tru.md` §audit, `threat-model.md` | Security Lead |
| Secure defaults được liệt kê | `threat-model.md` §secure-defaults | Security Lead |
| RBAC spec tồn tại trong `09-bao-mat-va-luu-tru.md` §8F | `09-bao-mat-va-luu-tru.md` §8F — Role model + Permission matrix đầy đủ | Security Lead |
| Permission matrix đầy đủ (30 compat + native endpoints) | `09-bao-mat-va-luu-tru.md` §8F.3 — tất cả endpoints có ADMIN/OPERATOR/VIEWER status | Security Lead |

**FAIL condition**: Thiếu bất kỳ control nào; threat model không đề cập attack surface nào.

---

### Gate G6 — Restricted Content Governance

**Mục đích**: Không có nội dung anti-detect/unethical; restricted features có governance.

| Điều kiện PASS | Evidence | Người phê duyệt |
|---|---|---|
| Không có nội dung fingerprint spoofing / anti-bot | Manual review tất cả `*.md` | Product Owner + Legal |
| Tất cả `[Restricted]` features có governance: ai được bật, audit, compliance | Mọi section tagged `[Restricted]` có governance block | Product Owner |
| `scope-exceptions.md` có đầy đủ ID, lý do, workaround, người ký | `scope-exceptions.md` — mọi exception có signature block | Product Owner |
| Out-of-scope features trong `scope.md` không bị implement | `scope.md` §3 — O03 không có implementation | Tech Lead |

**FAIL condition**: Phát hiện anti-detect content; Restricted feature không có governance.

---

## 3. Definition of Done — Theo Module

### DoD: M01 — Profile System

**Done** khi:
- [ ] `02-he-thong-profile.md` có đầy đủ: form fields, default values, validation rules, mutual exclusion rules
- [ ] `profile-lifecycle.md` có đủ: removeToRecycleBin, restore, permanent delete states
- [ ] `data-dictionary.md` profile table: tất cả fields có type/nullable/default/index
- [ ] Tests: ít nhất 5 test cases trong `test-plan.md` §profile
- [ ] Logs: create/update/delete events log format spec'd

### DoD: M02 — Background Agent & Job System

**Done** khi:
- [ ] `job-spec.md` có đủ: 5 states, retry policy, backoff, timeout, idempotency key
- [ ] `03-background-agent.md` có sequence diagram: request → enqueue → execute → logs → result
- [ ] Concurrency limits documented (max 20 jobs)
- [ ] Tests: ít nhất 5 test cases trong `test-plan.md` §agent
- [ ] Health-check endpoint spec'd

### DoD: M03 — Local API

**Done** khi:
- [ ] `openapi.yaml` có schema (request + response + errors) cho tất cả 30 compat + native endpoints
- [ ] `error-catalog.md` có tất cả error codes với HTTP code + app code + message + cách xử lý
- [ ] `12-api-compatibility.md` có 1-1 mapping field cho tất cả 30 endpoints
- [ ] Tests: tất cả endpoints có ít nhất 1 contract test case trong `test-plan.md`
- [ ] Rate limiting values documented

### DoD: M04 — CLI

**Done** khi:
- [ ] `05-cli-spec.md` có đủ: command list, flags, examples, exit codes, output modes
- [ ] Auth config lookup order documented (env → config file → prompt)
- [ ] Tests: ít nhất 3 CLI integration test cases

### DoD: M05/M06 — Browser Runtime & Automation

**Done** khi:
- [ ] `06-browser-runtime.md` có launch/proxy/extension spec
- [ ] `07-automation-framework.md` có script templates và error handling
- [ ] Tests: ít nhất 2 E2E automation test cases trong `test-plan.md`

### DoD: M07 — Desktop GUI

**Done** khi:
- [ ] `08-desktop-gui.md` có screen list + navigation + flows
- [ ] Mọi screen có: empty state, error state, loading state
- [ ] Bulk actions flows spec'd
- [ ] Permission/Restricted states spec'd
- [ ] Tests: smoke test checklist trong `test-plan.md` §gui

### DoD: M08 — Security & Storage

**Done** khi:
- [ ] `threat-model.md` có: asset list, attack surfaces, controls, secure defaults
- [ ] `09-bao-mat-va-luu-tru.md` có: DPAPI, token rotation, rate limit, audit log
- [ ] Gate G5 PASS

### DoD: M09 — Installer

**Done** khi:
- [ ] `11-installer-spec.md` có: ports, firewall, service, permissions, upgrade, rollback, data retention
- [ ] `runbook.md` có: "nếu lỗi X → làm gì" cho ít nhất 10 scenarios
- [ ] Tests: install/upgrade/uninstall test matrix

### DoD: M10 — MoreLogin Compat Layer

**Done** khi:
- [ ] `12-api-compatibility.md` có 1-1 mapping cho tất cả 30 endpoints
- [ ] Mỗi endpoint có: side effects, corner cases, error mapping
- [ ] `golden-responses/` có sample response cho mỗi endpoint
- [ ] Gate G2 PASS

---

## 4. Release Gate

Dự án sẵn sàng release khi **tất cả** các điều kiện sau đạt:

| # | Điều kiện | Evidence |
|---|---|---|
| R1 | G0–G6 tất cả PASS | `00-tong-quan-du-an.md` §3A |
| R2 | CI `doc-consistency-check` PASS | GitHub Actions log |
| R3 | Tất cả module DoD PASS | Checklist trong tài liệu này §3 |
| R4 | `test-plan.md` acceptance tests PASS | QA sign-off |
| R5 | `threat-model.md` security review PASS | Security Lead sign-off |
| R6 | Performance targets met | Load test results |
| R7 | `runbook.md` reviewed by Ops | Ops Lead sign-off |

---

## 5. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
