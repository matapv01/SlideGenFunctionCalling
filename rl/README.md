# Serving & Huấn luyện Agent (RL/GRPO) - SlideGen

Thư mục này chứa toàn bộ tài nguyên, mã nguồn kiểm thử và huấn luyện Agent phục vụ sinh slide (Function Calling) chạy hoàn toàn offline bằng Học tăng cường (Reinforcement Learning / GRPO).

---

## 🚀 Chiến lược Huấn luyện Agent (RL Strategy)

Hệ thống được thiết kế theo các chiến lược kỹ thuật hiện đại nhằm tối ưu hóa chất lượng thiết kế slide của Agent dựa trên phản hồi thẩm mỹ:

### 1. Đồng bộ Ngữ cảnh Workflow (Workflow-Aware Prompts)
Để Agent học được cách phối hợp với toàn bộ hệ thống SlideGen (Planning Node, FAISS Tool Retriever), dữ liệu prompt đưa vào huấn luyện không phải là văn bản thô cô lập. 
*   **Chiến lược:** Trong pha tạo dữ liệu, văn bản thô được chạy thử qua các node **Lập kế hoạch** và **Truy xuất FAISS** để đóng gói thành một prompt hoàn chỉnh chứa đầy đủ: *Quy định layout hệ thống, Kế hoạch thiết kế slide, và Danh sách 5 tools gợi ý từ FAISS*.
*   Mô hình Qwen3 sẽ học cách đưa ra lựa chọn gọi Layout Tool tốt nhất dựa trên đúng ngữ cảnh này.

### 2. Chiến lược Đa phần thưởng (Multi-Reward Strategy)
Để ngăn ngừa lỗi **Trục lợi phần thưởng (Reward Hacking)** – hiện tượng mô hình cố tình xóa bớt chữ, cắt ngắn nội dung để slide trông sạch sẽ nhằm đạt điểm thẩm mỹ cao từ ViT – hệ thống sử dụng kết hợp 2 hàm thưởng:
*   **Aesthetic Reward (Thẩm mỹ - ViT Model):** Chụp ảnh slide HTML bằng Playwright và chấm điểm dựa trên mô hình học sâu ViT Pairwise (`best_model_pairwise.pt`) để tối ưu bố cục và màu sắc.
*   **Content Preservation Reward (Nội dung - NLP Rule):** 
    *   Phạt điểm `0` lập tức nếu Generator sinh ra JSON lỗi hoặc không gọi tool.
    *   Tính tỷ lệ bảo tồn từ khóa tiếng Việt chính giữa văn bản gốc và slide sinh ra.
    *   Áp dụng hình phạt độ dài (Length Penalty) nếu Agent cố tình cắt xén nội dung quá 30%.
*   *Điểm tối ưu tổng hợp = Điểm thẩm mỹ × Điểm bảo tồn nội dung.*

### 3. Quy trình Tiết kiệm VRAM (Decoupled VRAM Pipeline)
Mô hình MoE Qwen3-30B ngốn rất nhiều tài nguyên đồ họa. Để tránh lỗi **CUDA Out Of Memory** do nạp mô hình song song 2 lần (một lần trên vLLM để render, một lần trong PyTorch để train), quy trình được chia nhỏ thành các bước tuần tự (Xem Mục 4).

### 4. Dữ liệu huấn luyện thuần Việt (Vietnamese Localization)
Mọi prompt sinh ra tự động đều được giới hạn ở **tiếng Việt 100%** và xoay quanh các chủ đề thân thuộc với người dùng Việt Nam (Lịch sử Việt Nam, Doanh nghiệp Việt Nam như VinFast, FPT, Du lịch & Địa lý Việt Nam).

---

## 1. Cơ chế tải mô hình (Hugging Face Hub Direct Loading)

Hệ thống đã được cấu hình để nạp mô hình trực tiếp từ Hugging Face Hub. Khi bạn chạy kịch bản phục vụ API hoặc huấn luyện lần đầu tiên, thư viện sẽ tự động tải các file trọng số về máy và lưu vào thư mục cache mặc định (`~/.cache/huggingface/hub`). 

