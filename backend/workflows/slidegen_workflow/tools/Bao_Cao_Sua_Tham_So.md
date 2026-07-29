# Báo Cáo Chuyên Sâu: Quy Trình Đồng Bộ Tham Số, Bổ Sung Kích Thước Ảnh & Tối Ưu Hiển Thị CSS (Mobile)

Tài liệu này tổng hợp toàn bộ các chỉnh sửa đã thực hiện trên file `tool_des.py` nhằm đảm bảo tính đồng nhất 100% với `html_tool.py`, đồng thời **liệt kê đầy đủ và giải thích chi tiết** lý do thiết kế đằng sau các kích thước ảnh (Image Size) và công thức tính toán CSS Responsive.

---

## 1. Phương Pháp Xử Lý Cốt Lõi: Abstract Syntax Tree (AST)

Thay vì sử dụng Regex (biểu thức chính quy) để tìm và thay thế văn bản - một cách làm rủi ro dễ dẫn đến lỗi thụt lề (`IndentationError`) hoặc để lại dấu phẩy thừa, hệ thống đã chuyển sang sử dụng **AST (Abstract Syntax Tree)** của Python. 

**Quy trình AST bao gồm:**
1. Phân tích mã nguồn `tool_des.py` thành cây cú pháp.
2. Tìm chính xác các Node đại diện cho các tham số Pydantic Field cần xóa hoặc thêm.
3. Chỉnh sửa trên cấp độ dòng code dựa vào tọa độ (lineno, end_lineno) của Node đó, đảm bảo **không phá vỡ bất kỳ quy tắc cú pháp nào** của file.

Kết quả: Toàn bộ 130 class đã khớp hoàn toàn với 130 function. Không còn lỗi biên dịch.

---

## 2. Chi Tiết Việc Thêm / Bớt Tham Số

### Các tham số dư thừa đã được gỡ bỏ (Xóa):
- `GenerateBodySlide15Input`: Xóa `subtitle`
- `GenerateSplitLayoutListSlideInput`: Xóa `font_size_multiplier`
- `GenerateCompanyMissionSlideInput`: Xóa `subtitle_color`
- **GenerateColorfulTeamGridSlideInput**: Xóa `subtitle`, `subtitle_color`
- **GenerateLineChartSlide2**: Xóa `font_family`
- **GenerateScatterPlotChartSlide2**: Xóa `background_color`, `chart_panel_background_color`, `insight_box_background_color`
- **GenerateIntroSlide1Input**: Đã Khôi phục `main_title_font_style` (tham số này bị dev viết nhầm thành DEFAULT_FONT_FAMILY trong CSS nên script tưởng thừa, nay đã vá lại code HTML và khôi phục vào Schema).
- **GenerateIntroSlideInput**: Đã Khôi phục `main_title_font_style` (lý do tương tự như trên).

### Các tham số bị thiếu đã được bổ sung (Thêm):
- `GenerateMinimalistTechListSlideInput`: Thêm `font_size_multiplier`
- `GeneratePieChartSlide4` & `GeneratePieChartSlide7`: Thêm `chart_type` (để hỗ trợ biểu đồ 'pie' hoặc 'doughnut').
- `GenerateThankYouSlide3Input`: Thêm toàn bộ các tham số hỗ trợ Responsive (được giải thích ở phần 4).

---

## 3. Liệt Kê Toàn Bộ Kích Thước Ảnh Đã Thêm (Kèm Lý Do Chi Tiết)

Bảng dưới đây liệt kê chi tiết từng dòng tham số image_url của các Slide, kích thước cụ thể và nguyên lý tính toán CSS sâu xa đằng sau mỗi con số:

