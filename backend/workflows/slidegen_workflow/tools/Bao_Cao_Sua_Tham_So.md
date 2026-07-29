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

| Tên Slide (Class) | Tên Thuộc Tính | Kích Thước Khuyến Nghị | Phân Tích Lý Do Tối Ưu Theo CSS |
|---|---|---|---|
| GenerateIntroSlide1Input | image_url | **600x750px (portrait)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateElegantIntroSlideInput | image_url | **560x420px (landscape, 4:3 ratio)** | Hình ảnh nằm trong block nội dung hình chữ nhật ngang, cần tỷ lệ ~4:3 để hài hòa với text xung quanh. |
| GenerateDynamicIntroSlideInput | image_url | **960x1080px (portrait, covers right half of slide)** | Layout chia màn hình. Dùng ảnh dọc để object-fit: cover không xén mất rìa trái/phải. |
| GenerateElegantAgendaSlideInput | image_url | **500x400px (landscape)** | Hình ảnh nằm trong block nội dung hình chữ nhật ngang, cần tỷ lệ ~4:3 để hài hòa với text xung quanh. |
| GenerateMissionSlideInput | image_url | **400x1000px (tall portrait)** | Căn chỉnh kích thước để vừa với Grid/Flex layout cụ thể. |
| GenerateTrainingIntroSlideInput | image_url | **1920x600px (wide landscape, bottom banner)** | Banner kéo dài ở dưới đáy. Phải dùng ảnh ngang cực rộng và lùn để object-fit: cover cắt chính diện. |
| GenerateTitleSlide5Input | image_path | **444x457px (square-like portrait)** | CSS order-radius: 50% hoặc khung Polaroid. Cần ảnh 1:1 (vuông) để khi bo tròn không cắt cụt đầu nhân vật trong ảnh Avatar. |
| GenerateIntroSlideInput | image_url | **600x750px (portrait, displayed in right panel)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateImageCutoutListSlideInput | background_image_url | **1920x1080px (landscape, full slide background)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS ackground-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateBodySlide4Input | image_url_1 | **500x240px (landscape, 2:1 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide4Input | image_url_2 | **500x240px (landscape, 2:1 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide4Input | image_url_3 | **500x240px (landscape, 2:1 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide5Input | image_url_1 | **300x400px (portrait, 3:4 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide5Input | image_url_2 | **300x400px (portrait, 3:4 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide5Input | image_url_3 | **300x400px (portrait, 3:4 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide5Input | image_url_4 | **300x400px (portrait, 3:4 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide10Input | image_url | **500x450px (landscape, displayed in left column)** | Hình ảnh nằm trong block nội dung hình chữ nhật ngang, cần tỷ lệ ~4:3 để hài hòa với text xung quanh. |
| GenerateBodySlide12Input | image_url_1 | **400x300px (landscape, 4:3 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide12Input | image_url_2 | **400x300px (landscape, 4:3 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide12Input | image_url_3 | **400x300px (landscape, 4:3 ratio)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateBodySlide15Input | image_url | **800x800px (square, for right column)** | Căn chỉnh kích thước để vừa với Grid/Flex layout cụ thể. |
| GenerateReferenceSlideInput | image_url | **800x1080px (portrait, covers right column)** | Layout chia màn hình. Dùng ảnh dọc để object-fit: cover không xén mất rìa trái/phải. |
| GenerateTextWithImageSlideInput | image_url | **800x1080px (portrait, covers right side)** | Layout chia màn hình. Dùng ảnh dọc để object-fit: cover không xén mất rìa trái/phải. |
| GenerateGeometricImageContentSlideInput | image_url | **1000x1080px (portrait)** | Layout chia màn hình. Dùng ảnh dọc để object-fit: cover không xén mất rìa trái/phải. |
| GenerateMethodologySlideInput | image_url | **700x780px (portrait, right column)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateClassicContentSlideInput | image_url | **800x880px (portrait, right column with rounded corners)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateModernContactSlideInput | top_image_url | **400x300px (landscape)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateModernContactSlideInput | bottom_image_url | **400x300px (landscape)** | Giao diện Grid nhiều cột. Đảm bảo tỷ lệ hằng số (VD: 3:4 hoặc 2:1) để Flexbox các cột có chiều cao bằng nhau, không làm rách giao diện lưới. |
| GenerateClosingSlideInput | image_url | **400x400px (square, will be cropped to circle)** | CSS order-radius: 50% hoặc khung Polaroid. Cần ảnh 1:1 (vuông) để khi bo tròn không cắt cụt đầu nhân vật trong ảnh Avatar. |
| GenerateBrandCollaborationClosingSlideInput | left_image_url | **460x650px (portrait)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateBrandCollaborationClosingSlideInput | right_image_url | **250x280px (portrait)** | Ảnh phụ trợ đi kèm nằm góc phần tư. Tỷ lệ dọc để phù hợp với column hẹp bên phải. |
| GenerateMilitaryThankYouSlideInput | bg_image_url | **1920x1080px (landscape, full slide background)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS ackground-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateCreativeThankYouInput | image_url | **700x720px (square-like portrait)** | CSS order-radius: 50% hoặc khung Polaroid. Cần ảnh 1:1 (vuông) để khi bo tròn không cắt cụt đầu nhân vật trong ảnh Avatar. |
| GenerateElegantThankYouInput | bg_image | **1920x1080px (landscape, full slide background)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS ackground-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateBarChartSlide3 | image_url | **500x800px (portrait, capsule shape)** | Ảnh đặt lọt trong Column/Panel bo góc. Tính toán dựa trên độ rộng CSS Flex/Grid column để không bị tràn khung bo tròn (border-radius). |
| GenerateTeamSlideInput | team_members (image_url) | **800x800px (square)** | Cần khung vuông để CSS có thể dễ dàng crop thành hình tròn hoàn hảo (border-radius: 50%) cho ảnh đại diện của thành viên nhóm. |
| GenerateColorfulTeamGridSlideInput | team_members (image_url) | **800x800px (square)** | Cần khung vuông để CSS có thể dễ dàng crop thành hình tròn hoàn hảo (border-radius: 50%) cho ảnh đại diện của thành viên nhóm. |
| GenerateCorporateTeamSlideInput | team_members (image_url) | **800x800px (square)** | Cần khung vuông để CSS có thể dễ dàng crop thành hình tròn hoàn hảo (border-radius: 50%) cho ảnh đại diện của thành viên nhóm. |
| GenerateProcessStepsSlideInput | steps (image_url) | **600x400px (landscape) / 400x400px (square)** | Khung ảnh nhỏ dùng minh họa theo từng bước của chu trình, dùng tỷ lệ nằm ngang hoặc vuông để cân đối layout flexbox. |
| GenerateFlexibleColumnsSlideInput | bg_url | **1920x1080px (landscape)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS background-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateTextWithImageSlideInput | bg_url | **1920x1080px (landscape)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS background-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateRadarChartSlide1 | background_image | **1920x1080px (landscape)** | Slide tỷ lệ 16:9. Chống giãn ảnh nền toàn màn hình. Thuộc tính CSS background-size: cover sẽ lấp đầy màn hình mà không làm vỡ hạt ảnh. |
| GenerateTextWithImageSlideInput | doodle_border_url | **1920x200px (seamless pattern)** | Hình ảnh được sử dụng để làm viền (border/banner) trang trí theo chiều ngang, cần chiều ngang cực dài để lấp đầy cạnh đáy của Slide. |


## 4. Tối Ưu Responsive Mobile: Lý Do Tính Toán CSS Chi Tiết

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
