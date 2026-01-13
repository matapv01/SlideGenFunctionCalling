# Tích hợp Pixabay API vào SlideGen

## 📸 Giới thiệu

Tính năng mới cho phép bạn tìm kiếm và sử dụng hàng triệu hình ảnh miễn phí từ Pixabay trực tiếp trong SlideGen Editor.

## 🚀 Tính năng

### Backend API
- **Tìm kiếm hình ảnh**: `/api/pixabay/search/images`
- **Tìm kiếm video**: `/api/pixabay/search/videos`
- **Lấy ảnh tốt nhất**: `/api/pixabay/best-image`

### Frontend UI
- Giao diện tìm kiếm trong tab "Thành Phần"
- Lọc theo loại ảnh (Photo, Illustration, Vector)
- Lọc theo hướng (Ngang, Dọc, Tất cả)
- Xem trước và chọn ảnh
- Kéo thả ảnh vào slide

## 📦 Cài đặt

1. Cài đặt thư viện Python:
```bash
pip install requests
```

2. Khởi động lại backend:
```bash
cd web/backend
python run.py
```

## 🎯 Cách sử dụng

### 1. Trong Editor

1. Mở trang Edit: `http://localhost:8000/edit`
2. Click tab "**Thành Phần**" ở thanh bên trái
3. Tìm mục "**🌐 Pixabay - Hình ảnh miễn phí**" (ở đầu danh sách)
4. Nhập từ khóa tìm kiếm (bằng tiếng Anh, VD: "technology", "business")
5. Chọn loại ảnh và hướng ảnh
6. Nhấn nút "**Tìm**"
7. Click vào ảnh để thêm vào slide

### 2. Qua API

#### Tìm kiếm hình ảnh
```bash
curl "http://localhost:8000/api/pixabay/search/images?q=technology&image_type=photo&orientation=horizontal"
```

#### Lấy ảnh tốt nhất
```bash
curl "http://localhost:8000/api/pixabay/best-image?q=business&quality=large"
```

### 3. Trong Python Code

```python
from src.tools.pixabay_tool import PixabayTool

# Tìm kiếm
results = PixabayTool.search_images(
    q="technology",
    image_type="photo",
    orientation="horizontal",
    per_page=10
)

# Lấy ảnh tốt nhất
best_image = PixabayTool.search_and_get_best_image(
    query="business meeting",
    orientation="horizontal",
    quality="large"
)

print(f"Image URL: {best_image['url']}")
```

## 🎨 Các tham số tìm kiếm

### Loại hình ảnh (image_type)
- `photo` - Ảnh chụp thật
- `illustration` - Hình minh họa
- `vector` - Đồ họa vector

### Hướng ảnh (orientation)
- `horizontal` - Ảnh ngang (phù hợp cho slide)
- `vertical` - Ảnh dọc
- `all` - Tất cả

### Chất lượng (quality)
- `preview` - 150px (nhanh)
- `webformat` - 640px (trung bình)
- `large` - 1280px (chất lượng cao)

### Danh mục (category)
- backgrounds, fashion, nature, science
- education, feelings, health, people
- religion, places, animals, industry
- computer, food, sports, transportation
- travel, buildings, business, music

### Màu sắc (colors)
- grayscale, transparent, red, orange
- yellow, green, turquoise, blue
- lilac, pink, white, gray, black, brown

## ⚠️ Lưu ý quan trọng

### 1. Rate Limit
- **100 requests / 60 giây**
- Nên cache kết quả trong 24 giờ
- Tránh gửi request liên tục

### 2. Attribution (Ghi nguồn)
- Pixabay yêu cầu ghi nguồn khi hiển thị ảnh
- UI tự động hiển thị "Images from Pixabay"
- Nên giữ nguyên attribution này

### 3. Hotlinking
- **KHÔNG được hotlink** (link trực tiếp đến URL Pixabay)
- Nên download ảnh về server trước khi sử dụng lâu dài
- URL chỉ dùng để xem trước tạm thời

### 4. API Key
- API key hiện tại: `54167480-1cbc91f10888131422616cb30`
- Có thể thay đổi trong file `src/tools/pixabay_tool.py`

## 📁 Cấu trúc file

```
SlideGenFunctionCalling/
├── src/tools/
│   └── pixabay_tool.py          # Backend tool
├── web/
│   ├── backend/app/
│   │   └── main.py              # API endpoints (đã cập nhật)
│   └── frontend/
│       ├── edit.html            # UI search box (đã cập nhật)
│       └── js/
│           ├── pixabay.js       # Pixabay Manager (mới)
│           └── init/
│               └── init.js      # Import Pixabay (đã cập nhật)
└── requirements.txt             # Thêm 'requests'
```

## 🐛 Troubleshooting

### Lỗi: "Module not found: requests"
```bash
pip install requests
```

### Lỗi: "Pixabay API rate limit exceeded"
- Đợi 60 giây rồi thử lại
- Giảm số lượng request

### Không tìm thấy kết quả
- Thử từ khóa tiếng Anh khác
- Thay đổi bộ lọc (loại ảnh, hướng)
- Kiểm tra kết nối internet

### Ảnh không load được
- Kiểm tra URL có còn hợp lệ không
- Thử chất lượng khác (webformat thay vì large)
- Download ảnh về server

## 📚 Tài liệu tham khảo

- [Pixabay API Documentation](https://pixabay.com/api/docs/)
- [Pixabay Content License](https://pixabay.com/service/license/)

## 🎉 Ví dụ từ khóa hay

- **Business**: "business meeting", "office workspace", "teamwork"
- **Technology**: "technology", "laptop coding", "digital innovation"
- **Nature**: "mountain landscape", "ocean sunset", "forest path"
- **Abstract**: "abstract background", "geometric pattern", "gradient"
- **Education**: "classroom", "students learning", "books"

## 📝 TODO (Tương lai)

- [ ] Cache kết quả tìm kiếm trong 24h
- [ ] Download và lưu ảnh tự động về server
- [ ] Tìm kiếm video từ Pixabay
- [ ] Lọc theo màu sắc
- [ ] Pagination (phân trang kết quả)
- [ ] Preview ảnh fullscreen trước khi chọn
