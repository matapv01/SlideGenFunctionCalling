# SlideGen

AI-powered presentation generator. Upload tài liệu hoặc nhập ý tưởng → nhận slide HTML đẹp.

---

## Mục lục

- [Yêu cầu](#yêu-cầu)
- [Cấu hình `.env`](#cấu-hình-env)
- [Server (Production)](#server-production)
- [Local Development](#local-development)
- [Lệnh Docker thường dùng](#lệnh-docker-thường-dùng)
- [Quản lý Subscription Codes](#quản-lý-subscription-codes)

---

## Yêu cầu

Docker 24+, Docker Compose v2, Git.

```bash
# Cài Docker nếu server chưa có
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

## Server (Production)

**Lần đầu deploy:**

```bash
git clone <repo-url> SlideGenFunctionCalling
cd SlideGenFunctionCalling

cp env_template.txt .env
nano .env   # điền API keys

docker compose up -d --build
```

> Lần đầu build mất **15–25 phút** do tải Python deps, Playwright Chromium, Node.js.
> Theo dõi: `docker compose logs -f`

**Kiểm tra sau khi build xong:**

```bash
docker compose ps
curl http://localhost:12008/health
```

Truy cập từ ngoài: `http://<server-ip>:12008`

---

**Update code:**

```bash
# Máy local
git add . && git commit -m "..." && git push

# Trên server
git pull
docker compose up -d --build
```

> Rebuild lần sau nhanh (~3–5 phút) nhờ Docker layer cache.
> File `.env` và dữ liệu trong volumes **không bị ảnh hưởng** khi rebuild.

---

## Local Development

**Lần đầu:**

```bash
git clone <repo-url> SlideGenFunctionCalling
cd SlideGenFunctionCalling

cp env_template.txt .env   # điền API keys

docker compose -f docker-compose.dev.yml up --build
```

**Từ lần 2 trở đi:**

```bash
docker compose -f docker-compose.dev.yml up
```

**Dev mode:**

| | URL |
|---|---|
| Frontend (Vite HMR) | `http://localhost:5173` |
| Backend API | `http://localhost:12008` |
| API Docs | `http://localhost:12008/docs` |

- Sửa file trong `backend/` → backend tự reload (uvicorn `--reload`)
- Sửa file trong `frontend/src/` → browser tự cập nhật (Vite HMR)
- Không cần rebuild image khi sửa code

**Rebuild khi nào:**
- Thêm/xóa Python package (`pyproject.toml` đổi)
- Thêm/xóa npm package (`package.json` đổi)

---

## Lệnh Docker thường dùng

```bash
# Xem container đang chạy
docker compose ps

# Theo dõi log realtime
docker compose logs -f

# Xem log gần nhất
docker compose logs --tail 100

# Restart không rebuild
docker compose restart

# Dừng (giữ nguyên data)
docker compose down

# Dừng + xóa toàn bộ data (KHÔNG THỂ PHỤC HỒI)
docker compose down -v

# Vào trong container để debug
docker compose exec slidegen bash          # production
docker compose -f docker-compose.dev.yml exec slidegen-dev bash   # dev

# Rebuild 1 service cụ thể
docker compose build --no-cache
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
# Vào container (production)
docker compose exec slidegen bash

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
