# Runbook — BrowserManager v1.0

> **Phiên bản**: 1.0 | **Ngày**: 2026-02-20 | **Trạng thái**: Approved  
> **Mục đích**: Hướng dẫn xử lý sự cố: "Nếu lỗi X → làm gì"  
> **Người phê duyệt**: Ops Lead + Tech Lead

---

## 1. Tổng quan

Runbook này liệt kê các sự cố phổ biến và các bước xử lý cụ thể.  
**Nguyên tắc**: Mỗi bước có lệnh cụ thể có thể copy-paste và chạy ngay.

---

## 2. Sự cố: Agent không khởi động

### Triệu chứng
- CLI trả về lỗi `"Agent not running"` hoặc `-1404`
- GUI hiển thị banner "Cannot connect to agent"
- `GET http://localhost:40000/health` trả về connection refused

### Chẩn đoán

```powershell
# 1. Kiểm tra service status
Get-Service -Name "BrowserManagerAgent"

# 2. Kiểm tra event log
Get-EventLog -LogName Application -Source "BrowserManager" -Newest 20

# 3. Kiểm tra agent log file
Get-Content "$env:LOCALAPPDATA\BrowserManager\logs\agent.log" -Tail 50

# 4. Kiểm tra port
netstat -ano | findstr ":40000"
```

### Xử lý

```powershell
# Option A: Restart service
Restart-Service -Name "BrowserManagerAgent"

# Option B: Start service nếu stopped
Start-Service -Name "BrowserManagerAgent"

# Option C: Nếu service không tồn tại (re-register)
bm agent install
bm agent start

# Option D: Chạy trực tiếp để xem error
& "$env:LOCALAPPDATA\BrowserManager\agent.exe" --console
```

### Root causes thường gặp

| Nguyên nhân | Triệu chứng trong log | Cách fix |
|---|---|---|
| Port 40000 bị chiếm | `Address already in use` | Đổi port: `bm config set api.port 40001` |
| DB migration failed | `Migration failed: ...` | Xem §5 (DB Issues) |
| DPAPI decrypt failed | `Unprotect failed` | User profile thay đổi; xem §9 |
| Insufficient permissions | `Access denied` | Chạy với user account đúng |

---

## 3. Sự cố: API trả về 401 Unauthorized

### Triệu chứng
- Tất cả API calls trả về HTTP 401, `code: -1501` hoặc `-1502`

### Chẩn đoán

```powershell
# Xem token hiện tại (masked)
bm agent status

# Test với token đúng
$token = bm agent token get
curl -H "Authorization: Bearer $token" http://localhost:40000/health
```

### Xử lý

```powershell
# Rotate token (tạo token mới)
bm agent token rotate

# Lấy token mới để dùng
$newToken = bm agent token get
Write-Host "New token: $newToken"
```

---

## 4. Sự cố: Browser không mở (Profile start fail)

### Triệu chứng
- `POST /api/env/start` trả về `-1006` `"Browser launch failed"`
- Browser window không xuất hiện

### Chẩn đoán

```powershell
# 1. Kiểm tra job logs
$jobId = "<job-id-từ-response>"
curl -H "Authorization: Bearer $token" "http://localhost:40000/api/jobs/$jobId/logs"

# 2. Kiểm tra số browsers đang mở
curl -H "Authorization: Bearer $token" http://localhost:40000/health
# Xem browsers.active vs browsers.max

# 3. Kiểm tra data_dir
$envId = "<env-id>"
$dataDir = "$env:LOCALAPPDATA\BrowserManager\profiles\$envId"
Test-Path $dataDir
```

### Xử lý

```powershell
# Case: Max concurrent reached (20 browsers)
# Close một số browsers trước
curl -X POST -H "Authorization: Bearer $token" `
     -H "Content-Type: application/json" `
     -d '{"id": "<running_env_id>"}' `
     http://localhost:40000/api/env/close

# Case: Data dir bị corrupt
# Xóa và recreate data dir
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\BrowserManager\profiles\$envId"
# Agent sẽ tạo lại khi start