Bạn **không cần** chạy bất kỳ script tải mô hình thủ công nào nữa!

---

## 2. Kiểm tra Local Inference trực tiếp từ Hugging Face

Bạn có thể chạy thử tính năng sinh Layout (Function Calling) trực tiếp bằng mô hình trên Hugging Face để xác minh GPU và môi trường chạy:

```bash
# 1. Cài đặt các thư viện cần thiết cho mô hình (nếu chưa có)
uv pip install autoawq transformers accelerate playwright

# 2. Tải trình duyệt Chromium cho Playwright (bắt buộc để chụp ảnh slide chấm điểm thẩm mỹ)
uv run playwright install chromium

# 3. Chạy thử nghiệm với mô hình 0.5B mặc định (Hugging Face tự tải về)
uv run python3 infer.py

# Hoặc chạy thử nghiệm với mô hình Qwen3.6 35B lớn:
export TRAINING_MODEL_ID="Qwen/Qwen3.6-35B-A3B"
uv run python3 infer.py
```

---

## 3. Triển khai API Server bằng vLLM (Production & Generation)

vLLM hỗ trợ nạp trực tiếp mô hình từ Hugging Face repo ID và tự động lưu cache. Chạy lệnh sau để khởi động vLLM Server:

*   **Chạy mô hình nhỏ (0.5B - Mặc định):**
    ```bash
    uv run python3 -m vllm.entrypoints.openai.api_server \
        --model Qwen/Qwen2.5-Coder-0.5B-Instruct \
        --port 8008 \
        --trust-remote-code
    ```
*   **Chạy mô hình lớn (35B):**
    ```bash
    uv run python3 -m vllm.entrypoints.openai.api_server \
        --model Qwen/Qwen3.6-35B-A3B \
        --port 8008 \
        --trust-remote-code
    ```

---

## 4. Quy trình huấn luyện Agent với GRPO

Để tối ưu hóa tài nguyên VRAM trên một GPU duy nhất (tránh việc nạp mô hình Qwen hai lần song song), quy trình huấn luyện được thực hiện theo 3 bước tuần tự dưới đây. 

Mặc định, các script đã được tối ưu hóa để sử dụng mô hình nhỏ **Qwen/Qwen2.5-Coder-0.5B-Instruct (~0.5B)** giúp bạn chạy thử nghiệm toàn bộ luồng huấn luyện cực kỳ nhẹ nhàng và nhanh chóng. Khi muốn huấn luyện mô hình 30B lớn, bạn chỉ cần thay đổi tham số chỉ định mô hình.

### Bước 4.1: Khởi động API Server phục vụ workflow
Mở một terminal riêng và chạy script để khởi động vLLM Server:

*   **Chạy thử mô hình nhỏ (0.5B - Mặc định):**
    ```bash
    cd rl
    ./serve_vllm.sh
    ```
*   **Chạy mô hình lớn (35B trực tiếp từ Hugging Face):**
    ```bash
    cd rl
    ./serve_vllm.sh Qwen/Qwen3.6-35B-A3B
    ```

### Bước 4.2: Chuẩn bị dữ liệu prompt đầu vào
Mở một terminal mới (vẫn giữ vLLM Server đang bật ở Bước 4.1):

*   **Cách A (Khuyên dùng - Tự động sinh dữ liệu tiếng Việt miễn phí):**
    ```bash
    cd rl
    uv run python3 generate_synthetic_prompts.py
    ```
    *Script này sẽ truy vấn trực tiếp model đang chạy trên vLLM để tự sinh ra 200 mẫu prompt slide tiếng Việt chất lượng cao.*
*   **Cách B (Trích xuất từ file Docx có sẵn):**
    Cấu hình đường dẫn file Word mẫu của bạn trong `generate_dataset.py` và chạy:
    ```bash
    cd rl
    uv run python3 generate_dataset.py
    ```

> [!IMPORTANT]
> **HÀNH ĐỘNG BẮT BUỘC:** Sau khi file `slidegen_rl_dataset.json` được lưu thành công ra đĩa, bạn phải **tắt vLLM Server** ở Bước 4.1 (ấn `Ctrl + C` trên terminal đó) để giải phóng hoàn toàn bộ nhớ GPU trước khi chạy lệnh train ở Bước 4.3.