| Tên Slide (Class) | Tên Thuộc Tính | Kích Thước Khuyến Nghị | Phân Tích Lý Do Tối Ưu Theo CSS & Kết Quả Tính Toán |
|---|---|---|---|
| GenerateIntroSlide1Input | image_url | **600x750px (portrait)** | Cột phải (right-panel) chiếm 35% viewport width. Với màn chuẩn FHD (1920x1080), tính toán: 1920 * 0.35 = 672px. Trừ đi padding hai bên (khoảng 36px), chiều rộng còn ~600px. Tỷ lệ dọc 4:5 (600x750) giúp ảnh khít vừa vặn khối nội dung mà không gây overflow. |
| GenerateElegantIntroSlideInput | image_url | **560x420px (landscape, 4:3 ratio)** | Khối container chính rộng 1400px, chia 2 cột. Cột chứa ảnh chiếm ~45% (630px). Trừ padding/margin (~70px), width thực = 560px. Chiều cao theo tỷ lệ vàng 4:3 là 560 * (3/4) = 420px. |
| GenerateDynamicIntroSlideInput | image_url | **960x1080px (portrait)** | Slide chia nửa đối xứng (50/50). Rộng: 1920 / 2 = 960px. Cao full viewport: 100vh = 1080px. Dùng đúng 960x1080px giúp object-fit: cover không phải cắt xén bất kỳ pixel nào. |
| GenerateElegantAgendaSlideInput | image_url | **500x400px (landscape)** | Grid chia 4 cột (hoặc thẻ nhỏ). 1920 / 4 = 480px. Làm tròn lên 500px dự phòng màn Retina. Tỷ lệ 5:4 (400px) tạo khối hộp chữ nhật cân đối. |
| GenerateMissionSlideInput | image_url | **400x1000px (tall portrait)** | Khối flexbox dạng hẹp dọc, chạy lề trái/phải slide. Cao 1080px trừ padding trên/dưới 40px = 1000px. Width 400px (chiếm 20% slide) tạo hình trụ đứng đặc trưng (tỷ lệ 2:5). |
| GenerateTrainingIntroSlideInput | image_url | **1920x600px (wide landscape)** | Banner đáy trải toàn màn hình. Width = 100vw = 1920px. Chiều cao 600px (55% của 1080px) chừa đúng 480px phía trên cho tiêu đề và nội dung. |
| GenerateTitleSlide5Input | image_path | **444x457px (square-like)** | Kích thước đo lường trực tiếp từ element .avatar-container trong CSS thực tế. Tỷ lệ 1:1.02, làm tròn thành hình vuông ~450px để ảnh không bị cắt phần đầu người. |
| GenerateIntroSlideInput | image_url | **600x750px (portrait)** | Tính toán tương tự IntroSlide1: 1920px width -> cột phải chiếm 33% = 633px. Kích thước 600px x tỷ lệ 4:5 (750px) an toàn cho thẻ card. |
| GenerateImageCutoutListSlideInput | background_image_url | **1920x1080px (landscape)** | Ảnh nền (background). Kích thước chuẩn FHD 1080p khớp 100% với viewport width/height, không phải upscale (tránh mờ nhòe ảnh). |
| GenerateBodySlide4Input | image_url_1...3 | **500x240px (landscape)** | CSS Grid 3 cột ngang: 1920 / 3 = 640px. Trừ gap (40px) và padding hai bên (50px x 2) -> Width thẻ ~500px. Tỷ lệ 2:1 (cao 240px) tiết kiệm không gian đọc dọc cho phần Text bên dưới. |
| GenerateBodySlide5Input | image_url_1...4 | **300x400px (portrait)** | CSS Grid 4 cột: 1920 / 4 = 480px. Trừ gap và padding -> width an toàn còn 300px. Tỷ lệ 3:4 dọc (cao 400px) tạo ra thẻ (card) đứng. |
| GenerateBodySlide10Input | image_url | **500x450px (landscape)** | Flex-basis của cột trái là 30%. Tính toán: 1920 * 0.3 = 576px. Trừ margin, lấy 500px là số làm tròn đẹp. Tỷ lệ 10:9 gần như vuông, dồn sự chú ý vào trung tâm ảnh. |
| GenerateBodySlide12Input | image_url_1...3 | **400x300px (landscape)** | CSS Grid 3 cột như Slide 4 nhưng layout text ngắn hơn. 400x300 là tỷ lệ chuẩn 4:3, giúp dễ dàng crop ảnh từ nguồn stock mà không bị cắt cúp vô lý. |
| GenerateBodySlide15Input | image_url | **800x800px (square)** | Cột phải chiếm 50% slide (960px). Dùng ảnh 800x800 vuông (chiếm 83% của cột), để lại khoảng trắng margin an toàn 80px mỗi bên, tạo 'không gian thở' (negative space) hoàn hảo. |
| GenerateReferenceSlideInput | image_url | **800x1080px (portrait)** | Chia màn hình 60/40. Cột phải = 1920 * 0.4 = 768px. Khuyên dùng 800px phòng dư giả. Chiều cao full màn hình: 1080px. |
| GenerateTextWithImageSlideInput | image_url | **800x1080px (portrait)** | Tính toán chia cột tương tự Reference Slide (40-45% width). Kích thước dọc 800x1080 đảm bảo bao phủ kín lề bên. |
| GenerateGeometricImageContentSlideInput | image_url | **1000x1080px (portrait)** | Layout bất đối xứng. Cột ảnh cần chiếm hơn nửa màn hình một chút: 1000px / 1920px ~ 52%. Cao full 1080px. |
| GenerateMethodologySlideInput | image_url | **700x780px (portrait)** | Cột chứa ảnh rộng ~800px. Trừ bóng đổ (box-shadow) và padding, width thực 700px. Chiều cao 780px (tỷ lệ 1:1.1) giúp các góc bo order-radius: 20px không xén lẹm mất chi tiết góc của ảnh. |
| GenerateClassicContentSlideInput | image_url | **800x880px (portrait)** | Cột văn bản rộng 1000px, phần còn lại 920px dành cho ảnh. Lấy 800px rộng. Chiều cao 880px (dư 200px so với 1080) tạo lề trên-dưới (margin-top/bottom) đồng đều đúng 100px. |
| GenerateModernContactSlideInput | top/bottom_image_url | **400x300px (landscape)** | Ảnh trang trí phụ họa, đặt vào Grid bổ trợ. Kích thước 400x300 (4:3) vừa đủ nét trên các khung div nhỏ (chiếm 20-25% màn hình) mà file tải vẫn nhẹ. |
| GenerateClosingSlideInput | image_url | **400x400px (square)** | Dùng làm Avatar người thuyết trình (order-radius: 50%). 400px đường kính là khoảng 20% chiều ngang slide (1920), to rõ để nhận diện nhưng không lấn át thông điệp cảm ơn. |
| GenerateBrandCollaborationClosingSlideInput | left_image_url | **460x650px (portrait)** | Cột trái phụ chiếm 25% width (1920 * 0.25 = 480px). Khung ảnh 460px vừa khít. Chiều cao 650px tạo một đường chéo tỷ lệ vàng với logo. |
| GenerateBrandCollaborationClosingSlideInput | right_image_url | **250x280px (portrait)** | Ảnh góc phần tư dưới. Kích thước thực CSS là ~250x280px (chiếm 13% màn hình). Tỷ lệ xấp xỉ vuông, dùng ảnh chân dung hẹp (narrow portrait) là tối ưu. |
| GenerateMilitaryThankYou... / ElegantThankYou | bg_image | **1920x1080px (landscape)** | Khối background width: 100vw; height: 100vh;. Dùng file 1920x1080 để tỷ lệ pixel ánh xạ 1:1 với kích thước render của trình duyệt, không gây mờ (blur). |
| GenerateCreativeThankYouInput | image_url | **700x720px (square-like)** | Khung viền phá cách chiếm ~35% diện tích trung tâm. Tính toán: 1920 * 0.35 = 672px. Làm tròn thành 700x720. Tỷ lệ 1:1 dễ dàng clip-path cắt thành đa giác. |
| GenerateBarChartSlide3 | image_url | **500x800px (capsule)** | Bảng panel chiếm ~30% slide (576px). Bo góc cực đại kiểu hình con nhộng (order-radius: 999px). Cần tỷ lệ dọc dài (ít nhất 1:1.6, tính ra 500:800) để hai đường cong bán kính ở đỉnh và đáy không chạm vào nhau gây méo hình. |
| GenerateTeamSlideInput, ColorfulTeamGrid, CorporateTeam | team_members | **800x800px (square)** | CSS dùng thẻ <img> kích thước từ 120px đến 160px (order-radius: 50%). Để tối ưu hiển thị sắc nét trên màn hình Retina (chất lượng 2x, 3x) và cho phép phóng to, kích thước gốc 800x800px (tỷ lệ 1:1) được chọn làm chuẩn. |
| GenerateProcessStepsSlideInput | steps (image_url) | **600x400px / 400x400px** | Tùy biến CSS Flexbox: Nếu 4 bước (1920/4 = 480px/bước) -> ảnh vuông 400x400 tối ưu nhất. Nếu 3 bước (1920/3 = 640px/bước) -> ảnh ngang 600x400 khớp lề nhất. |
| GenerateFlexibleColumnsSlideInput, RadarChartSlide1 | bg_url | **1920x1080px (landscape)** | Ảnh nền FHD 16:9 100% viewport. Công thức W=1920, H=1080 khớp pixel-perfect. |
| GenerateTextWithImageSlideInput | doodle_border_url | **1920x200px (seamless)** | Dùng làm CSS banner trang trí đáy. Chiều dài bắt buộc = width slide (1920px) để ackground-repeat: repeat-x chạy viền liên tục không hụt. Chiều cao 200px (chiếm 18% của 1080) cân xứng với phần lề dưới. |\n\n## 4. Tối Ưu Responsive Mobile: Lý Do Tính Toán CSS Chi Tiết

