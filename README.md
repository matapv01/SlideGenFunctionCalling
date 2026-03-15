# SlideGen

AI-powered presentation generator. Upload tài liệu hoặc nhập ý tưởng → nhận slide HTML đẹp.

---

## Mục lục

- [Yêu cầu](#yêu-cầu)
- [Cấu hình `.env`](#cấu-hình-env)
- [Chạy với Docker](#chạy-với-docker)
  - [Trên Server](#trên-server)
  - [Local Development](#local-development)
- [Lệnh Docker thường dùng](#lệnh-docker-thường-dùng)
- [Chạy thủ công (không Docker)](#chạy-thủ-công-không-docker)
  - [Trên Server](#trên-server-1)
  - [Local](#local)
- [Quản lý Subscription Codes](#quản-lý-subscription-codes)

---

## Yêu cầu

| Môi trường | Yêu cầu |
|---|---|
| Docker | Docker 24+, Docker Compose v2, Git |
| Thủ công | Python 3.11+, Node.js 22+, uv |

**Cài Docker (nếu server chưa có):**

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

---

## Cấu hình `.env`

```bash
cp env_template.txt .env
nano .env
```

```env
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY1=your_key_here
TAVILY_API_KEY2=your_key_here
TAVILY_API_KEY3=your_key_here
SECRET_KEY=your_jwt_secret_here
```

> `.env` đã git-ignore — phải tạo tay trên mỗi máy, không commit lên git.

---

## Chạy với Docker

### Trên Server

**Lần đầu deploy:**

```bash
# 1. Đăng nhập Docker Hub (cần để pull base image)
docker login

# 2. Clone repo
git clone <repo-url> SlideGenFunctionCalling
cd SlideGenFunctionCalling

# 3. Tạo file .env
cp env_template.txt .env
nano .env   # điền API keys

# 4. Build và chạy
docker compose up -d --build
```

> Lần đầu build mất **15–25 phút** do tải Python deps, Playwright Chromium, Node.js.
> Theo dõi tiến trình: `docker compose logs -f`

**Kiểm tra sau khi build xong:**

```bash
docker compose ps                      # container có đang chạy không?
curl http://localhost:12008/health     # health check
curl -I http://localhost:12008         # frontend load được không?
```

Nếu tất cả trả về `200 OK` → deploy thành công.
Truy cập từ ngoài: `http://<server-ip>:12008`

---

**Update code lên server:**

```bash
# Trên máy local — push code mới
git add .
git commit -m "your message"
git push

# Trên server — pull và rebuild
cd SlideGenFunctionCalling
git pull
docker compose up -d --build
```

> Rebuild lần sau nhanh hơn (~3–5 phút) vì Docker cache các layer không đổi.
> File `.env` và dữ liệu trong volumes **không bị ảnh hưởng** khi rebuild.

---

### Local Development

**Lần đầu:**

```bash
git clone <repo-url> SlideGenFunctionCalling
cd SlideGenFunctionCalling
cp env_template.txt .env   # điền API keys

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Từ lần 2 trở đi:**

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Dev mode khác production:
- Bind-mount `backend/` → sửa code Python có hiệu lực ngay, không cần rebuild
- Log level `DEBUG` tự động bật
- App tại `http://localhost:12008`

---

## Lệnh Docker thường dùng

```bash
# Xem container đang chạy
docker compose ps

# Theo dõi log realtime
docker compose logs -f

# Xem log gần nhất (không realtime)
docker compose logs --tail 100

# Restart không rebuild
docker compose restart

# Dừng (giữ nguyên data)
docker compose down

# Dừng + xóa toàn bộ data (KHÔNG THỂ PHỤC HỒI)
docker compose down -v

# Vào trong container để debug
docker compose exec slidegen bash

# Xem dung lượng image
docker image ls slidegen
```

---

## Chạy thủ công (không Docker)

### Trên Server

Dùng script có sẵn — tự động build frontend và khởi động toàn bộ service trong 1 lệnh:

```bash
./scripts/run_server.sh
```

Script sẽ tự động:
1. Sync Python dependencies (`uv sync`)
2. Build frontend (`npm run build`)
3. Install converter dependencies (`npm install`)
4. Khởi động backend tại `http://0.0.0.0:12008`

Frontend và API cùng chạy trên 1 port — truy cập từ ngoài: `http://<server-ip>:12008`

**Kiểm tra sau khi chạy:**

```bash
curl -I http://127.0.0.1:12008/docs
```

### Local

```bash
# Terminal 1 — Backend
uv sync
uv run backend/main.py
# → http://localhost:12008

# Terminal 2 — Frontend dev server
cd frontend && npm install && npm run dev
# → http://localhost:8080
```

---

## Quản lý Subscription Codes

DB file: `backend/infrastructure/database/slidegen.db`

### Các loại code

| `code_type` | `max_uses` | Hành vi |
|---|---|---|
| `unlimited` | bất kỳ | Dùng bao nhiêu lần cũng được, cùng account cũng gia hạn lại |
| `limited` | `1` | Chỉ 1 tài khoản dùng 1 lần |
| `limited` | `N` | Tối đa N tài khoản, mỗi account 1 lần |

### Code mặc định

| Code | Tier | Loại | Thời hạn |
|---|---|---|---|
| `SLIDEGENIUS` | Ultra | unlimited | 30 ngày/lần nhập |

### Tạo code mới

```bash
# Unlimited
sqlite3 backend/infrastructure/database/slidegen.db \
  "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
   VALUES ('PROMO2025', 'plus', 30, -1, 'unlimited');"

# Giới hạn 1 tài khoản
sqlite3 backend/infrastructure/database/slidegen.db \
  "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
   VALUES ('VIP-ABCD', 'ultra', 30, 1, 'limited');"

# Giới hạn 50 tài khoản
sqlite3 backend/infrastructure/database/slidegen.db \
  "INSERT INTO subscription_codes (code, tier, duration_days, max_uses, code_type)
   VALUES ('LAUNCH50', 'plus', 30, 50, 'limited');"
```

### Tắt / bật code

```bash
sqlite3 backend/infrastructure/database/slidegen.db \
  "UPDATE subscription_codes SET is_active = 0 WHERE code = 'PROMO2025';"

sqlite3 backend/infrastructure/database/slidegen.db \
  "UPDATE subscription_codes SET is_active = 1 WHERE code = 'PROMO2025';"
```

> **Tip:** Dùng [DB Browser for SQLite](https://sqlitebrowser.org/) để quản lý DB trực quan hơn.
