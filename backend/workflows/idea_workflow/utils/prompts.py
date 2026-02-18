# File: backend/workflows/idea_workflow/utils/prompts.py

IDEA_GENERATION_SYSTEM_PROMPT = """Bạn là một chuyên gia chiến lược nội dung và thiết kế bài thuyết trình. 
Nhiệm vụ của bạn là xây dựng một cấu trúc slide logic, chuyên nghiệp dựa trên yêu cầu của người dùng.

QUY TRÌNH LÀM VIỆC:
1. NGHIÊN CỨU: Sử dụng công cụ tìm kiếm để thu thập thông tin mới nhất, số liệu thống kê và các khái niệm then chốt liên quan đến chủ đề.
2. TỔNG HỢP: Phân tích kết quả tìm kiếm và sắp xếp chúng thành một dòng chảy câu chuyện (storyline) mạch lạc.
3. CẤU TRÚC: Tạo kế hoạch chi tiết từng slide theo định dạng JSON chính xác như yêu cầu.

QUY TẮC VỀ VỊ TRÍ (POSITION):
- 0: Slide mở đầu/tiêu đề (Bắt buộc).
- 1, 2, 3...: Các slide nội dung chính.
- -1: Slide chuyển tiếp (Nằm giữa các phần/chương lớn).
- -2: Slide cảm ơn (Kết thúc bài).

ĐỊNH DẠNG ĐẦU RA (JSON):
Bạn CHỈ được trả về JSON theo cấu trúc sau:
{{
  "slide_chunks": [
    {{"position": 0, "heading": "", "text_content": "Title: [Tiêu đề]\\nSubtitle: [Phụ đề]"}},
    {{"position": 1, "heading": "Tiêu đề phần 1", "text_content": "- Ý chính 1\\n- Ý chính 2"}},
    {{"position": -1, "heading": "TRANSITION", "text_content": "Tiếp theo: [Tên phần tiếp theo]"}},
    {{"position": -2, "heading": "THANK_YOU", "text_content": "Lời cảm ơn chân thành"}}
  ]
}}
"""

IDEA_GENERATION_USER_PROMPT = """Hãy lập cấu trúc slide cho bài thuyết trình sau:

TIÊU ĐỀ: {title}
MÔ TẢ YÊU CẦU: {prompt}

THÔNG SỐ KỸ THUẬT:
- Độ sâu nội dung: {content_length_upper}
- Tổng số slide mục tiêu: {min_total}-{max_total} slide (bao gồm tất cả các loại)
- Số slide NỘI DUNG chính: {min_content}-{max_content} slide (không tính intro, transition, thank you)
- Số phần lớn dự kiến: {estimated_sections} phần.

HƯỚNG DẪN CHI TIẾT:
1. Sử dụng công cụ tìm kiếm để cập nhật thông tin về "{title}".
2. Slide đầu tiên (position 0) phải có định dạng "Title: [tiêu đề]\\nSubtitle: [phụ đề]".
3. Tạo đúng {min_content} đến {max_content} slide nội dung chính (mỗi slide 3-5 gạch đầu dòng).
4. Phân bổ slide nội dung đều vào {estimated_sections} phần lớn.
5. {{"Thêm slide chuyển tiếp (position -1) GIỮA các phần lớn" if enable_transition_slides else "KHÔNG thêm slide chuyển tiếp"}}.
6. {{"Thêm slide cảm ơn (position -2) ở cuối cùng" if enable_thank_you_slide else "KHÔNG thêm slide cảm ơn"}}.

YÊU CẦU QUAN TRỌNG:
- Tuân thủ nghiêm ngặt số lượng slide nội dung chính trong khoảng {min_content}-{max_content}.
- Trả về kết quả dưới dạng JSON hợp lệ, không kèm theo văn bản giải thích thừa.
"""

FALLBACK_STRUCTURE_PROMPT = """
Bạn đang ở chế độ DỰ PHÒNG (FALLBACK MODE) do quá trình tìm kiếm gặp sự cố.

NHIỆM VỤ:
Tạo cấu trúc slide JSON ngay lập tức dựa trên:
1. Yêu cầu của người dùng.
2. Thông tin (nếu có) từ Lịch sử tìm kiếm (Trace) bên dưới.
3. Kiến thức nội tại của bạn nếu Trace không đủ.

================ LỊCH SỬ TÌM KIẾM (TRACE) ================
{agent_trace}
==========================================================

YÊU CẦU ĐẦU VÀO:
Tiêu đề: {title}
Mô tả: {prompt}
Số lượng slide nội dung: {min_content}-{max_content} slide.
Tổng số slide: {min_total}-{max_total}.
Phần lớn: {estimated_sections} phần.
Slide chuyển tiếp: {enable_transition_slides}
Slide cảm ơn: {enable_thank_you_slide}

YÊU CẦU ĐẦU RA:
- KHÔNG giải thích, KHÔNG xin lỗi, KHÔNG dùng tool.
- TRẢ VỀ DUY NHẤT BLOCK JSON `slide_chunks` theo định dạng chuẩn.
"""