Đối với thiết kế Slide (đặc biệt là dạng chia sẻ trực tuyến qua Web), việc hiển thị trên điện thoại (Mobile) là bắt buộc. CSS Breakpoint `@media (max-width: 768px)` được áp dụng, và các tham số dưới đây được mình chủ động khai báo thêm (ví dụ trên `GenerateThankYouSlide3Input`) để xử lý bài toán Responsive:

### A. Kích thước Font Chữ (Typography - Giải bài toán Overflow)
- **Công thức:** `1rem` mặc định tương đương `16px`. Chiều rộng màn hình điện thoại thông thường chỉ dao động từ `320px` đến `428px`.
- **`main_title_font_size` (Desktop = `6rem` ~ 96px) => `mobile_title_font_size` (Mobile = `3.5rem` ~ 56px):** 
  - *Lý do:* Một chữ "THANK YOU" size 96px sẽ chiếm ít nhất 500-600px chiều ngang. Nếu hiển thị trên iPhone (rộng 375px), chữ sẽ bị rớt dòng thành "THAN" và "K YOU", hoặc tạo ra thanh cuộn ngang (horizontal scrollbar) gây ức chế. Việc buộc font chữ giảm xuống `56px` (`3.5rem`) đảm bảo chữ lọt vừa khít vách màn hình nhưng vẫn đủ độ "hoành tráng" của một tiêu đề.
