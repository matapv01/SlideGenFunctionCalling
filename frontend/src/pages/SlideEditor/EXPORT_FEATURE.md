# 📤 Tính năng Export Slide

## Tổng quan

Chức năng export slide đã được tích hợp vào React SlideEditor, chuyển đổi từ pattern **ExportMixin.js** (vanilla JS) sang **Custom Hook** (React).

## 📁 Cấu trúc files

```
frontend/src/pages/SlideEditor/
├── hooks/
│   └── useSlideExport.ts        ← Custom hook xử lý export logic
└── components/
    └── ExportModal.tsx          ← Modal component chọn kiểu export
```

## 🎯 Cách hoạt động

### 1. **useSlideExport Hook**
```typescript
const { exportHTML } = useSlideExport();

// Export slides
exportHTML(slides, 'responsive' | 'fixed');
```

**Chức năng:**
- `exportHTML()` - Xuất slides thành file HTML
- `createSlideHTML()` - Tạo HTML cho 1 slide
- `createIndexHTML()` - Tạo trang index liệt kê slides

### 2. **ExportModal Component**
Modal cho phép người dùng chọn:
- 🖥️ **Responsive**: Tự động scale theo màn hình
- 📏 **Fixed**: Giữ nguyên kích thước 1920×1080

### 3. **Tích hợp vào Toolbar**
Button "Export" trong toolbar → Mở modal → Chọn type → Xuất file

## 🚀 Hành vi export

### Single Slide (1 slide)
```
Click Export → Chọn type → Tải file slide.html
```

### Multiple Slides (nhiều slides)
```
Click Export → Chọn type → Tải file slides.zip
```

**Cấu trúc ZIP:**
```
slides.zip
├── index.html          ← Trang chủ liệt kê tất cả slides
├── slide_001.html      ← Slide 1
├── slide_002.html      ← Slide 2
└── slide_XXX.html      ← Slide N
```

## 🔧 Dependencies

**Cần cài đặt:**
```bash
npm install jszip @types/jszip --legacy-peer-deps
```

**Đã có sẵn:**
- `@radix-ui/react-dialog` - Modal component
- `lucide-react` - Icons

## 💻 Implementation details

### Responsive Mode
Sử dụng CSS transform để scale:
```css
transform: scale(calc(min(100vw / 1920, 100vh / 1080)));
```

### Fixed Mode
Giữ nguyên kích thước:
```css
width: 1920px;
height: 1080px;
```

### HTML Template
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Styles cho slide-container và elements */
  </style>
</head>
<body>
  <div class="slide-container">
    <!-- Elements được render ở đây -->
  </div>
</body>
</html>
```

## ✅ So sánh với ExportMixin.js

| Feature | ExportMixin.js | useSlideExport.ts |
|---------|----------------|-------------------|
| Pattern | Mixin | Custom Hook |
| Modal | `document.createElement()` | React Component |
| State | `this.slides` | Parameter `slides` |
| JSZip | Global import | Dynamic import |
| Type Safety | ❌ No | ✅ TypeScript |

## 🔍 Testing

**Test cases:**
1. ✅ Export 1 slide → file `slide.html`
2. ✅ Export nhiều slides → file `slides.zip`
3. ✅ Responsive mode → Scale theo màn hình
4. ✅ Fixed mode → Giữ nguyên 1920×1080
5. ✅ Index.html → Links tới tất cả slides

## 🐛 Error Handling

- Không có slide → Alert "Không có slide nào để xuất!"
- JSZip chưa cài → Alert "Vui lòng cài đặt jszip..."
- Lỗi export → Alert "Có lỗi xảy ra khi xuất slides!"

## 📝 Notes

- HTML export chỉ render **elements hiện tại** của slide
- Background color/image được giữ nguyên
- Editor-specific elements (resize handles) đã được loại bỏ
- Z-index được preserve để giữ thứ tự layers
- Font styles và colors được inline vào style attribute
