# 📊 Báo Cáo So Sánh Benchmark Sau Nâng Cấp (Qwen 3 8B vs Qwen 3 14B AWQ)

Tài liệu này tổng hợp và phân tích chi tiết kết quả benchmark mới nhất của **Qwen 3 8B** và **Qwen 3 14B AWQ** trên 50 samples đầu tiên (start0 -> end49) sau khi áp dụng các cải tiến:
1. **Native Function Calling qua vLLM / Remote FastAPI Server**
2. **Cơ chế Actionable Feedback Loop thay thế `default_fallback`**
3. **Nâng giới hạn số lần sửa lỗi tối đa lên 10 Attempts (`EXECUTOR_MAX_RETRIES=10`)**

---

## 1. 🎯 Bảng So Sánh Tổng Quan (Benchmark Summary)

| Chỉ số (Metric) | 🥇 **Qwen 3 8B (New)** | 🥈 **Qwen 3 14B AWQ (New)** | Đánh giá & Chênh lệch |
| :--- | :---: | :---: | :--- |
| **Tổng số Sample test** | **50** | **50** | Đồng bộ 50 samples |
| **Pass Rate (Tỷ lệ vượt qua)** | **100.0%** (50/50) 🎉 | **100.0%** (50/50) 🎉 | **Hoàn hảo 100% ở cả 2 model** |
| **First-Try Pass (Vượt qua lần 1)** | **50.0%** (25/50) 🚀 | **24.0%** (12/50) | **Qwen 3 8B vượt trội gấp 2.1 lần** |
| **Tool Name Match (Khớp Tool GT)** | **6.0%** (3/50) | **14.0%** (7/50) 🎯 | **14B AWQ khớp chuẩn hơn gấp 2.3 lần** |
| **Trung bình số lượt thử (Avg Attempts)** | **1.80 lượt** ⚡ | **2.22 lượt** | **8B sửa lỗi nhanh hơn** |
| **Thời gian phản hồi TB (Avg Latency)** | **88.8s** | **91.1s** | Tương đương (~88s - 91s) |
| **Tổng số cờ lỗi (Total Errors)** | **43 lỗi** 📉 | **70 lỗi** | **8B ít lỗi hơn 38.5%** |

> [!TIP]
> **Điểm đột phá:**
> - Tỷ lệ **Pass Rate nhảy vọt từ ~56% lên tuyệt đối 100.0%** trên cả 2 model nhờ cơ chế Actionable Feedback và tăng Attempt lên 10.
> - **First-Try Pass Rate:** Trước đây là **0.0%**, nay **Qwen 3 8B đạt tới 50.0%** (một nửa số slide pass ngay từ lần đầu tiên mà không cần sửa lỗi!).

---

## 2. 🔄 Phân Bố Số Lượt Thử (Attempts Breakdown)

| Số lần thử (Attempt) | Qwen 3 8B (New) | Qwen 3 14B AWQ (New) | So sánh xu hướng |
| :--- | :---: | :---: | :--- |
| **Attempt 1 (Lần đầu)** | **25/50 (50.0%)** | 12/50 (24.0%) | 8B vượt trội ở lượt đầu |
| **Attempt 2** | 17/50 (34.0%) | **25/50 (50.0%)** | 14B AWQ tập trung pass ở lần 2 |
| **Attempt 3** | 6/50 (12.0%) | 9/50 (18.0%) | Cả 2 đều xử lý xong >90% ở attempt 3 |
| **Attempt 4** | 1/50 (2.0%) | 1/50 (2.0%) | Số lượng rất ít |
| **Attempt 5** | 0/50 (0.0%) | 1/50 (2.0%) | — |
| **Attempt 6 -> 7** | 0/50 (0.0%) | 2/50 (4.0%) | 14B có 2 case cần retry sâu |
| **Attempt 8** | 1/50 (2.0%) | 0/50 (0.0%) | 8B có 1 case cần 8 lượt |
| **Attempt 9 -> 10** | 0/50 (0.0%) | 0/50 (0.0%) | Không có sample nào chạm trần |
| ❌ **Thất bại (> 10 attempts)** | **0/50 (0.0%)** | **0/50 (0.0%)** | **0% thất bại** |

> [!NOTE]
> - **Tỷ lệ Pass tích lũy đến Attempt 2:**
>   - **Qwen 3 8B:** Đạt **84.0%** (42/50 samples).
>   - **Qwen 3 14B AWQ:** Đạt **74.0%** (37/50 samples).
> - **Tích lũy đến Attempt 3:** Cả 2 model đều đạt tỷ lệ hoàn thành $\ge$ **92% - 96%**.

---

## 3. 📂 Kết Quả Theo Từng Nhóm Slide (Per-Category Breakdown)

Cả 2 mô hình đều đạt tỷ lệ hoàn thành **100%** trên tất cả 6 nhóm slide:

