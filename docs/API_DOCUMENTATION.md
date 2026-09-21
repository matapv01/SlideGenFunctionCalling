# 📌 HƯỚNG DẪN SỬ DỤNG API — DOCUMENT AI SERVICE

## 🌐 1. THÔNG TIN KẾT NỐI (SERVER IP & BASE URL)

- **Server IP (Public / Truy cập từ xa):** `171.226.10.153`
- **Server IP (Mạng nội bộ LAN / VPN):** `192.168.1.3`
- **Localhost (Chạy trực tiếp trên máy chủ):** `127.0.0.1`
- **Cổng dịch vụ (Port):** `12006`

### Base URLs:
| Môi trường | Base URL |
|---|---|
| **Public URL** (Internet) | `http://171.226.10.153:12006` |

### Tài liệu API tương tác trực quan:
- **Swagger UI:** [http://171.226.10.153:12006/docs](http://171.226.10.153:12006/docs)
- **ReDoc:** [http://171.226.10.153:12006/redoc](http://171.226.10.153:12006/redoc)

---

## 🔐 2. XÁC THỰC & BẢO MẬT (AUTHENTICATION / AUTHORIZATION)

- **Cơ chế xác thực (Authentication):** **Không yêu cầu (`None` / No Auth)**.
- **Authorization Header:** **Không cần** truyền `Authorization: Bearer <token>` hay `X-API-Key`.
- **Mục đích:** Dịch vụ Document AI Service được triển khai dưới dạng **Internal Microservice** trong hạ tầng ADCS, phục vụ trực tiếp cho Backend, Data Service, Pipeline Worker và các ứng dụng tích hợp được phân quyền cấp mạng (Firewall / IP Whitelist).
- **Headers khi gửi Request:**
  - **Upload file (`multipart/form-data`):**
    - Không cần đặt header `Content-Type` thủ công nếu dùng Postman, `fetch` (FormData) hoặc `axios` (để HTTP client tự sinh kèm `boundary`).
    - Nếu dùng `cURL`: sử dụng cờ `-F "file=@/duong/dan/file.pdf"`.
  - **Dữ liệu JSON (`application/json`):**
    - Thêm header: `Content-Type: application/json`.

---

## 📋 3. TỔNG HỢP CÁC API

| # | Method | Endpoint | Content-Type | Chức năng |
|:---:|:---:|---|---|---|
| 1 | `POST` | `/api/v1/analyze-document` | `multipart/form-data` | **API chính:** OCR file → AI tóm tắt, trích xuất metadata, gợi ý phòng ban, hạn xử lý & lưu DB |
| 2 | `POST` | `/api/v1/ocr` | `multipart/form-data` | OCR trích xuất text thuần và bảng biểu thô từ file |
| 3 | `POST` | `/api/v1/summarize` | `application/json` | Gửi cây JSON cấu trúc văn bản có sẵn → AI tóm tắt & gợi ý phòng ban |
| 4 | `POST` | `/api/v1/hierarchy-parse` | `multipart/form-data` | Bóc tách văn bản thành cây cấu trúc phân cấp (Chương, Điều, Khoản...) |
| 5 | `POST` | `/api/v1/raw_miner_ocr` | `multipart/form-data` | Trích xuất bảng biểu trong file thành mã HTML `<table>` bằng MinerU |
| 6 | `POST` | `/api/v1/raw_miner_ocr/qwen` | `multipart/form-data` | Trích xuất bảng và dùng Qwen LLM tự động sửa cú pháp / format lại HTML hoàn chỉnh |
| 7 | `GET` | `/health` | — | Kiểm tra trạng thái hoạt động (Health check) |

---

## 📖 4. CHI TIẾT TỪNG API & CÚ PHÁP GỌI (cURL SAMPLES)

### 1. `POST /api/v1/analyze-document` (Dùng nhiều nhất)
Phân tích toàn diện văn bản hành chính: OCR → AI Map-Reduce Summarize & Metadata Extraction → Data Service.

- **URL:** `http://171.226.10.153:12006/api/v1/analyze-document`
- **Content-Type:** `multipart/form-data`
- **Authorization:** *Không yêu cầu*
- **Request Parameters (Form Data):**
  - `file` *(bắt buộc)*: File tài liệu (hỗ trợ: `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.txt`). Dung lượng tối đa: 50MB.
  - `save_document` *(tùy chọn, `bool`, mặc định `false`)*:
    - `false`: Chỉ phân tích AI (chế độ xem trước / preview), không lưu vào cơ sở dữ liệu.
    - `true`: Phân tích AI và lưu vào Database + VectorDB qua Data Service.
  - `region` *(tùy chọn, `string`, mặc định `"north"`)*: Gợi ý phòng ban theo cơ sở (`"north"`: Hà Nội, `"south"`: TP.HCM, `"both"`: Cả hai).
  - `department_list` *(tùy chọn, `string` JSON array)*: Danh sách phòng ban tùy biến nếu muốn AI gợi ý theo danh sách riêng (vd: `'["Phòng Đào tạo", "Phòng Tài chính"]'`).

#### Ví dụ cURL:
```bash
# Phân tích xem trước (không lưu DB)
curl -X POST "http://171.226.10.153:12006/api/v1/analyze-document" \
  -F "file=@/path/to/van_ban.pdf" \
  -F "save_document=false" \
  -F "region=north"

# Phân tích và lưu vào cơ sở dữ liệu
curl -X POST "http://171.226.10.153:12006/api/v1/analyze-document" \
  -F "file=@/path/to/van_ban.pdf" \
  -F "save_document=true"
```

- **Response mẫu (`200 OK`):**
```json
{
  "trang_thai": "success",
  "tom_tat": "Tóm tắt ngắn gọn nội dung văn bản (5-8 câu)...",
  "key_points": [
    "Điểm chính 1",
    "Điểm chính 2"
  ],
  "loai_van_ban": {
    "nhan": "quyet_dinh",
    "diem_tin_cay": 0.98
  },
  "extracted_fields": {
    "so_hieu_van_ban": "456/QĐ-HVBC",
    "ngay_ban_hanh": "2026-03-30",
    "co_quan_ban_hanh": "Học viện Công nghệ Bưu chính Viễn thông",
    "nguoi_ky": "Trần Văn B",
    "chuc_vu_nguoi_ky": "Giám đốc",
    "noi_nhan": ["Phòng Đào tạo", "Lưu: VT"],
    "trich_yeu": "Về việc phê duyệt chỉ tiêu tuyển sinh 2026",
    "do_khan": "thuong"
  },
  "de_xuat_thoi_han_xu_ly": {
    "so_ngay_de_xuat": 3,
    "muc_uu_tien": "bình thường",
    "ly_do": "Quyết định phê duyệt cần 3 ngày để tiếp nhận và lập kế hoạch."
  },
  "goi_y_phong_ban": {
    "phong_ban": "PDT1",
    "id_phong_ban": 34,
    "ten_hien_thi": "Phòng Đào tạo",
    "ly_do": "Văn bản về tuyển sinh thuộc chức năng Phòng Đào tạo",
    "diem_tin_cay": 0.96
  },
  "storage_info": {
    "document_id": 102,
    "attachment_id": 563,
    "status": "saved"
  },
  "related_documents": [
    {
      "document_id": 98,
      "so_ky_hieu": "312/QĐ-HVBC",
      "trich_yeu": "Quy chế tuyển sinh năm trước",
      "similarity": 0.88
    }
  ],
  "processing_time": 4.12
}
```

---

### 2. `POST /api/v1/ocr`
Đọc văn bản thuần và trích xuất bảng từ file tài liệu (không gọi LLM tóm tắt).

- **URL:** `http://171.226.10.153:12006/api/v1/ocr`
- **Content-Type:** `multipart/form-data`
- **Authorization:** *Không yêu cầu*
- **Request Parameters (Form Data):**
  - `file` *(bắt buộc)*: File tài liệu (PDF, DOCX, ảnh scan JPG/PNG).

#### Ví dụ cURL:
```bash
curl -X POST "http://171.226.10.153:12006/api/v1/ocr" \
  -F "file=@/path/to/van_ban.pdf"
```

- **Response mẫu (`200 OK`):**
```json
{
  "file_name": "van_ban.pdf",
  "text": "Toàn bộ nội dung chữ trích xuất từ văn bản...",
  "pages": 2,
  "tables": [
    {
      "page": 1,
      "table_index": 1,
      "rows": [
        ["STT", "Nội dung", "Số tiền"],
        ["1", "Học phí", "10.000.000"]
      ],
      "row_count": 2,
      "col_count": 3
    }
  ],
  "table_count": 1
}
```

---

### 3. `POST /api/v1/summarize`
Gửi cấu trúc phân cấp JSON có sẵn để AI thực hiện tóm tắt và phân loại phòng ban.

- **URL:** `http://171.226.10.153:12006/api/v1/summarize`
- **Content-Type:** `application/json`
- **Authorization:** *Không yêu cầu*

#### Ví dụ cURL:
```bash
curl -X POST "http://171.226.10.153:12006/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 123,
    "status": "success",
    "pages": 2,
    "content": {
      "type": "root",
      "heading": "Tiêu đề văn bản",
      "text": "Nội dung chi tiết của văn bản...",
      "children": []
    }
  }'
```

- **Response mẫu (`200 OK`):**
```json
{
  "document_id": 123,
  "tom_tat": "Tóm tắt nội dung văn bản...",
  "key_points": ["Điểm chính 1", "Điểm chính 2"],
  "loai_van_ban": {
    "nhan": "cong_van",
    "diem_tin_cay": 0.95
  },
  "goi_y_phong_ban": {
    "phong_ban": "PDT1",
    "ten_hien_thi": "Phòng Đào tạo",
    "ly_do": "Thuộc nghiệp vụ đào tạo"
  },
  "muc_tin_cay": 0.95,
  "processing_time": 1.82
}
```

---

### 4. `POST /api/v1/hierarchy-parse`
Bóc tách nội dung tài liệu thành cây cấu trúc phân cấp (Phần → Chương → Mục → Điều → Khoản).

- **URL:** `http://171.226.10.153:12006/api/v1/hierarchy-parse`
- **Content-Type:** `multipart/form-data`
- **Authorization:** *Không yêu cầu*
- **Request Parameters (Form Data):**
  - `file` *(bắt buộc)*: File tài liệu.
  - `department_list` *(tùy chọn)*: Danh sách phòng ban dưới dạng JSON array.

#### Ví dụ cURL:
```bash
curl -X POST "http://171.226.10.153:12006/api/v1/hierarchy-parse" \
  -F "file=@/path/to/quy_che.pdf"
```

- **Response mẫu (`200 OK`):**
```json
{
  "status": "success",
  "pages": 3,
  "save_document": false,
  "content": {
    "id": "root-node-id",
    "type": "root",
    "heading": "Quy chế đào tạo",
    "text": "",
    "level": 0,
    "children": [
      {
        "type": "chapter",
        "heading": "Chương I: Quy định chung",
        "children": [
          {
            "type": "article",
            "heading": "Điều 1: Phạm vi điều chỉnh",
            "text": "Nội dung điều 1..."
          }
        ]
      }
    ]
  },
  "summary": "Tóm tắt quy chế...",
  "so_ky_hieu": "123/QĐ-HVBC",
  "document_type": "quyet_dinh"
}
```

---

### 5. `POST /api/v1/raw_miner_ocr`
Trích xuất tất cả các bảng biểu trong file thành các khối mã HTML `<table>...</table>` bằng MinerU OCR.

- **URL:** `http://171.226.10.153:12006/api/v1/raw_miner_ocr`
- **Content-Type:** `multipart/form-data`
- **Authorization:** *Không yêu cầu*
- **Request Parameters (Form Data):**
  - `file` *(bắt buộc)*: File PDF hoặc file hình ảnh chứa bảng biểu.

#### Ví dụ cURL:
```bash
curl -X POST "http://171.226.10.153:12006/api/v1/raw_miner_ocr" \
  -F "file=@/path/to/bang_bieu.pdf"
```

- **Response mẫu (`200 OK`):**
```json
{
  "file_name": "bang_bieu.pdf",
  "tables": [
    "<table border='1'><tr><th>STT</th><th>Họ tên</th></tr><tr><td>1</td><td>Nguyễn Văn A</td></tr></table>"
  ],
  "table_count": 1,
  "processing_time": 1.5
}
```

---

### 6. `POST /api/v1/raw_miner_ocr/qwen`
Trích xuất bảng biểu từ PDF/ảnh và dùng mô hình Qwen LLM tự động chuẩn hóa cú pháp, sửa lỗi cấu trúc và làm đẹp HTML.

- **URL:** `http://171.226.10.153:12006/api/v1/raw_miner_ocr/qwen`
- **Content-Type:** `multipart/form-data`
- **Authorization:** *Không yêu cầu*

#### Ví dụ cURL:
```bash
curl -X POST "http://171.226.10.153:12006/api/v1/raw_miner_ocr/qwen" \
  -F "file=@/path/to/bang_bieu.pdf"
```

---

### 7. `GET /health`
Kiểm tra trạng thái sẵn sàng hoạt động của Document AI Service.

- **URL:** `http://171.226.10.153:12006/health`
- **Method:** `GET`
- **Authorization:** *Không yêu cầu*

#### Ví dụ cURL:
```bash
curl -X GET "http://171.226.10.153:12006/health"
```

- **Response (`200 OK`):**
```json
{
  "status": "healthy"
}
```
