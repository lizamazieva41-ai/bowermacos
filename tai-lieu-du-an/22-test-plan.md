# Test Plan — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Kế hoạch test đầy đủ: API contract, migration, agent, GUI smoke, performance.  
> **Người phê duyệt**: QA Lead + Tech Lead

---

## 1. Tổng quan

### 1.1 Test Scope

| Layer | Tool | Automation |
|---|---|---|
| API Contract Tests | REST Client (Hurl/Postman/Newman) | CI |
| Unit Tests | xUnit (C#) / Jest (JS) | CI |
| Integration Tests | xUnit + TestContainers | CI |
| Agent Resilience Tests | xUnit + process manipulation | CI |
| GUI Smoke Tests | Playwright + Windows | Manual / Semi-auto |
| Performance Tests | k6 / Bombardier | Manual (pre-release) |
| Data Migration Tests | SQL scripts + validation | CI |

### 1.2 Môi trường test

| Env | Mô tả | Khi nào dùng |
|---|---|---|
| Local | Developer machine Windows 10+ | Dev testing |
| CI | GitHub Actions Windows runner | Every PR |
| QA | Dedicated QA Windows machine | Pre-release |

### 1.3 Golden Responses

File golden response nằm tại `golden-responses/` directory.  
Mỗi file là JSON response mẫu cho 1 endpoint.  
Dùng trong contract tests để so sánh cấu trúc response (không so sánh values động).

---

## 2. API Contract Tests

### 2.1 `/api/env/create/quick` — POST

**Mục đích**: Tạo profile với cấu hình tối thiểu.

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-001 | Create profile basic | `{"name": "Test Profile 1"}` | HTTP 200, `code: 0`, `data.envId` UUID format |
| TC-ENV-002 | Duplicate name | `{"name": "Test Profile 1"}` (lần 2) | HTTP 409, `code: -1002` |
| TC-ENV-003 | Missing name | `{}` | HTTP 400, `code: -1601` |
| TC-ENV-004 | Name too long | `{"name": "A".repeat(201)}` | HTTP 400, `code: -1606` |
| TC-ENV-005 | With proxy config | `{"name": "Proxy Profile", "proxyType": "http", "proxyHost": "127.0.0.1", "proxyPort": 8080}` | HTTP 200, `code: 0` |
| TC-ENV-006 | Invalid proxy type | `{"name": "Bad Proxy", "proxyType": "invalid"}` | HTTP 400, `code: -1604` |

**Golden file**: `golden-responses/env-create-quick.json`

---

### 2.2 `/api/env/create/advanced` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-010 | Create advanced | `{"name": "Advanced", "browserType": "chromium", "windowWidth": 1920, "windowHeight": 1080}` | HTTP 200, `code: 0` |
| TC-ENV-011 | Invalid browser type | `{"name": "Test", "browserType": "ie"}` | HTTP 400, `code: -1604` |
| TC-ENV-012 | Window size out of range | `{"name": "Test", "windowWidth": 100}` | HTTP 400, `code: -1603` |

**Golden file**: `golden-responses/env-create-advanced.json`

---

### 2.3 `/api/env/start` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-020 | Start existing stopped profile | `{"id": "<valid_env_id>"}` | HTTP 200, `code: 0`, `data.debugPort` integer |
| TC-ENV-021 | Start already running | `{"id": "<running_env_id>"}` | HTTP 409, `code: -1005`, returns current debug port |
| TC-ENV-022 | Start non-existent | `{"id": "non-existent-id"}` | HTTP 404, `code: -1001` |
| TC-ENV-023 | Start soft-deleted | `{"id": "<deleted_env_id>"}` | HTTP 422, `code: -1004` |

**Golden file**: `golden-responses/env-start.json`

---

### 2.4 `/api/env/close` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-030 | Close running profile | `{"id": "<running_env_id>"}` | HTTP 200, `code: 0` |
| TC-ENV-031 | Close already stopped (idempotent) | `{"id": "<stopped_env_id>"}` | HTTP 200, `code: 0` |
| TC-ENV-032 | Close non-existent | `{"id": "non-existent"}` | HTTP 404, `code: -1001` |

**Golden file**: `golden-responses/env-close.json`

---

### 2.5 `/api/env/list` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-040 | List all | `{}` | HTTP 200, `code: 0`, `data` array |
| TC-ENV-041 | Soft-deleted excluded | After soft delete | Deleted profile NOT in response |
| TC-ENV-042 | Filter by group | `{"groupId": "<group_id>"}` | Only profiles in group |

**Golden file**: `golden-responses/env-list.json`

---

### 2.6 `/api/env/page` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-050 | First page | `{"pageNum": 1, "pageSize": 10}` | HTTP 200, `data.total`, `data.list` array, `data.pageNum: 1` |
| TC-ENV-051 | Invalid page | `{"pageNum": 0}` | HTTP 400, `code: -1607` |
| TC-ENV-052 | Page size too large | `{"pageNum": 1, "pageSize": 101}` | HTTP 400, `code: -1607` |

**Golden file**: `golden-responses/env-page.json`

---

### 2.7 `/api/env/detail` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-060 | Get existing | `{"id": "<valid_env_id>"}` | HTTP 200, `code: 0`, full profile object |
| TC-ENV-061 | Non-existent | `{"id": "bad-id"}` | HTTP 404, `code: -1001` |

**Golden file**: `golden-responses/env-detail.json`

---

### 2.8 `/api/env/update` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-070 | Update name | `{"id": "<id>", "name": "New Name"}` | HTTP 200, `code: 0` |
| TC-ENV-071 | Update to duplicate name | `{"id": "<id>", "name": "<existing_name>"}` | HTTP 409, `code: -1002` |

---

### 2.9 `/api/env/removeToRecycleBin/batch` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-080 | Soft delete single | `{"ids": ["<id>"]}` | HTTP 200, `code: 0` |
| TC-ENV-081 | Soft delete batch | `{"ids": ["<id1>", "<id2>"]}` | HTTP 200, partial success response |
| TC-ENV-082 | Include non-existent IDs | `{"ids": ["<id>", "fake-id"]}` | HTTP 200, `data.succeeded`, `data.failed` |

**Golden file**: `golden-responses/env-remove-to-recycle-bin.json`

---

### 2.10 `/api/env/active` — POST

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-ENV-090 | Get active (running) | `{"id": "<running_id>"}` | HTTP 200, `data.debugPort` |
| TC-ENV-091 | Not running | `{"id": "<stopped_id>"}` | HTTP 422, `code: -1003` or debug info empty |

**Golden file**: `golden-responses/env-active.json`

---

### 2.11 Group Endpoints

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-GRP-001 | List groups (page) | `{"pageNum": 1, "pageSize": 10}` | HTTP 200, list of groups |
| TC-GRP-002 | Create group | `{"name": "Group A"}` | HTTP 200, `data.groupId` |
| TC-GRP-003 | Edit group | `{"groupId": "<id>", "name": "Group B"}` | HTTP 200 |
| TC-GRP-004 | Delete empty group | `{"groupId": "<empty_group_id>"}` | HTTP 200 |
| TC-GRP-005 | Delete group with profiles | `{"groupId": "<group_with_profiles>"}` | HTTP 422, `code: -1103` |

**Golden files**: `golden-responses/envgroup-*.json`

---

### 2.12 Tag Endpoints

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-TAG-001 | Get all tags | `{}` (GET) | HTTP 200, array of tags |
| TC-TAG-002 | Create tag | `{"name": "automation"}` | HTTP 200, `data.tagId` |
| TC-TAG-003 | Edit tag | `{"tagId": "<id>", "name": "auto2"}` | HTTP 200 |
| TC-TAG-004 | Delete unused tag | `{"tagId": "<id>"}` | HTTP 200 |
| TC-TAG-005 | Delete tag in use | `{"tagId": "<used_id>"}` | HTTP 422, `code: -1204` |

---

### 2.13 ProxyInfo Endpoints

| # | Test Case | Input | Expected |
|---|---|---|---|
| TC-PRX-001 | List proxies (page) | `{"pageNum": 1, "pageSize": 10}` | HTTP 200, list |
| TC-PRX-002 | Add proxy | `{"proxyType": "http", "proxyHost": "1.2.3.4", "proxyPort": 8080}` | HTTP 200 |
| TC-PRX-003 | Update proxy | `{"proxyId": "<id>", "proxyPort": 8081}` | HTTP 200 |
| TC-PRX-004 | Delete unused proxy | `{"proxyId": "<unused_id>"}` | HTTP 200 |
| TC-PRX-005 | Delete proxy in use | `{"proxyId": "<used_id>"}` | HTTP 422, `code: -1304` |

---

### 2.14 Authentication Tests

| # | Test Case | Expected |
|---|---|---|
| TC-AUTH-001 | No token | HTTP 401, `code: -1501` |
| TC-AUTH-002 | Invalid token | HTTP 401, `code: -1502` |
| TC-AUTH-003 | Valid token | HTTP 200 |
| TC-AUTH-004 | Rate limit exceeded | HTTP 429, `code: -1505`, `Retry-After` header |

---

## 3. Data Migration Tests

| # | Test Case | How | Expected |
|---|---|---|---|
| TC-MIG-001 | Fresh install (migration 001) | Run agent on empty DB | All tables created |
| TC-MIG-002 | Upgrade v1.0→v1.1 (migration 006) | Run on existing DB | `env_groups`, `env_tags`, `profile_tags` tables created |
| TC-MIG-003 | Idempotent migration | Run migration twice | No error, same schema |
| TC-MIG-004 | Data preserved after migration | Populate data → run 006 | Existing profiles unchanged |
| TC-MIG-005 | Migration failure rollback | Corrupt migration 006 | DB rolled back to pre-migration state; agent refuses to start |

---

## 4. Agent Resilience Tests

| # | Test Case | How | Expected |
|---|---|---|---|
| TC-AGT-001 | Agent crash → auto restart | Kill agent process | Agent restarts within 5s; jobs resume |
| TC-AGT-002 | Running job after crash | Kill agent mid-job | Job set to `failed` on restart; retry if policy allows |
| TC-AGT-003 | Health check when idle | `GET /health` | HTTP 200, `status: "ok"` |
| TC-AGT-004 | Health check when overloaded | 20 concurrent browsers | HTTP 200, `status` may be `"degraded"` |
| TC-AGT-005 | Job timeout | Submit job with 1s timeout | Job → `failed` with `error_message: "Execution timeout"` |
| TC-AGT-006 | Job cancel | Submit + immediately cancel | Job → `canceled` |
| TC-AGT-007 | Max concurrent jobs | Submit 25 jobs | 20 run concurrently; rest `queued`; 21st+ return `-1403` if queue full |
| TC-AGT-008 | Idempotency key | Submit same job twice with same key | Second call returns existing job, not new one |

---

## 5. GUI Smoke Tests

| # | Test Case | Steps | Expected |
|---|---|---|---|
| TC-GUI-001 | App launches | Start app | Main window visible; profile list loads |
| TC-GUI-002 | Create profile wizard | Open wizard → fill basic fields → save | New profile appears in list |
| TC-GUI-003 | Open profile | Select profile → click Open | Browser window opens; status → running |
| TC-GUI-004 | Close profile | Click Close on running profile | Browser closes; status → stopped |
| TC-GUI-005 | Delete profile (soft) | Select → Delete → confirm | Profile moves to recycle bin; disappears from list |
| TC-GUI-006 | Recycle bin view | Open recycle bin | Deleted profiles visible |
| TC-GUI-007 | Restore from bin | Select in recycle bin → Restore | Profile back in main list |
| TC-GUI-008 | Settings page | Open Settings | API port, token visible (masked) |
| TC-GUI-009 | Job monitoring | Open profile → switch to Jobs tab | Job status updates in real-time |
| TC-GUI-010 | Empty state | No profiles | Empty state message shown |
| TC-GUI-011 | Error state | Agent not running | Error banner shown; "Start Agent" button |
| TC-GUI-012 | Bulk select + delete | Select multiple → Bulk Delete | All selected soft-deleted |

---

## 6. Performance Tests

### 6.1 Targets

| Test | Load | Target |
|---|---|---|
| API latency (simple GET) | 1 user | P95 < 50ms |
| API latency (list 200 profiles) | 1 user | P95 < 200ms |
| API concurrent requests | 50 concurrent | P95 < 500ms, 0 errors |
| Browser launch | 1 sequential | < 3s |
| Browser launch concurrent | 5 parallel | All launched < 10s |
| Job throughput | 20 concurrent | All queued jobs start < 500ms |

### 6.2 Performance Test Tool

```bash
# Using k6
k6 run --vus 50 --duration 30s performance/api-load-test.js

# Verify thresholds
k6 run --vus 1 performance/api-latency-test.js
```

---

## 7. Definition of Done — QA Sign-off Checklist

Trước khi release, QA Lead phải tick tất cả:

- [ ] Tất cả TC-ENV-* PASS (30/30 contract tests)
- [ ] Tất cả TC-GRP-* PASS
- [ ] Tất cả TC-TAG-* PASS
- [ ] Tất cả TC-PRX-* PASS
- [ ] Tất cả TC-AUTH-* PASS
- [ ] Tất cả TC-MIG-* PASS
- [ ] Tất cả TC-AGT-* PASS
- [ ] Tất cả TC-GUI-* PASS (manual)
- [ ] Performance targets met
- [ ] CI `doc-consistency-check` PASS
- [ ] No open P0/P1 bugs

---

## 8. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
