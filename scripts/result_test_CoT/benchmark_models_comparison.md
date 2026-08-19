# 📊 Báo Cáo So Sánh Benchmark Generator 🔄 Executor Loop

Tài liệu này tổng hợp và so sánh chi tiết kết quả benchmark giữa 3 phiên bản mô hình **Qwen** khi chạy thử nghiệm trên bộ dataset mẫu SlideGen (51–53 samples, Max Retries: 5).

---

## 1. 🎯 Bảng So Sánh Tổng Quan (Overall Benchmark Summary)

| Chỉ số (Metric) | 🥇 **Qwen 3 8B** | 🥈 **Qwen 3 14B AWQ** | 🥉 **Qwen 3.5 9B** |
| :--- | :---: | :---: | :---: |
| **Tổng số Sample test** | **53** | **52** | **51** |
| **Pass Rate (Tỷ lệ vượt qua)** | **56.6%** (30/53) | **55.8%** (29/52) | **25.5%** (13/51) |
| **First-Try Pass Rate (Vượt qua ngay Lần 1)** | **0.0%** (0/53) | **0.0%** (0/52) | **0.0%** (0/51) |
| **Tool Name Match (Khớp Tool chuẩn GT)** | **7.5%** (4/53) | **5.8%** (3/52) | **2.0%** (1/51) |
| **Trung bình số lượt thử (Avg Attempts)** | **3.87** | **4.10** | **4.63** |
| **Thời gian phản hồi TB (Avg Latency)** | **169.14s** | **86.40s** ⚡ | **351.59s** 🐢 |

> [!TIP]
> **Nhận xét nhanh:**
> - **Qwen 3 8B** đạt tỷ lệ thành công tổng thể cao nhất (**56.6%**) và có độ chính xác khớp tên tool cao nhất (**7.5%**).
> - **Qwen 3 14B AWQ** có tỷ lệ thành công suýt soát 8B (**55.8%**), nhưng có tốc độ xử lý nhanh nhất vượt trội (**86.4s** - gấp 2 lần 8B và gấp 4 lần 3.5 9B).
> - **Qwen 3.5 9B** cho kết quả thấp nhất đáng kể (**25.5%**) với thời gian trễ rất cao (**351.59s**).

---

## 2. 🔄 Phân Bố Số Lượt Thử (Attempts Breakdown)

Bảng dưới đây thống kê số lượng mẫu vượt qua (Pass) theo từng số lần thử (Attempt 1 -> 5) và số mẫu thất bại hoàn toàn (Fail > 5 retries):

| Số lần thử (Attempt) | Qwen 3 8B | Qwen 3 14B AWQ | Qwen 3.5 9B |
| :--- | :---: | :---: | :---: |
| **Attempt 1** (Lần đầu) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| **Attempt 2** | **13 (24.5%)** | 4 (7.7%) | 2 (3.9%) |
| **Attempt 3** | 6 (11.3%) | **14 (26.9%)** | 5 (9.8%) |
| **Attempt 4** | 9 (17.0%) | 7 (13.5%) | 3 (5.9%) |
| **Attempt 5** | 2 (3.8%) | 4 (7.7%) | 3 (5.9%) |
| ❌ **Thất bại (> 5 attempts)** | **23 (43.4%)** | **23 (44.2%)** | **38 (74.5%)** |

> [!NOTE]
> - Cả 3 mô hình đều **không vượt qua được ở Attempt 1 (0%)**, cho thấy khâu sinh Tool Call ban đầu luôn cần ít nhất 1 lượt sửa lỗi (Self-Correction / Feedback Loop) từ Executor.
> - **Qwen 3 8B** sửa lỗi nhanh nhất, tập trung pass ở **Attempt 2** (24.5%).
> - **Qwen 3 14B AWQ** thường sửa lỗi xong và pass ở **Attempt 3** (26.9%).

---

## 3. 📂 Kết Quả Theo Loại Slide (Per-Category Pass Rate)

