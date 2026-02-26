# 1. QUẢN LÝ RỦI RO

## Risk Register

| ID | Rủi ro | Xác suất | Tác động | Mitigation |
|----|--------|----------|----------|------------|
| R001 | Bot detection (headless) | Cao | Cao | playwright-stealth, selenium-stealth |
| R002 | IP leak (WebRTC) | Trung bình | Cao | Disable WebRTC |
| R003 | DNS leak | Trung bình | Trung bình | Proxy DNS config |
| R004 | Browser crash | Trung bình | Trung bình | Process monitoring |
| R005 | RAM/CPU overload | Trung bình | Cao | Resource limits |
| R006 | API latency | Trung bình | Trung bình | Async design |
| R007 | Scope creep | Cao | Trung bình | Change management |

## Risk Matrix
```
         Tác động
         L    M    H
Xác   L   -    -    -
suất  M   -   R003  R002,R005
      H   -   R007  R001,R006
```

*Document ID: ABB-V2-DOC-1201*
