# Health Check Script

> **Version**: 1.0.0 | **Yêu cầu**: Node.js ≥18, Playwright (@playwright/test), agent đang chạy

## Mục đích

Script này kiểm tra nhanh **7 điểm** để xác định agent hoạt động đúng và sẵn sàng cho testing:

| # | Check | Kết quả mong đợi |
|---|---|---|
| 1 | Agent health | `GET /health` → 200, status `healthy` |
| 2 | Auth token | `GET /api/agent/status` với token → 200 |
| 3 | Auth rejection | Request không có token → 401 |
| 4 | Create profile | `POST /api/profiles` → 201 |
| 5 | Launch session | `POST /api/sessions/start` → 200, có debug_port |
| 6 | CDP connect | Playwright attach qua `debug_port` → thành công |
| 7 | Stop session | `POST /api/sessions/{id}/stop` → 200, cleanup |

## Cài đặt

```powershell
cd scripts/health-check
npm install
```

## Sử dụng

```powershell
# Chạy với PowerShell wrapper (khuyến nghị)
.\run.ps1

# Hoặc chạy trực tiếp
node health-check.js

# Với tùy chọn
node health-check.js --port 40000 --token "your-api-token"

# Chỉ test connectivity (không tạo profile thật)
node health-check.js --quick
```

## Tham số

| Flag | Default | Mô tả |
|---|---|---|
| `--port` | `40000` | Port của agent |
| `--token` | (từ env `BM_TOKEN`) | API token |
| `--quick` | false | Chỉ test health + auth, bỏ qua CDP |
| `--json` | false | Output định dạng JSON |
| `--timeout` | `30000` | Timeout ms cho mỗi bước |

## Output mẫu

```
BrowserManager Health Check v1.0.0
Agent URL: http://127.0.0.1:40000
─────────────────────────────────────────
[1/7] Agent health ......... ✅ PASS (12ms)
[2/7] Auth token ........... ✅ PASS (8ms)
[3/7] Auth rejection ....... ✅ PASS (5ms)
[4/7] Create test profile .. ✅ PASS (45ms)
[5/7] Launch session ....... ✅ PASS (3420ms)
[6/7] CDP connect .......... ✅ PASS (210ms)
[7/7] Stop session ......... ✅ PASS (180ms)
─────────────────────────────────────────
Result: 7/7 PASSED ✅
Duration: 3.88s
```

## Môi trường

Biến môi trường:

```
BM_PORT=40000        # Port agent (override --port)
BM_TOKEN=xxxxx       # API token (bắt buộc nếu không dùng --token)
BM_TIMEOUT=30000     # Timeout ms
```

## Exit codes

| Code | Nghĩa |
|---|---|
| `0` | Tất cả checks pass |
| `1` | Một hoặc nhiều checks fail |
| `2` | Agent không reachable |
| `3` | Token không hợp lệ |