| Thể loại Slide (Category) | Qwen 3 8B (New) | Qwen 3 14B AWQ (New) |
| :--- | :---: | :---: |
| **CHART_TOOLS** (Biểu đồ) | **6/6 (100.0%)** | **6/6 (100.0%)** |
| **CONTENT_TOOLS** (Nội dung chính) | **19/19 (100.0%)** | **19/19 (100.0%)** |
| **INTRO_TOOLS** (Mở đầu) | **7/7 (100.0%)** | **7/7 (100.0%)** |
| **TEAM_TOOLS** (Đội ngũ) | **6/6 (100.0%)** | **6/6 (100.0%)** |
| **THANK_YOU_TOOLS** (Cảm ơn) | **6/6 (100.0%)** | **6/6 (100.0%)** |
| **TRANSITION_TOOLS** (Chuyển tiếp) | **6/6 (100.0%)** | **6/6 (100.0%)** |

> [!IMPORTANT]
> Nhóm **CHART_TOOLS** (trước đây chỉ đạt ~14-16% pass rate) nay đã đạt **100% Pass** nhờ khả năng sửa lỗi tham số dữ liệu biểu đồ qua các lượt retry tiếp theo!

---

## 4. ⚠️ Phân Tích Các Loại Lỗi (Error Breakdown)

| Mã lỗi (Error Flag) | Qwen 3 8B (New) | Qwen 3 14B AWQ (New) | Nhận xét |
| :--- | :---: | :---: | :--- |
| `UNKNOWN_TOOL` *(Chọn tool ngoài candidate)* | **13** | **30** | 14B AWQ hay bị chọn nhầm tool hơn |
| `EXTRA_ARGUMENT` *(Bịa thêm tham số ngoài schema)* | **0** 🎉 | **14** | **8B đã triệt tiêu 100% lỗi bịa tham số** |
| `Slide HTML tool returned empty content` | 5 | 7 | Render lỗi nhẹ, được fix ngay ở lần sau |
| `ITEM_TYPE_MISMATCH` / `TYPE_MISMATCH` | 5 | 0 | 14B AWQ chuẩn kiểu dữ liệu hơn |
| `MISSING_TOOL_CALL_TAGS` / `INVALID_SYNTAX` | 3 | 2 | Thiếu/sai thẻ tool_call (hiếm gặp) |
| `Image search count mismatch` *(Lệch số lượng ảnh)* | 7 | 7 | Thiếu gọi `search_ddgs_images` ở lần 1 |
| **TỔNG SỐ LỖI (TOTAL ERRORS)** | **43** | **70** | **Qwen 3 8B ổn định hơn rõ rệt** |

> [!WARNING]
> - **Điểm sáng nhất:** Lỗi **`EXTRA_ARGUMENT`** trên **Qwen 3 8B đã giảm từ 447 lỗi về đúng con số 0**!
> - Lỗi chủ yếu còn lại là `UNKNOWN_TOOL` ở Attempt 1 khi model ưu tiên chọn layout quen thuộc hơn danh sách 5 tools được gợi ý, nhưng được sửa ngay ở Attempt 2 sau khi nhận feedback.

---

## 5. 💡 So Sánh Trước và Sau Nâng Cấp (Before vs After)

| Chỉ số | Qwen 3 8B (Cũ) | 🚀 **Qwen 3 8B (Mới)** | Qwen 3 14B (Cũ) | 🚀 **Qwen 3 14B (Mới)** |
| :--- | :---: | :---: | :---: | :---: |
| **Pass Rate** | 56.6% | **100.0%** (+43.4%) | 55.8% | **100.0%** (+44.2%) |
| **First-Try Pass** | 0.0% | **50.0%** (+50.0%) | 0.0% | **24.0%** (+24.0%) |
| **Avg Attempts** | 3.87 | **1.80** (Giảm hơn 2 lần) | 4.10 | **2.22** (Giảm gần 2 lần) |
| **Avg Latency** | 169.1s | **88.8s** (Nhanh gấp 2) | 86.4s | **91.1s** (Duy trì tối ưu) |
| **Tổng số lỗi** | 690 lỗi | **43 lỗi** (Giảm 93.8%) | 485 lỗi | **70 lỗi** (Giảm 85.5%) |

---

## 6. 🏆 Kết Luận & Khuyến Nghị

1. **Model xuất sắc toàn diện nhất:** **Qwen 3 8B**
   - Đạt **50% First-Try Pass** (cứ 2 slide thì có 1 slide pass ngay lần đầu).
   - Số lượt thử trung bình thấp nhất (**1.80 attempts**).
   - Tốc độ xử lý nhanh (**88.8s**).
   - **Hoàn toàn sạch bóng lỗi `EXTRA_ARGUMENT`**.

2. **Model có khả năng chọn đúng Tool gốc cao nhất:** **Qwen 3 14B AWQ**
   - Đạt **14.0% Tool Name Match** (cao hơn gấp 2.3 lần so với 8B), thể hiện khả năng hiểu ngữ cảnh nội dung sâu sắc hơn để chọn đúng tool ground truth ban đầu.

3. **Cải tiến Feedback Loop & Native Calling cực kỳ thành công:**
   - Việc loại bỏ `default_fallback` và bổ sung thông điệp lỗi rõ ràng giúp tỷ lệ thành công của cả pipeline đạt mức tuyệt đối **100%**.