### Bước 4.3: Khởi chạy huấn luyện GRPO
Tiến hành chạy huấn luyện tối ưu hóa Agent. 

Kịch bản hỗ trợ cấu hình linh hoạt thông qua các biến môi trường:
*   `LIMIT_GPU_MEM` (Mặc định không giới hạn): Giới hạn lượng VRAM tối đa PyTorch được phép sử dụng trên GPU (ví dụ: `"4GiB"`, `"6GiB"`), phần còn lại của mô hình sẽ tự động được **offload sang RAM thường (CPU)**.
*   `USE_CPU` (Mặc định `False`): Đặt `True` để ép chạy hoàn toàn trên CPU (tiêu tốn **0 MB VRAM**).
*   `USE_LORA` (Mặc định `True`): Sử dụng kỹ thuật tối ưu hóa trọng số thấp (PEFT LoRA). Đặt `False` để chạy Full-Parameter Fine-Tuning.
*   `USE_GRAD_CHECKPOINT` (Mặc định `True`): Sử dụng Gradient Checkpointing để tiết kiệm VRAM. Đặt `False` trên các GPU mạnh như H100 để tăng ~30% tốc độ huấn luyện.

Lựa chọn cách chạy phù hợp với GPU của bạn:

*   **Cách A: Chạy trên GPU hạn chế VRAM (như RTX 3090/4090 - Mặc định):**
    ```bash
    # 1. Cài đặt các thư viện cần thiết & Playwright (nếu chưa có)
    uv pip install trl peft playwright
    
    # 2. Tải trình duyệt Chromium cho Playwright (bắt buộc để chụp ảnh slide chấm điểm)
    uv run playwright install chromium
    
    # 3. Chạy huấn luyện (sẽ tự động dùng LoRA + Gradient Checkpointing để chỉ tốn ~6GB VRAM)
    # Mẹo: Bạn có thể đặt LIMIT_GPU_MEM để ép offload bớt sang CPU nếu GPU quá đầy (ví dụ: limit 3GB VRAM)
    export LIMIT_GPU_MEM="3GiB"
    uv run python3 train.py
    ```

*   **Cách B: Chạy trên GPU cao cấp (H100/A100) để tối ưu chất lượng & hiệu suất cao nhất:**
    ```bash
    # 1. Cài đặt các thư viện cần thiết & Playwright (nếu chưa có)
    uv pip install trl peft playwright
    
    # 2. Tải trình duyệt Chromium cho Playwright
    uv run playwright install chromium
    
    # 3. Thiết lập biến môi trường: Tắt LoRA để chạy Full Fine-Tuning và tắt Gradient Checkpointing để tăng tốc
    export USE_LORA="False"
    export USE_GRAD_CHECKPOINT="False"
    
    # Nếu muốn dùng mô hình 35B lớn của Hugging Face:
    export TRAINING_MODEL_ID="Qwen/Qwen3.6-35B-A3B"
    
    # 4. Khởi chạy huấn luyện
    uv run python3 train.py
    ```

*   **Cách C: Phương án chống cháy - Chạy hoàn toàn trên CPU (Không tốn VRAM GPU):**
    Nếu GPU của bạn hoàn toàn bị chiếm dụng bởi các tiến trình khác và bạn không thể giải phóng VRAM, bạn có thể ép toàn bộ chương trình chạy trên CPU:
    ```bash
    # 1. Tải trình duyệt cho Playwright (bản Chromium)
    uv run playwright install chromium
    
    # 2. Thiết lập biến môi trường chạy trên CPU
    export USE_CPU="True"
    
    # 3. Khởi chạy huấn luyện
    uv run python3 train.py
    ```

Sau khi hoàn tất, trọng số tối ưu nhất sẽ được lưu tại thư mục `./qwen3_slidegen_grpo`. Bạn chỉ cần khởi động lại vLLM trỏ vào thư mục này để đưa Agent đã tinh chỉnh vào chạy chính thức cho Backend.
