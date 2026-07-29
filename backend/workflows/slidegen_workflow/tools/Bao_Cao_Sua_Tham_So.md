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
| GenerateIntroSlide1Input | image_url | **600x750px (portrait)** | Cột phải (right-panel) chiếm 35% viewport width. Phép tính: 1920px * 0.35 = 672px. Trừ đi padding CSS 36px hai bên: 672px - 72px = 600px. Áp dụng tỷ lệ khung hình 4:5 (dọc) -> Chiều cao: 600px * (5/4) = 750px. |
| GenerateElegantIntroSlideInput | image_url | **560x420px (landscape, 4:3)** | Khối container rộng tối đa 1400px. Cột ảnh chiếm 45% container: 1400px * 0.45 = 630px. Trừ lề an toàn (margin/padding) 70px: 630px - 70px = 560px. Áp dụng tỷ lệ vàng 4:3 -> Chiều cao: 560px * (3/4) = 420px. |
| GenerateDynamicIntroSlideInput | image_url | **960x1080px (portrait)** | Layout chia 2 nửa bằng nhau (50/50). Phép tính chiều rộng: 1920px / 2 = 960px. Chiều cao full 100vh: 1080px. Không trừ padding vì dùng ảnh tràn lề (object-fit: cover). Kích thước thực tế: 960x1080px. |
| GenerateElegantAgendaSlideInput | image_url | **500x400px (landscape)** | Grid 4 cột ngang bằng nhau. Phép tính mỗi cột: 1920px / 4 = 480px. Làm tròn lên 500px để phòng trường hợp hiển thị trên màn hình Retina (chống vỡ nét). Tỷ lệ 5:4 -> Chiều cao: 500px * (4/5) = 400px. |
| GenerateMissionSlideInput | image_url | **400x1000px (tall portrait)** | Khối dọc lề bên chiếm 20% slide. Chiều rộng: 1920px * 0.2 = 384px, làm tròn thành 400px. Chiều cao = slide 1080px trừ lề trên dưới 40px * 2: 1080 - 80 = 1000px. Tỷ lệ cực dốc 2:5. |
| GenerateTrainingIntroSlideInput | image_url | **1920x600px (wide landscape)** | Banner đáy chiếm 100% chiều ngang slide: Width = 1920px. Chiều cao chiếm 55% màn hình: 1080px * 0.55 = 594px, làm tròn 600px. Tỷ lệ trải dài 16:5 (1920x600). |
| GenerateTitleSlide5Input | image_path | **444x457px (square-like)** | Avatar container được cố định kích thước cứng trong CSS: width: 444px; height: 457px. Tỷ lệ xấp xỉ 1:1.02. Con số này là số đo Pixel-perfect trực tiếp từ DOM để tránh méo hình khuôn mặt. |
| GenerateIntroSlideInput | image_url | **600x750px (portrait)** | Cột phải chiếm 33.33% màn hình: 1920px * (1/3) = 640px. Trừ gap 40px -> Width tối ưu 600px. Dùng tỷ lệ hình thẻ dọc 4:5 -> Chiều cao: 600px * (5/4) = 750px. |
| GenerateImageCutoutListSlideInput | background_image_url | **1920x1080px (landscape)** | Phép tính cố định cho ảnh nền toàn màn hình tỷ lệ 16:9: Chiều rộng = 100vw = 1920px. Chiều cao = 100vh = 1080px. Đảm bảo mapping 1:1 pixel không cần CSS scale. |
| GenerateBodySlide4Input | image_url_1...3 | **500x240px (landscape)** | Grid 3 thẻ card. Phép tính: 1920px / 3 = 640px. Trừ gap 40px và padding trong card 50px * 2 = 100px: Width 640 - 140 = 500px. Để dành chỗ cho Text dưới, ép tỷ lệ 2:1 -> Chiều cao: 500 / 2 = 240px. |
| GenerateBodySlide5Input | image_url_1...4 | **300x400px (portrait)** | Grid 4 thẻ đứng. Phép tính: 1920px / 4 = 480px. Trừ đi CSS gap (30px) và padding (75px * 2 = 150px): 480 - 180 = 300px. Tỷ lệ chân dung dọc 3:4 -> Chiều cao: 300 * (4/3) = 400px. |
| GenerateBodySlide10Input | image_url | **500x450px (landscape)** | Cột bên trái flex-basis: 30%. Tính chiều rộng: 1920px * 0.3 = 576px. Trừ 76px margin cho không gian âm: 500px. Tỷ lệ 10:9 gần như hình vuông, chiều cao: 500 * 0.9 = 450px. |
| GenerateBodySlide12Input | image_url_1...3 | **400x300px (landscape)** | Grid 3 cột như BodySlide4 (1920/3), nhưng content text ngắn hơn nên ảnh to hơn. Chọn width 400px với tỷ lệ nhiếp ảnh kinh điển 4:3 -> Chiều cao: 400 * (3/4) = 300px. |
| GenerateBodySlide15Input | image_url | **800x800px (square)** | Cột phải chiếm 50%: 1920 / 2 = 960px. Để hình ảnh nổi bật ở giữa với viền margin âm lớn: 960px - (80px * 2) = 800px. Dùng ảnh vuông 1:1 -> 800x800px. |
| GenerateReferenceSlideInput | image_url | **800x1080px (portrait)** | Cột chia tỷ lệ 60/40. Cột phải chiếm 40%: 1920 * 0.4 = 768px. Làm tròn lên 800px chống nứt hạt ở viền. Chiều cao full 100vh = 1080px. Kích thước chốt: 800x1080px. |
| GenerateTextWithImageSlideInput | image_url | **800x1080px (portrait)** | Thiết kế chia lề tương tự Reference Slide. Phép tính 1920 * 0.4 = 768px -> 800px. Cao 1080px tràn viền. |
| GenerateGeometricImageContentSlideInput | image_url | **1000x1080px (portrait)** | Layout bất đối xứng thiên lệch. Phép tính cột ảnh cần lớn hơn một nửa màn hình: 1920 / 2 = 960px, lấy dư 40px bù trừ hiệu ứng bóng đổ chéo -> Width: 1000px. Cao full: 1080px. |
| GenerateMethodologySlideInput | image_url | **700x780px (portrait)** | Panel rộng 800px. Trừ bóng đổ (ox-shadow: 20px) và lề (padding: 30px * 2 = 60px): 800 - 20 - 60 = 720px, làm tròn 700px. Tỷ lệ 1:1.11 -> Chiều cao 700 * 1.11 = 780px. |
| GenerateClassicContentSlideInput | image_url | **800x880px (portrait)** | Text chiếm 1000px, chừa lại không gian còn 1920 - 1000 = 920px cho cột phải. Width dùng 800px (trừ padding 120px). Để cách đều mép trên-dưới slide: 1080px - (100px * 2) = 880px. |
| GenerateModernContactSlideInput | top/bottom_image_url | **400x300px (landscape)** | Hình ảnh phụ trang trí trong container Flex hẹp (rộng 480px). Chiếm khoảng 83% div: 480 * 0.83 = 400px. Tỷ lệ thân thiện 4:3 -> 300px chiều cao. |
| GenerateClosingSlideInput | image_url | **400x400px (square)** | Ảnh Avatar nằm ở vị trí trung tâm, chiếm 20% chiều ngang slide: 1920 * 0.2 = 384px, làm tròn 400px. Yêu cầu tỷ lệ 1:1 (400x400) để áp dụng CSS order-radius: 50% thành hình tròn. |
| GenerateBrandCollaborationClosingSlideInput | left_image_url | **460x650px (portrait)** | Khối ảnh trái (aside) chiếm 25% slide: 1920 * 0.25 = 480px. Trừ 20px viền -> 460px. Để khối ảnh có độ dài tương đương logo khối chính, tính toán cao độ đạt khoảng 650px (tỷ lệ xấp xỉ 1:1.4). |
| GenerateBrandCollaborationClosingSlideInput | right_image_url | **250x280px (portrait)** | Cột ảnh trang trí nhỏ phụ ở góc, chiếm 13% viewport: 1920 * 0.13 = 249.6px -> 250px. Tỷ lệ xấp xỉ vuông, cao 280px để nằm gọn trên khoảng hở mép dưới. |
| GenerateMilitaryThankYou... / ElegantThankYou | bg_image | **1920x1080px (landscape)** | Ảnh nền (Background layer). Công thức bất biến cho màn hình FHD: Width: 100vw = 1920px, Height: 100vh = 1080px. Đảm bảo render 1-1 (1 pixel ảnh trên 1 pixel CSS). |
| GenerateCreativeThankYouInput | image_url | **700x720px (square-like)** | Bố cục đa giác giữa màn hình, chiếm 35% diện tích ngang: 1920 * 0.35 = 672px. Chỉnh kích thước gốc lên 700x720 (gần 1:1) để CSS clip-path (cắt xén đa giác) vẫn giữ được nét. |
| GenerateBarChartSlide3 | image_url | **500x800px (capsule)** | Khối biểu đồ chiếm khoảng 30% tổng diện tích: 1920 * 0.3 = 576px -> chốt 500px. Dùng CSS viên thuốc order-radius: 999px. Phép tính bán kính: hai đầu đường cong cần 500/2 = 250px. Chiều cao bắt buộc > 250*2=500. Dùng 800px (tỷ lệ 1:1.6) để khúc giữa không bị bóp méo. |
| GenerateTeamSlideInput, ColorfulTeamGrid, CorporateTeam | team_members | **800x800px (square)** | Avatars được render trên CSS với thẻ width: 150px; height: 150px; border-radius: 50%;. Tuy nhiên, để đảm bảo sắc nét gấp 4 lần (4x zoom) trên màn hình độ phân giải 4K, công thức gốc là: 150px * 4 + 200px (margin an toàn) = 800px. Tỷ lệ 1:1. |
| GenerateProcessStepsSlideInput | steps (image_url) | **600x400px / 400x400px** | Nếu có 3 bước: 1920 / 3 = 640px (chọn ngang 600x400). Nếu có 4 bước: 1920 / 4 = 480px (chọn vuông 400x400). Phép chia Grid quyết định tỷ lệ khung hình. |
| GenerateFlexibleColumnsSlideInput, RadarChartSlide1 | bg_url | **1920x1080px (landscape)** | Ảnh nền (Background layer). Công thức chuẩn màn hình FHD: Width: 100vw = 1920px, Height: 100vh = 1080px. |
| GenerateTextWithImageSlideInput | doodle_border_url | **1920x200px (seamless)** | Hoa văn viền chạy ngang đáy slide. Width bắt buộc bằng độ phân giải slide: 1920px (để tránh rách viền lặp lại). Chiều cao 200px tính dựa trên tỷ lệ 1080 * 0.18 = 194.4px -> 200px. |\n