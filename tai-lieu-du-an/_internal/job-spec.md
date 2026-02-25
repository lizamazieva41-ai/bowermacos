# Job Spec — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Đặc tả đầy đủ hệ thống Job Queue: states, retry, timeout, concurrency, idempotency.  
> **SSOT cho**: Background Agent job model.

---

## 1. Tổng quan

Background Agent sử dụng một **internal job queue** để xử lý tất cả tác vụ bất đồng bộ.  
Mỗi API call có side-effect (start browser, run script, clear cache) được thực thi qua job queue.

### Nguyên tắc thiết kế

- **Decoupled**: API nhận request → enqueue job → trả `jobId` ngay lập tức (non-blocking)
- **Durable**: Jobs được persist trong SQLite; không mất khi agent restart
- **Idempotent**: Client có thể gửi `idempotencyKey` để tránh duplicate jobs
- **Observable**: Mọi transition có log; client có thể poll status hoặc nhận event

---

## 2. Job States

### 2.1 State Machine

```
              ENQUEUE
                │
                ▼
          ┌─────────┐
          │  queued  │◄──────── RETRY (sau failed)
          └─────────┘
                │
                │ Worker picks up
                ▼
          ┌─────────┐
          │ running  │
          └─────────┘
           /        \
          /          \
   SUCCESS           FAILURE / TIMEOUT
       │                    │
       ▼                    ▼
  ┌──────────┐        ┌──────────┐
  │succeeded │        │  failed  │
  └──────────┘        └──────────┘
                           │
                    retry_count < max_retries
                           │
                           └──► RETRY → queued

                      retry_count >= max_retries
                           │
                           └──► final failed


  Từ bất kỳ non-terminal state:
  ┌─────────────┐
  │   canceled   │
  └─────────────┘
```

### 2.2 State Definitions

| State | Mô tả | Terminal? |
|---|---|---|
| `queued` | Job đang chờ worker | No |
| `running` | Worker đang thực thi | No |
| `succeeded` | Hoàn thành thành công | ✅ Yes |
| `failed` | Thất bại (hết retry hoặc non-retryable) | ✅ Yes |
| `canceled` | Bị hủy bởi user/system | ✅ Yes |

**Terminal states**: `succeeded`, `failed`, `canceled` — không thể transition sang state khác.

---

## 3. Job Types

| `job_type` | Mô tả | Timeout Default | Max Retries Default | Idempotent? |
|---|---|---|---|---|
| `browser_start` | Khởi động browser instance | 30s | 2 | No (debug port varies) |
| `browser_stop` | Đóng browser instance | 15s | 3 | Yes |
| `browser_stop_all` | Đóng tất cả browsers | 30s | 1 | Yes |
| `script_run` | Chạy automation script | 300s | 1 | Depends on script |
| `cache_clear_local` | Xóa cache local của profile | 60s | 3 | Yes |
| `cache_clear_cloud` | N/A (out of scope) | — | — | — |
| `proxy_test` | Kiểm tra kết nối proxy | 15s | 2 | Yes |
| `profile_clone` | Clone profile (copy data dir) | 120s | 1 | No |
| `db_migration` | Chạy DB migration | 60s | 0 | Yes |
| `recycle_bin_cleanup` | Auto-expire recycle bin | 300s | 1 | Yes |

---

## 4. Retry Policy

### 4.1 Nguyên tắc

- **Retryable errors**: Transient failures (timeout, resource busy, network error)
- **Non-retryable errors**: Business rule violations, validation errors, permanent failures
- **Backoff**: Exponential backoff với jitter

### 4.2 Backoff Formula

```
delay = min(base_delay * 2^retry_count + jitter, max_delay)

base_delay = 1s
max_delay  = 60s
jitter     = random(0, 1000ms)
```

| Retry # | Min delay | Max delay |
|---|---|---|
| 1st retry | 1s | 2s |
| 2nd retry | 2s | 4s |
| 3rd retry | 4s | 8s |
| 4th retry | 8s | 16s |
| 5th retry | 16s | 32s |

### 4.3 Retry Configuration per Job Type

| `job_type` | `max_retries` | Retryable conditions |
|---|---|---|
| `browser_start` | 2 | Browser process crash, port bind fail |
| `browser_stop` | 3 | Process still running |
| `script_run` | 1 | Timeout only |
| `cache_clear_local` | 3 | File locked |
| `proxy_test` | 2 | Connection timeout |
| `db_migration` | 0 | Never retry (fix code instead) |

### 4.4 Non-retryable Conditions

Các lỗi sau → `failed` ngay (không retry):
- Profile không tồn tại
- Profile trong recycle bin
- Max concurrent browsers reached
- Invalid job payload (validation error)
- Job đã bị canceled

---

## 5. Timeout Rules

### 5.1 Timeout Types

| Type | Mô tả |
|---|---|
| **Execution timeout** | Thời gian tối đa để job hoàn thành từ khi `running` |
| **Queue timeout** | Thời gian tối đa job có thể ở trạng thái `queued` |

### 5.2 Timeout Values

| `job_type` | Execution timeout | Queue timeout |
|---|---|---|
| `browser_start` | 30s | 300s |
| `browser_stop` | 15s | 60s |
| `script_run` | configurable (default 300s, max 3600s) | 600s |
| `cache_clear_local` | 60s | 300s |
| `proxy_test` | 15s | 60s |

### 5.3 Timeout Handling

