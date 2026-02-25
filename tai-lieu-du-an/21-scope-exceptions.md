# Scope Exceptions — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Tài liệu hóa các tính năng/endpoint được chủ động loại khỏi scope v1.0 với lý do kinh doanh và kỹ thuật rõ ràng.

---

## 1. Tổng quan

Tài liệu này liệt kê các tính năng từ MoreLogin baseline mà BrowserManager **chủ động không implement** trong v1.0, kèm theo:
- Lý do kỹ thuật/kinh doanh
- Tác động lên người dùng
- Roadmap (nếu có kế hoạch implement trong tương lai)
- Chữ ký phê duyệt từ Product Owner

### Nguyên tắc Scope Exception

1. **Tính năng cloud-only**: Không áp dụng cho self-hosted architecture
2. **Tính năng yêu cầu infrastructure phức tạp**: Không phù hợp cho local desktop app
3. **Tính năng có risk bảo mật cao**: Cần thêm thời gian audit và hardening
4. **Tính năng low-value/high-cost**: ROI không đủ cho v1.0

---

## 2. API Endpoints — Scope Exceptions

### E1: `POST /api/env/cache/cleanCloud`

**Loại**: Cloud-only endpoint  
**Trạng thái**: 🚫 **N/A** (Not Applicable)

#### Lý do

Endpoint này trong MoreLogin được thiết kế để:
- Xóa cache browser profile được lưu trên cloud storage của MoreLogin
- Đồng bộ hóa việc xóa cache giữa nhiều máy client
- Giải phóng dung lượng lưu trữ trên cloud infrastructure

BrowserManager là **self-hosted** architecture:
- Không có cloud storage backend
- Profile data lưu hoàn toàn local trên máy user
- Không có multi-device sync mechanism

#### Giải pháp thay thế

BrowserManager cung cấp endpoint tương đương cho **local cache cleaning**:
```
POST /api/env/removeLocalCache
POST /api/profiles/{id}/clear-cache
```

Các endpoint này xóa cache local của profile, bao gồm:
- Browser cache (HTTP cache)
- Cookies
- LocalStorage
- SessionStorage
- IndexedDB

#### Tác động

- **Người dùng chuyển từ MoreLogin**: Không còn khả năng "clean cloud cache" vì không có cloud
- **API clients**: Nếu gọi endpoint này sẽ nhận `501 Not Implemented` với message rõ ràng

#### Response khi gọi endpoint

```json
// HTTP 501 Not Implemented
{
  "code": -1501,
  "msg": "Cloud cache not supported in self-hosted mode",
  "data": {
    "alternative": "POST /api/env/removeLocalCache",
    "docs": "https://github.com/lizamazieva41-ai/bower/blob/main/tai-lieu-du-an/scope-exceptions.md"
  },
  "requestId": "req-abc123"
}
```

**Spec đầy đủ**: `04-local-api.md` §cleanCloud + `openapi.yaml` `/api/env/cache/cleanCloud`

#### Roadmap

- **v1.0**: ❌ Không có
- **v1.1+**: ❌ Không có kế hoạch (không áp dụng cho self-hosted)

#### Phê duyệt

- [x] **Product Owner**: Đã phê duyệt loại khỏi scope v1.0
- [x] **Technical Lead**: Xác nhận không áp dụng cho architecture self-hosted
- **Ngày phê duyệt**: 2026-02-19

---

## 3. Data Fields — Scope Exceptions

_Hiện tại không có data fields được loại khỏi scope. Tất cả fields trong Profile/Group/Tag/Proxy đều được implement đầy đủ hoặc có status Partial với roadmap rõ ràng._

---

## 4. UX Operations — Restricted Items

Các tính năng GUI được đánh dấu `[Restricted]` không phải là Scope Exception, mà là **phased rollout**:

### R1: Refresh Fingerprint

**Trạng thái**: 🔒 **Restricted — v1.3+**  
**Lý do**: Fingerprint generation engine cần thêm thời gian phát triển và testing  
**Hiển thị trong UI**: Có (disabled + tooltip "Available in v1.3+")  
**Roadmap**: v1.3 (Q3 2026)

### R2: E2E Encryption Setting

**Trạng thái**: 🔒 **Restricted — v1.2+**  
**Lý do**: E2E encryption implementation cần security audit và key management infrastructure  
**Hiển thị trong UI**: Có (disabled + tooltip "Available in v1.2+")  
**Interface spec**: Đầy đủ trong `09-bao-mat-va-luu-tru.md` §8C  
**Roadmap**: v1.2 (Q2 2026)

### R3: Operation Authorization

**Trạng thái**: 🔒 **Restricted — v1.4+**  
**Lý do**: Yêu cầu role-based access control (RBAC) system  
**Hiển thị trong UI**: Không (không có UI element cho RBAC trong v1.0)  
**Roadmap**: v1.4 (Q4 2026)

---

## 5. Security Features — Phased Implementation

### Interface vs Implementation

BrowserManager v1.0 có **đầy đủ interface** cho các security features nhưng **enforcement được phân giai đoạn**:

| Feature | Interface Spec | v1.0 Enforcement | v1.1+ Enforcement |
|---|---|---|---|
| E2E Encryption | ✅ Full (`e2e_encryption_enabled` field) | ❌ Flag-only | ✅ Actual encryption |
| Lock Status | ✅ Full (`lock_status` field) | ❌ Flag-only | ✅ Actual lock/unlock |
| Operation Auth | ⚠️ Partial | ❌ No RBAC | ✅ RBAC system |

**Lý do phân giai đoạn**:
- v1.0 cung cấp **data model & API interface** để client có thể set flags
- v1.1+ implement **actual enforcement logic** sau khi có đủ security audit
- Tránh "fake security" — nếu chưa enforce được thì document rõ ràng

Chi tiết: xem `09-bao-mat-va-luu-tru.md` §8E (Implementation Phasing).

---

## 6. Quy trình thêm Scope Exception mới

Nếu phát hiện thêm tính năng cần loại khỏi scope:

1. **Tạo Pull Request** thêm section vào file này
2. **Document đầy đủ**:
   - Lý do kỹ thuật/kinh doanh
   - Tác động lên user
   - Giải pháp thay thế (nếu có)
   - Roadmap (nếu có kế hoạch implement)
3. **Review & Approval**:
   - Technical Lead review
   - Product Owner approve
   - Merge vào main branch
4. **Update `14-parity-matrix.md`**:
   - Thay đổi status thành 🚫 N/A
   - Thêm reference tới section trong file này

---

## 7. Change Log

| Ngày | Thay đổi | Người thực hiện |
|---|---|---|
| 2026-02-19 | Tạo file, document E1 (`cleanCloud` endpoint) | Technical Team |

---

**Tài liệu liên quan**:
- [14-parity-matrix.md](14-parity-matrix.md) — Ma trận parity chi tiết
- [00-tong-quan-du-an.md](00-tong-quan-du-an.md) — Scope tổng quan
- [09-bao-mat-va-luu-tru.md](09-bao-mat-va-luu-tru.md) — Security phasing plan