# Case: Chromium process còn lại từ crash trước
Get-Process -Name "chrome", "chromium" | Stop-Process -Force
```

---

## 5. Sự cố: Database Issues

### 5a. DB Migration Failed

### Triệu chứng
- Agent không start, log: `"Migration failed: ..."`, code `-1705`

### Chẩn đoán

```powershell
# Xem chi tiết migration error
Get-Content "$env:LOCALAPPDATA\BrowserManager\logs\agent.log" | Select-String "Migration"

# Kiểm tra DB file
$dbPath = "$env:LOCALAPPDATA\BrowserManager\browsermanager.db"
Test-Path $dbPath
(Get-Item $dbPath).Length
```

### Xử lý

```powershell
# Option A: Backup và retry
Copy-Item $dbPath "$dbPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
Start-Service "BrowserManagerAgent"

# Option B: Nếu DB corrupt (mất data hoặc fresh start OK)
Stop-Service "BrowserManagerAgent"
Move-Item $dbPath "$dbPath.corrupt"
Start-Service "BrowserManagerAgent"
# Agent sẽ tạo DB mới, nhưng mất tất cả data
```

### 5b. DB Locked / SQLite Busy

### Triệu chứng
- API calls chậm hoặc timeout; log: `"database is locked"`

### Xử lý

```powershell
# Restart agent (releases DB lock)
Restart-Service "BrowserManagerAgent"

# Kiểm tra không có process nào khác mở DB
# (SQLite không hỗ trợ multiple writers)
```

---

## 6. Sự cố: Disk đầy

### Triệu chứng
- API trả về `-1704` `"Insufficient storage"`
- Browser fail to launch
- Log: `"No space left on device"` hoặc `"not enough space"`

### Chẩn đoán

```powershell
# Kiểm tra disk usage
Get-PSDrive C | Select-Object Used, Free