1. Worker monitor kiểm tra `started_at` mỗi 5s
2. Nếu `now() - started_at > timeout_seconds`:
   - Cập nhật `status = 'failed'`, `error_message = 'Execution timeout'`
   - Nếu `retry_count < max_retries`: schedule retry
3. Queue timeout: scheduler check `queued` jobs mỗi 60s; expire nếu quá queue timeout

---

## 6. Idempotency

### 6.1 Client-provided Idempotency Key

Client có thể gửi header `X-Idempotency-Key: <uuid>` hoặc field `idempotencyKey` trong body.

**Behavior**:
- Nếu key chưa tồn tại → tạo job mới, lưu key vào `jobs.idempotency_key`
- Nếu key đã tồn tại → trả về job hiện tại (không tạo mới)

**Idempotency window**: 24 giờ sau khi job terminal.

### 6.2 Example

```http
POST /api/env/start
Content-Type: application/json
X-Idempotency-Key: idem-abc123

{
  "id": "env-uuid-xxx"
}
```

Response (nếu key đã tồn tại):
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "jobId": "job-uuid-existing",
    "status": "succeeded",
    "result": { "debugPort": 9222 },
    "idempotent": true
  },
  "requestId": "req-xyz"
}
```

---

## 7. Concurrency Limits

### 7.1 Global Limits

| Resource | Default Limit | Configurable? | Setting Key |
|---|---|---|---|
| Max concurrent `running` jobs | 20 | Yes | `agent.max_concurrent_jobs` |
| Max concurrent browsers | 20 | Yes | `agent.max_concurrent_browsers` |
| Max `queued` jobs | 500 | Yes | `agent.max_queue_size` |
| Max jobs per profile | 3 | Yes | `agent.max_jobs_per_profile` |

### 7.2 Per-type Concurrency

| `job_type` | Max concurrent |
|---|---|
| `browser_start` | 5 (limited by launch overhead) |
| `browser_stop` | 10 |
| `script_run` | Depends on `agent.max_concurrent_browsers` |
| `cache_clear_local` | 10 |
| `proxy_test` | 20 |

### 7.3 Queue Full Behavior

Khi queue đầy (`queued` jobs ≥ `max_queue_size`):
- API trả về HTTP 422, code `-1403` `"Job queue full"`
- Client nên poll và retry sau khi queue giảm

---

## 8. IPC / Local API → Agent Sequence

### 8.1 Sequence Diagram: Request → Enqueue → Execute → Result

```
Client          Local API          Job Queue          Worker           Browser
  │                │                   │                │                │
  │ POST /api/     │                   │                │                │
  │ env/start      │                   │                │                │
  │───────────────►│                   │                │                │
  │                │ validate request  │                │                │
  │                │ check idempotency │                │                │
  │                │                   │                │                │
  │                │ enqueue job       │                │                │
  │                │──────────────────►│                │                │
  │                │                   │                │                │
  │ {jobId, status:│                   │                │                │
  │   "queued"}    │                   │                │                │
  │◄───────────────│                   │                │                │
  │                │                   │                │                │
  │                │                   │ worker poll    │                │
  │                │                   │◄───────────────│                │
  │                │                   │                │                │
  │                │                   │ job dequeued   │                │
  │                │                   │───────────────►│                │
  │                │                   │                │                │
  │                │                   │                │ launch browser  │
  │                │                   │                │───────────────►│
  │                │                   │                │                │
  │                │                   │                │ debug port     │
  │                │                   │                │◄───────────────│
  │                │                   │                │                │
  │                │                   │                │ update job:    │
  │                │                   │                │ status=succeeded│
  │                │                   │                │ result={port}  │
  │                │                   │◄───────────────│                │
  │                │                   │                │                │
  │ GET /api/jobs/ │                   │                │                │
  │ {jobId}        │                   │                │                │
  │───────────────►│                   │                │                │
  │                │ query job status  │                │                │
  │                │──────────────────►│                │                │
  │                │                   │                │                │
  │ {status:       │                   │                │                │
  │   "succeeded", │                   │                │                │
  │   result:{...}}│                   │                │                │
  │◄───────────────│                   │                │                │
```

### 8.2 Long-polling & WebSocket (Optional)

Client có thể:
1. **Poll**: `GET /api/jobs/{jobId}` mỗi 500ms đến khi terminal
2. **WebSocket** (nếu implement): `ws://localhost:40000/ws/jobs/{jobId}` để nhận push events

---

## 9. API Endpoints

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/jobs/{jobId}` | GET | Get job status + result |
| `/api/jobs/{jobId}/cancel` | POST | Cancel job (nếu queued/running) |
| `/api/jobs/{jobId}/logs` | GET | Get job log lines |
| `/api/jobs` | GET | List recent jobs (paginated) |
| `/health` | GET | Agent health check |

---

## 10. Health Check

**Endpoint**: `GET /health`  
**Auth**: Không cần (public endpoint)

**Response (healthy)**:
```json
{
  "status": "ok",
  "agent_version": "1.0.0",
  "uptime_seconds": 3600,
  "queue": {
    "queued": 2,
    "running": 5,
    "max_concurrent": 20
  },
  "browsers": {
    "active": 5,
    "max": 20
  },
  "db": "ok",
  "timestamp": "2026-02-20T10:00:00Z"
}
```

**Response (degraded)**:
```json
{
  "status": "degraded",
  "reason": "DB connection slow",
  ...
}
```

---

## 11. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
