# 1. Cài dependencies

## Tạo file .env (root project)
GEMINI_API_KEY=your_key_here
VITE_API_BASE_URL=http://your-server-domain:12008/api/v1

## Chạy Dev bằng Docker (khuyên dùng)

Không cần cài uv/Python/Node trên máy local.

### Lần đầu

```bash
docker compose -f docker-compose.dev.yml up --build
```

Nếu mạng tới PyPI chập chờn (timeout khi `uv sync`), có thể build với timeout/retry cao hơn:

```bash
docker compose -f docker-compose.dev.yml build \
	--build-arg UV_HTTP_TIMEOUT=300 \
	--build-arg UV_HTTP_CONNECT_TIMEOUT=60 \
	--build-arg UV_HTTP_RETRIES=12

docker compose -f docker-compose.dev.yml up
```

Nếu vẫn timeout do route tới `pypi.org`, có thể thử mirror:

```bash
docker compose -f docker-compose.dev.yml build \
	--build-arg UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
```

### Từ lần sau

```bash
docker compose -f docker-compose.dev.yml up
```

### URL khi chạy dev

- Frontend (Vite HMR): http://localhost:5173
- Backend API: http://localhost:12008
- API Docs: http://localhost:12008/docs

### Lệnh thường dùng cho dev

```bash
# Xem log
docker compose -f docker-compose.dev.yml logs -f

# Vào container dev
docker compose -f docker-compose.dev.yml exec slidegen-dev bash

# Dừng môi trường dev
docker compose -f docker-compose.dev.yml down
```


## Chạy Backend (Terminal 1)
uv run backend/main.py
→ Backend: http://localhost:12008

## Chạy Frontend (Terminal 2)
cd frontend
npm run dev
→ Frontend: http://localhost:5173

## Chạy trên Server

Script `scripts/run_server.sh` build frontend và khởi động toàn bộ service trong 1 lệnh:

```bash
./scripts/run_server.sh
```

Script sẽ tự động:
- Build frontend dist (Node 22)
- Khởi động backend tại `http://0.0.0.0:12008`
- Serve cả frontend lẫn API từ cùng 1 port

**Cấu hình API URL** (thêm vào `.env` ở root, script sẽ đọc khi build):

```
VITE_API_BASE_URL=http://your-server-domain:12008/api/v1
```

Nếu không set, mặc định dùng `http://aicontest.ptit.edu.vn:12008/api/v1`.

### Kiểm tra nhanh sau khi chạy

```bash
curl -I http://127.0.0.1:12008/docs
```

## Quản lý Subscription Codes

DB file: `backend/infrastructure/database/slidegen.db`
Dùng [DB Browser for SQLite](https://sqlitebrowser.org/) hoặc chạy SQL trực tiếp.

### Các loại code

| `code_type`  | `max_uses` | Hành vi |
|--------------|------------|---------|
| `unlimited`  | bất kỳ     | Dùng bao nhiêu lần cũng được, cùng 1 account cũng gia hạn lại được |
| `limited`    | `1`        | Chỉ 1 tài khoản dùng được 1 lần |
| `limited`    | `N`        | Tối đa N tài khoản dùng được, mỗi account 1 lần |

### Code mặc định (có sẵn trong DB)

| Code | Tier | Loại | Thời hạn |
|------|------|------|----------|
| `SLIDEGENIUS` | Ultra | unlimited | 30 ngày/lần nhập |

### Ví dụ tạo code

```bash
# Unlimited (dùng bao nhiêu lần cũng được)
sqlite3 backend/infrastructure/database/slidegen.db "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type) VALUES ('PROMO2025', 'plus', 30, -1, 'unlimited');"

# Chỉ 1 tài khoản dùng được
sqlite3 backend/infrastructure/database/slidegen.db "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type) VALUES ('VIP-ABCD', 'ultra', 30, 1, 'limited');"

# Tối đa 50 tài khoản
sqlite3 backend/infrastructure/database/slidegen.db "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type) VALUES ('LAUNCH50', 'plus', 30, 50, 'limited');"
```

### Tắt/kích hoạt code

```bash
# Tắt code
sqlite3 backend/infrastructure/database/slidegen.db "UPDATE subscription_codes SET is_active = 0 WHERE code = 'PROMO2025';"

# Bật lại
sqlite3 backend/infrastructure/database/slidegen.db "UPDATE subscription_codes SET is_active = 1 WHERE code = 'PROMO2025';"
```
