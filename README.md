# 1. Cài dependencies
// backend
uv sync
// frontend
cd frontend
npm install



cd frontend
npm install jszip @types/jszip --legacy-peer-deps

## Tạo file .env (root project)
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY1=your_key_here
TAVILY_API_KEY2=your_key_here
TAVILY_API_KEY3=your_key_here


## Chạy Backend (Terminal 1)
uv run backend/main.py
→ Backend: http://localhost:12008

## Chạy Frontend (Terminal 2)
cd frontend
npm run dev
→ Frontend: http://localhost:8080

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
