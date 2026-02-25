# Glossary — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Định nghĩa thuật ngữ thống nhất cho toàn bộ dự án.  
> **Người phê duyệt**: Tech Lead + Product Owner

---

## Mục đích

Tài liệu này là **Single Source of Truth** cho tất cả thuật ngữ kỹ thuật và nghiệp vụ trong dự án BrowserManager.  
Mọi tài liệu khác phải sử dụng thuật ngữ từ glossary này để đảm bảo nhất quán.

---

## A

### Agent
**Background Agent** — Windows Service hoặc System Tray process chạy ngầm, quản lý job queue, khởi động browser, và phục vụ Local API. Xem chi tiết: `03-background-agent.md`.

### API Token
Bearer token 256-bit dùng để xác thực mọi request tới Local API. Token được lưu dưới dạng SHA-256 hash trong DB (key `api_token_hash`). Không có thời hạn mặc định; có thể rotate thủ công.

### Audit Log
Bản ghi sự kiện bảo mật (authentication, profile operations, token rotation) lưu trong bảng `audit_logs`. Không chứa request body; chỉ chứa metadata sự kiện.

---

## B

### Bearer Token
Xem **API Token**.

### BrowserManager
Tên sản phẩm tổng thể — Windows Desktop Cloud Browser bao gồm Background Agent, Local API, CLI (`bm`), và Desktop GUI.

---

## C

### CLI
Command-line interface của BrowserManager. Tên lệnh: `bm`. Ví dụ: `bm profile list`, `bm agent start`. Xem đặc tả đầy đủ: `05-cli-spec.md`.

### Compat Endpoints
30 endpoints mô phỏng MoreLogin public API (`/api/env/*`, `/api/envgroup/*`, `/api/envtag/*`, `/api/proxyInfo/*`). Cho phép client MoreLogin chạy không cần sửa code. Xem: `12-api-compatibility.md`, `13-baseline-morelogin-public.md`.

### Compat Envelope
Format response chuẩn `{code, msg, data, requestId}` dùng cho tất cả endpoints. Xem SSOT: `error-catalog.md` §1.1.

### correlationId
Xem **requestId**.

---

## D

### Data Directory (`data_dir`)
Thư mục lưu trữ dữ liệu browser profile (cookies, localStorage, cache, ...). Mỗi profile có một `data_dir` riêng biệt để đảm bảo isolation. Đường dẫn tuyệt đối, duy nhất, không đổi sau khi tạo.

### DPAPI
Windows Data Protection API — cơ chế mã hoá dữ liệu nhạy cảm (proxy passwords, CLI config token) sử dụng Windows user credentials làm key. Mất khi roaming profile hoặc đổi user.

---

## E

### Envelope
Xem **Compat Envelope**.

### Env
Viết tắt của **Environment** = **Profile** trong ngữ cảnh MoreLogin compat API. Prefix `/api/env/` đến từ MoreLogin. Trong native API, dùng `profile`.

### envId
UUID v4 dùng làm public identifier cho browser profile trong compat API. Ổn định, không thay đổi sau khi tạo. Tương đương `env_id` trong bảng `profiles`.

### Error Code
Số nguyên âm (< 0) trong field `code` của compat envelope, chỉ định loại lỗi. `0` = success. Xem catalog đầy đủ: `error-catalog.md`.

---

## G

### Gate
Điều kiện nghiệm thu (G0–G6) xác định khi nào documentation hoặc implementation đạt chuẩn để triển khai. Xem: `gates-and-dod.md`.

### Golden Response
File JSON mẫu trong `golden-responses/` directory, biểu diễn response hợp lệ của một endpoint. Dùng trong contract tests để validate cấu trúc response.

### Group
Nhóm quản lý browser profiles (`env_groups` table). Mỗi profile thuộc về tối đa 1 group. Xem: `02-he-thong-profile.md`.

---

## H

### Health Check
Endpoint `GET /health` (không yêu cầu auth) trả về trạng thái agent. Response: `{status: "healthy"|"degraded"|"unhealthy", version, uptime_seconds, ...}`.

---

## I

### idempotencyKey
Header `X-Idempotency-Key` dùng để tránh duplicate jobs khi client retry. Agent nhận key đã xử lý → trả lại kết quả cũ thay vì tạo job mới.

### In-Scope
Tính năng được cam kết trong v1.0. Xem danh sách đầy đủ: `scope.md` §2.

---

## J

### Job
Đơn vị công việc bất đồng bộ trong Background Agent (start browser, run script, clear cache,...). Mỗi job có states: `queued → running → succeeded|failed|canceled`. Xem: `job-spec.md`.

### jobId
UUID duy nhất định danh một job. Client dùng để poll status hoặc cancel.

---

## L

### Local API
HTTP server chạy tại `127.0.0.1:40000`, phục vụ cả compat endpoints và native endpoints. Chỉ lắng nghe localhost; không expose ra mạng.

### lastUsedAt
Timestamp ghi nhận lần cuối user mở profile (tương đương `last_opened_at` trong DB). Cập nhật khi: `POST /api/env/start` hoặc `POST /api/env/reopen` thành công.