# Kiểm tra thư mục profiles
$profilesDir = "$env:LOCALAPPDATA\BrowserManager\profiles"
Get-ChildItem $profilesDir | 
    ForEach-Object { 
        [PSCustomObject]@{
            Name = $_.Name
            SizeMB = [math]::Round((Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        }
    } | Sort-Object SizeMB -Descending | Format-Table
```

### Xử lý

```powershell
# 1. Xóa browser cache của profiles (giữ data)
curl -X POST -H "Authorization: Bearer $token" `
     -H "Content-Type: application/json" `
     -d '{"ids": ["<env_id>"]}' `
     http://localhost:40000/api/env/removeLocalCache

# 2. Empty recycle bin (permanent delete all)
bm profiles trash clear

# 3. Xóa old job logs
bm maintenance clean-logs --older-than 7days

# 4. Kiểm tra downloads trong profile data dirs
# Xóa thủ công downloads lớn trong %LOCALAPPDATA%\BrowserManager\profiles\*\Default\Downloads\
```

---

## 7. Sự cố: Rate Limit / 429 Too Many Requests

### Triệu chứng
- API trả về HTTP 429, `code: -1505`
- Header `Retry-After: 1`

### Xử lý

```powershell
# Kiểm tra rate limit config
bm config get api.rate_limit_rps

# Tăng rate limit nếu client hợp lệ
bm config set api.rate_limit_rps 100
Restart-Service "BrowserManagerAgent"
```

---

## 8. Sự cố: Jobs bị stuck (running quá lâu)

### Triệu chứng
- Job ở trạng thái `running` quá thời gian timeout
- Agent health cho thấy `queue.running` không giảm

### Chẩn đoán

```powershell
# List running jobs
curl -H "Authorization: Bearer $token" "http://localhost:40000/api/jobs?status=running"

# Xem logs của job cụ thể
curl -H "Authorization: Bearer $token" "http://localhost:40000/api/jobs/<jobId>/logs"
```

### Xử lý

```powershell
# Cancel stuck job
curl -X POST -H "Authorization: Bearer $token" `
     http://localhost:40000/api/jobs/<jobId>/cancel

# Nếu không cancel được: restart agent
Restart-Service "BrowserManagerAgent"
# Stuck jobs sẽ được set failed trên startup
```

---

## 9. Sự cố: DPAPI Decryption Failed

### Triệu chứng
- Agent log: `"DPAPI Unprotect failed"` hoặc `"CryptographicException"`
- Agent không start

### Nguyên nhân
- User profile thay đổi (password reset bởi admin)
- Profile được copy sang machine khác
- Môi trường domain thay đổi

### Xử lý

```powershell
# Xóa encrypted settings (sẽ mất token và proxy passwords)
$settingsPath = "$env:LOCALAPPDATA\BrowserManager\settings.enc"
Remove-Item $settingsPath

# Restart agent (sẽ tạo token mới)
Start-Service "BrowserManagerAgent"

# Lấy token mới
bm agent token get
```

**Lưu ý**: Proxy passwords trong DB cũng sẽ không decrypt được.  
Cần update lại proxy credentials qua API.

---

## 10. Sự cố: Upgrade Failed / Rollback

### Triệu chứng
- Sau upgrade, agent không start hoặc API lỗi

### Rollback

```powershell
# 1. Stop agent
Stop-Service "BrowserManagerAgent"

# 2. Backup current DB
Copy-Item "$env:LOCALAPPDATA\BrowserManager\browsermanager.db" `
          "$env:LOCALAPPDATA\BrowserManager\browsermanager.db.backup"

# 3. Uninstall current version
# Qua Control Panel hoặc:
msiexec /x {PRODUCT-GUID} /quiet

# 4. Install previous version
# Chạy installer cũ
msiexec /i BrowserManager-v1.0.0.msi /quiet

# 5. Start agent
Start-Service "BrowserManagerAgent"
```

---

## 11. Sự cố: Security Incident (Token Leak)

### Nếu nghi ngờ token bị lộ

```powershell
# 1. Rotate token NGAY LẬP TỨC
bm agent token rotate

# 2. Xem audit logs để check unauthorized access
curl -H "Authorization: Bearer $newToken" `
     "http://localhost:40000/api/audit-logs?event_type=auth_success&from=<timestamp>"

# 3. Xem nếu có abnormal API calls
curl -H "Authorization: Bearer $newToken" `
     "http://localhost:40000/api/audit-logs?from=<timestamp>"

# 4. Nếu có unauthorized access: 
#    - Stop agent
#    - Kiểm tra tất cả running browsers (có thể bị điều khiển)
#    - Revoke tất cả browser sessions
Stop-Service "BrowserManagerAgent"
# Đóng tất cả browser instances
Get-Process -Name "chrome","chromium","msedge","firefox" | Stop-Process -Force
Start-Service "BrowserManagerAgent"
```

---

## 12. Diagnostics Reference

### Log Locations

| Log | Path |
|---|---|
| Agent log | `%LOCALAPPDATA%\BrowserManager\logs\agent.log` |
| Installer log | `%TEMP%\BrowserManager-install.log` |
| Audit log | DB table `audit_logs` |
| Job log | DB table `job_logs` |

### Useful Commands

```powershell
# Agent status
bm agent status

# Full diagnostic report
bm diagnose --output diagnostic-report.txt

# Check all service dependencies
Get-Service -Name "BrowserManagerAgent" -DependentServices

# View Windows Event Log
Get-EventLog -LogName Application -Source "BrowserManager" -Newest 50 | Format-List
```

### API Health Check

```powershell
$token = bm agent token get
$response = Invoke-RestMethod -Uri "http://localhost:40000/health" `
            -Headers @{Authorization="Bearer $token"}
$response | ConvertTo-Json
```

---

## 13. Escalation

Nếu không giải quyết được sau 30 phút:

1. Chạy `bm diagnose --output report.txt`
2. Attach `report.txt` và `agent.log` vào ticket
3. Escalate đến Tech Lead kèm theo:
   - Triệu chứng mô tả
   - Bước đã thử
   - Log files

---

## 14. Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-02-20 | Tạo mới |
