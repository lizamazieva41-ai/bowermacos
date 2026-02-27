# Khắc phục lỗi ModuleNotFoundError: No module named 'slowapi'

## 1. Đã thực hiện tự động

- **Cài slowapi vào thư mục dự phòng:** Đã chạy `pip install --target=.venv_lib slowapi==0.1.9` và cài thành công vào `.venv_lib` (vì ghi vào `venv/` bị lỗi quyền).
- **Thư mục `.venv_lib`** đã được thêm vào `.gitignore` để không commit lên repo.

## 2. Cách chạy app ngay bây giờ

Chạy với biến môi trường `PYTHONPATH` trỏ tới `.venv_lib`:

```bash
cd /Users/hello/Desktop/bower-macos
source venv/bin/activate
export PYTHONPATH="$(pwd)/.venv_lib"
python main.py
```

Hoặc dùng script (sau khi `chmod +x run_local.sh`):

```bash
./run_local.sh
```

Nếu báo **Address already in use**: tắt process đang chiếm port 8000 (ví dụ process cũ của `python main.py`) rồi chạy lại:

```bash
lsof -ti:8000 | xargs kill -9
python main.py   # với PYTHONPATH đã set như trên
```

## 3. Sửa import trùng trong routes.py (tùy chọn)

Trong `src/api/routes.py` hiện có import trùng (dòng 25–29). Có thể gộp thành một khối:

**Trước:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
```

**Sau:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
```

## 4. Khắc phục triệt để quyền venv (khuyến nghị)

Để cài đặt đúng vào `venv` và không phải dùng `.venv_lib`:

1. Sửa quyền sở hữu thư mục venv (chạy trong terminal của bạn):

   ```bash
   sudo chown -R $(whoami) /Users/hello/Desktop/bower-macos/venv
   ```

2. Cài lại dependencies:

   ```bash
   cd /Users/hello/Desktop/bower-macos
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Sau đó có thể chạy bình thường, không cần `PYTHONPATH` hay `run_local.sh`:

   ```bash
   python main.py
   ```

Nếu không dùng `sudo`, có thể tạo venv mới:

```bash
cd /Users/hello/Desktop/bower-macos
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
# Đổi tên: rm -rf venv && mv venv_new venv
python main.py
```