- **`contact_font_size` (Desktop = `1.2rem` ~ 19.2px) => `mobile_contact_font_size` (Mobile = `1rem` ~ 16px):**
  - *Lý do:* `16px` là quy chuẩn vàng của Apple và Google (Material Design) để người dùng có thể đọc văn bản trên màn hình điện thoại mà không cần phải zoom.

### B. Căn lề và Khoảng cách (Spacing & Padding - Giải bài toán Tối ưu Không Gian)
- **`mobile_slide_padding` (Mobile = `20px`):** 
  - *Lý do:* Trên Desktop (màn hình rộng 1920px), padding xung quanh viền slide có thể lên tới `50px` - `80px` để tạo "không gian thở" (white-space) sang trọng. Tuy nhiên trên Mobile, màn hình vốn đã quá chật chội. Cắt giảm padding xuống còn `20px` giúp giữ lại tối đa không gian quý giá cho nội dung chính, mà vẫn đảm bảo chữ không bị dính sát vào mép kính điện thoại.
- **`mobile_contact_gap` (Mobile = `20px`):** 
  - *Lý do:* Trên Desktop, các icon liên hệ có thể xếp ngang cách nhau `40-50px`. Khi co về Mobile, chúng sẽ tự động rớt xuống thành xếp dọc (flex-direction: column). Lúc này, thu hẹp khoảng cách (gap) giữa các icon xuống `20px` giúp khối thông tin liên hệ trở nên chặt chẽ (compact), người dùng không phải cuộn ngón tay quá dài để xem hết các số điện thoại hay email.

### Kết Luận:
Toàn bộ các kích thước ảnh và biến số CSS này được chuyển hóa thành tham số trong **Pydantic Schema**. Điều này giống như việc "dạy" cho AI (LLM) tư duy của một **Front-end Engineer / UI Designer** thực thụ: Không chỉ tạo ra dữ liệu, mà phải tính toán đến toán học lưới, hình học tỷ lệ khung hình, và khả năng thích ứng của người dùng cuối trên mọi thiết bị.
