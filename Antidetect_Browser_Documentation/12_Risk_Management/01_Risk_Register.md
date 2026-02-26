# 1. QUẢN LÝ RỦI RO - PHIÊN BẢN MỞ RỘNG

## Risk Register

| ID | Rủi ro | Xác suất | Tác động | Mitigation |
|----|--------|----------|----------|------------|
| R001 | Bot detection (headless) | Cao | Cao | playwright-stealth, selenium-stealth |
| R002 | IP leak (WebRTC) | Trung bình | Cao | Disable WebRTC via flags |
| R003 | DNS leak | Trung bình | Trung bình | Proxy DNS config |
| R004 | Browser crash | Trung bình | Trung bình | Process monitoring |
| R005 | RAM/CPU overload | Trung bình | Cao | Resource limits |
| R006 | API latency | Trung bình | Trung bình | Async design |
| R007 | Scope creep | Cao | Trung bình | Change management |
| R008 | Navigator.webdriver = true | Cao | Cao | addInitScript override |
| R009 | Canvas fingerprint leak | Cao | Cao | Canvas noise injection |
| R010 | WebGL fingerprint | Trung bình | Cao | WebGL spoofing |
| R011 | Token auth weak | Trung bình | Cao | JWT + expiry |
| R012 | Rate limit exceeded | Trung bình | Trung bình | Rate limiter middleware |

## Risk Matrix
```
         Tác động
         L    M    H
Xác   L   -    -    -
suất  M   -   R003  R002,R005,R010
      H   -   R007  R001,R006,R008,R009,R011
```

---

## Security Hardening Checklist

- [ ] TLS/SSL for Local API
- [ ] JWT token with expiry
- [ ] Rate limiting (e.g., 100 req/min)
- [ ] Audit logging
- [ ] DPAPI encryption for secrets
- [ ] CORS configuration

---

## Priority Actions

### 1. Anti-Detection (Week 1-2)
- Implement navigator.webdriver override
- Add WebGL spoofing
- Add Canvas noise
- Add WebRTC disable flags

### 2. Testing (Week 2-3)
- Unit tests
- Integration tests
- Stress tests

### 3. Security (Week 3-4)
- TLS setup
- Rate limiting
- Audit logging

---

*Document ID: ABB-V2-DOC-1201 v2*
