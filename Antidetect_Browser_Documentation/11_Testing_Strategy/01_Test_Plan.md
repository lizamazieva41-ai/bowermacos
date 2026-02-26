# 1. CHIẾN LƯỢC KIỂM THỬ - PHIÊN BẢN MỞ RỘNG

## Test Types

### Unit Testing
- Browser Module tests
- Fingerprint Module tests
- Proxy Module tests
- Session Manager tests

### Integration Testing
- CLI Integration
- API Integration
- Browser Integration

### System Testing
- End-to-End workflow
- Performance testing
- Stress testing

---

## Test Cases - Profile Management

| TC ID | Mô tả | Expected Result | Priority |
|-------|-------|----------------|----------|
| TC_PM_01 | Tạo profile mới | Profile được tạo, trả về ID | P0 |
| TC_PM_02 | Cập nhật profile | Thông tin cập nhật đúng | P0 |
| TC_PM_03 | Xóa profile | Xóa khỏi DB | P0 |
| TC_PM_04 | Liệt kê profiles | Danh sách đầy đủ | P0 |
| TC_PM_05 | Clone profile | Profile mới được tạo với config tương tự | P1 |
| TC_PM_06 | Import profile | Profile được import từ file | P1 |
| TC_PM_07 | Export profile | File config được export | P1 |

---

## Test Cases - Browser Operations

| TC ID | Mô tả | Expected Result | Priority |
|-------|-------|----------------|----------|
| TC_BO_01 | Khởi động headless browser | Browser không có GUI | P0 |
| TC_BO_02 | Navigate to URL | Page load thành công | P0 |
| TC_BO_03 | Click element | Element được click | P0 |
| TC_BO_04 | Type text | Text được nhập vào input | P0 |
| TC_BO_05 | Take screenshot | Ảnh chụp được lưu | P0 |
| TC_BO_06 | Execute JavaScript | JS được thực thi | P0 |
| TC_BO_07 | Get page source | HTML được trả về | P1 |

---

## Test Cases - Anti-Detection (STEALTH)

| TC ID | Mô tả | Expected Result | Priority |
|-------|-------|----------------|----------|
| TC_ST_01 | navigator.webdriver check | Trả về `undefined` hoặc `false` | P0 |
| TC_ST_02 | WebGL vendor check | Giá trị fake (Google Inc.) | P0 |
| TC_ST_03 | Canvas fingerprint | Hash khác nhau mỗi lần | P0 |
| TC_ST_04 | WebRTC leak test | IP thật không bị lộ | P0 |
| TC_ST_05 | Timezone check | Timezone khớp với proxy | P1 |
| TC_ST_06 | User-Agent check | UA khớp với cấu hình | P0 |
| TC_ST_07 | Language check | Language header đúng | P1 |

---

## Test Cases - Proxy

| TC ID | Mô tả | Expected Result | Priority |
|-------|-------|----------------|----------|
| TC_PR_01 | Connect HTTP proxy | Kết nối thành công | P0 |
| TC_PR_02 | Connect SOCKS5 proxy | Kết nối thành công | P0 |
| TC_PR_03 | Proxy with auth | Xác thực thành công | P0 |
| TC_PR_04 | DNS leak test | DNS không bị leak | P0 |
| TC_PR_05 | WebRTC IP leak test | IP không bị lộ qua WebRTC | P0 |
| TC_PR_06 | Invalid proxy | Báo lỗi phù hợp | P1 |

---

## Test Cases - API Endpoints

| TC ID | Mô tả | Expected Result | Priority |
|-------|-------|----------------|----------|
| TC_API_01 | POST /api/sessions/start | Trả về session_id, debug_port | P0 |
| TC_API_02 | POST /api/sessions/stop | Session được stop | P0 |
| TC_API_03 | GET /api/sessions/{id} | Trả về session info | P0 |
| TC_API_04 | GET /api/profiles | Trả về danh sách profiles | P0 |
| TC_API_05 | POST /api/profiles | Tạo profile mới | P0 |
| TC_API_06 | Without token | Trả về 401 Unauthorized | P0 |
| TC_API_07 | Invalid token | Trả về 401 Unauthorized | P0 |

---

## Stress Tests

### Concurrency Test
| TC ID | Mô tả | Criteria |
|-------|-------|----------|
| TC_STR_01 | Khởi 20 sessions đồng thời | Tất cả thành công, RAM < 4GB |
| TC_STR_02 | Khởi 50 sessions đồng thời | Tối đa 25 chạy, rest queued |
| TC_STR_03 | 1000 API requests | Throughput > 100 req/s |

### Performance Test
| TC ID | Mô tả | Criteria |
|-------|-------|----------|
| TC_PERF_01 | Session start time | < 5 giây |
| TC_PERF_02 | API response time | < 200ms |
| TC_PERF_03 | Memory per profile | < 200MB |

---

## Security Tests

| TC ID | Mô tả | Expected Result |
|-------|-------|----------------|
| TC_SEC_01 | Brute force login | Account lock sau 5 lần thất bại |
| TC_SEC_02 | Rate limiting | Trả về 429 sau limit |
| TC_SEC_03 | SQL injection | Input được sanitize |
| TC_SEC_04 | XSS prevention | Script không thể inject |

---

## Test Environment

### Hardware
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Disk | 50 GB | 100 GB SSD |

### Software
| Software | Version |
|----------|---------|
| Python | 3.10+ |
| Playwright | 1.40+ |
| Chrome | Latest |

---

*Document ID: ABB-V2-DOC-1101 v2*