| Thể loại Slide (Category) | Qwen 3 8B | Qwen 3 14B AWQ | Qwen 3.5 9B |
| :--- | :---: | :---: | :---: |
| **THANK_YOU_TOOLS** (Slide cảm ơn) | **6/6 (100%)** | 5/6 (83.3%) | 3/6 (50.0%) |
| **TRANSITION_TOOLS** (Slide chuyển tiếp) | **5/6 (83.3%)** | **5/6 (83.3%)** | 2/6 (33.3%) |
| **INTRO_TOOLS** (Slide giới thiệu/mở đầu) | **5/7 (71.4%)** | **5/7 (71.4%)** | 3/7 (42.9%) |
| **CONTENT_TOOLS** (Slide nội dung chính) | **12/21 (57.1%)** | 9/21 (42.9%) | 4/21 (19.0%) |
| **TEAM_TOOLS** (Slide đội ngũ) | 1/6 (16.7%) | **4/6 (66.7%)** | 0/6 (0.0%) |
| **CHART_TOOLS** (Slide biểu đồ) | 1/7 (14.3%) | 1/6 (16.7%) | 1/6 (16.7%) |

> [!IMPORTANT]
> - **TEAM_TOOLS**: Qwen 3 14B AWQ xử lý tốt hơn hẳn (66.7%) so với 8B (16.7%) và 3.5 9B (0%).
> - **CONTENT_TOOLS**: Qwen 3 8B áp đảo về khả năng sinh slide nội dung dài (57.1%).
> - **CHART_TOOLS**: Là nhóm khó nhất với cả 3 model, tỷ lệ pass đều rất thấp (~14-16%).

---

## 4. ⚠️ Phân Tích Các Loại Lỗi Phổ Biến (Error Breakdown)

| Mã lỗi (Error Type) | Qwen 3 8B | Qwen 3 14B AWQ | Qwen 3.5 9B |
| :--- | :---: | :---: | :---: |
| `EXTRA_ARGUMENT` *(Tham số bịa thừa)* | **447** | **245** | Phổ biến |
| `MISSING_REQUIRED_PARAM` *(Thiếu tham số bắt buộc)* | 126 | 101 | Phổ biến |
| `UNKNOWN_TOOL` *(Tên tool không tồn tại)* | 73 | 115 | Phổ biến |
| `Slide HTML tool returned empty content` | 8 | 6 | Ít gặp |
| `ITEM_TYPE_MISMATCH` / `TYPE_MISMATCH` | 14 | 6 | Ít gặp |
| `Image search count mismatch` *(Lỗi lệch số lượng ảnh)* | 10 | 6 | 3+ (Đặc biệt có case trả thừa >90 calls) |
| **Tổng số cờ lỗi (Total Error Flags)** | **690** | **485** | **> 600** |

> [!WARNING]
> - **`EXTRA_ARGUMENT`** là nguyên nhân lỗi lớn nhất ở tất cả các model (do model tự ý bịa thêm các trường như `logo_image_url`, `phone`...).
> - **Qwen 3 14B AWQ** ít mắc lỗi tham số bịa thừa hơn (245 lỗi) so với Qwen 3 8B (447 lỗi).

---

## 5. 💡 Kết Luận & Đánh Giá

1. **Về độ chính xác & Tỷ lệ Pass:** **Qwen 3 8B** cho tỷ lệ Pass cao nhất (**56.6%**), đặc biệt ở nhóm `CONTENT_TOOLS` và `THANK_YOU_TOOLS`.
2. **Về Hiệu năng & Tốc độ:** **Qwen 3 14B AWQ** là model tối ưu nhất về mặt **thời gian xử lý (86.4s)**, nhanh gấp đôi 8B mà vẫn giữ được tỷ lệ Pass tiệm cận (**55.8%**).
3. **Mô hình Qwen 3.5 9B:** Hoạt động kém hiệu quả trong bài test này (chỉ đạt **25.5%** pass và latency rất cao **351.59s**), gặp nhiều lỗi trả thừa search calls và suy luận lặp.