---

## M

### Migration
Script SQL cập nhật schema DB theo thứ tự version (001, 002,...). Chạy tự động khi agent khởi động. Xem: `migration-plan.md`.

### MoreLogin
Sản phẩm anti-detect browser của MoreLogin Inc. BrowserManager tương thích với MoreLogin public API để client có thể chuyển đổi không cần sửa code.

---

## N

### Native API
Endpoints nội bộ của BrowserManager (`/api/profiles/*`, `/api/jobs/*`, ...) — thiết kế riêng, không phải MoreLogin compat. Cũng sử dụng compat envelope `{code, msg, data, requestId}`.

### N/A (Not Applicable)
Trạng thái trong parity matrix chỉ endpoint/feature không áp dụng cho BrowserManager (thường là cloud-only). Mỗi N/A phải có entry trong `scope-exceptions.md`.

---

## O

### Out-of-Scope
Tính năng không được implement trong v1.0. Xem: `scope.md` §3.

---

## P

### Parity
Mức độ tương đương giữa BrowserManager và MoreLogin. Đo bằng: G2 (API parity), G3 (UX parity), G4 (Data model parity). Xem: `14-parity-matrix.md`.

### Profile
Browser profile — đơn vị quản lý độc lập bao gồm cấu hình browser, proxy, extensions, và data directory. Lưu trong bảng `profiles`. Đồng nghĩa với "Env" trong compat API.

### profileCount
Số lượng profiles thuộc một group. Computed field trong API response — tính bằng `COUNT(*)` từ bảng `profiles` với điều kiện `group_id = ?` và `deleted_at IS NULL`.

### Port
Default port của Local API: `40000`. Alt port khi conflict: `19000` (chỉ dùng làm ví dụ override, không phải default). Config key: `api.port`.

---

## R

### Rate Limit
Giới hạn tần suất request tới Local API: mặc định **100 req/s** global. Config key: `api.rate_limit_rps`. Vượt giới hạn → HTTP 429, code `-1505`.

### Recycle Bin
Trạng thái soft-delete cho profiles. Profile bị xóa mềm (`deleted_at IS NOT NULL`) vẫn tồn tại trong DB, có thể restore. Tự động xóa vĩnh viễn sau 30 ngày.

### requestId
UUID gắn với mỗi HTTP request/response, dùng để trace log. Client có thể cung cấp qua header `X-Request-ID`; nếu không có, agent tự sinh. Xuất hiện trong field `requestId` của compat envelope.

### Restricted
Trạng thái trong parity matrix chỉ feature có spec đầy đủ nhưng enforcement bị trì hoãn sang version sau (phased rollout). Khác với N/A: Restricted feature sẽ được implement.

---

## S

### Scope Exception
Entry trong `scope-exceptions.md` document hóa lý do kỹ thuật/kinh doanh, tác động, và roadmap cho một tính năng bị loại khỏi scope v1.0.

### Session
Một phiên chạy browser profile (từ khi `start` đến khi `close`). Không lưu trong DB riêng; tracked qua `status` field của profile và job logs.

### SHA-256
Hash function dùng để lưu API token trong DB (`api_token_hash`). Agent chỉ lưu hash, không lưu plain token. Khi verify: hash request token → so sánh với stored hash.

### SSOT (Single Source of Truth)
Nguyên tắc thiết kế tài liệu: mỗi thông tin chỉ tồn tại ở một nơi duy nhất. Ví dụ: `error-catalog.md` là SSOT cho error codes; `openapi.yaml` là SSOT cho API schema.

---

## T

### Tag
Label gắn vào profiles để phân loại/lọc (`env_tags` table, quan hệ N:N qua `profile_tags`). Xem: `02-he-thong-profile.md`.

### Token
Xem **API Token**.

### Token Rotation
Thao tác vô hiệu hóa token hiện tại và tạo token mới. Endpoint: `POST /api/agent/token/rotate`. CLI: `bm agent token rotate`. Token cũ bị invalidate ngay lập tức.

---

## U

### UUID
Universally Unique Identifier (v4) — format `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`. Dùng cho `envId`, `jobId`, `requestId`.

---

## V

### Validation Error
Lỗi do client gửi request không hợp lệ theo schema (missing required field, wrong type, out-of-range value,...). HTTP 400, codes `-1601` — `-1607`. Xem: `error-catalog.md` §9.

---

## W

### Worker
Thread/process trong Background Agent thực thi jobs từ queue. Số worker tối đa = `agent.max_concurrent_browsers` (default: 20).

---

## Tài liệu liên quan

| File | Vai trò |
|---|---|
| `error-catalog.md` | SSOT cho tất cả error codes |
| `scope.md` | SSOT cho phạm vi dự án v1.0 |
| `scope-exceptions.md` | Governance cho N/A và Restricted items |
| `openapi.yaml` | SSOT cho API schema |
| `14-parity-matrix.md` | Parity scores G2/G3/G4 |

---

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới — định nghĩa các thuật ngữ cốt lõi |
