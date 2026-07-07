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

## 1. Hướng dẫn tải mô hình (Download Model)

Chạy lệnh `uv` độc lập để tải mô hình **Qwen3-30B-A3B-Instruct-2507-AWQ** từ Hugging Face về thư mục `rl/model`:

```bash
uv run --no-project --python 3.12 --with huggingface-hub python3 -c "
from huggingface_hub import snapshot_download
import os

model_dir = '/home/MinhPV/SlideGenFunctionCalling/rl/model'
os.makedirs(model_dir, exist_ok=True)

print(f'Bắt đầu tải mô hình về {model_dir}...')
snapshot_download(
    repo_id='ELVISIO/Qwen3-30B-A3B-Instruct-2507-AWQ',
    local_dir=model_dir,
    ignore_patterns=['*.msgpack', '*.h5', '*.ot']
)
print('Tải thành công!')
"
```

---

## 2. Kiểm tra Local Inference

Xác minh tính đúng đắn của trọng số đã tải và sức tải của GPU bằng cách chạy kiểm tra cục bộ:

```bash
# 1. Cài đặt các thư viện cần thiết cho AWQ (nếu chưa có)
uv pip install autoawq transformers accelerate

# 2. Khởi chạy script test sinh JSON layout
python3 infer.py
```

---

## 3. Triển khai API Server bằng vLLM (Production & Generation)

Khởi động vLLM Server để phục vụ API OpenAI-Compatible tại cổng `8000`:

```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model /home/MinhPV/SlideGenFunctionCalling/rl/model \
    --quantization awq \
    --port 8000 \
    --trust-remote-code
```

---

## 4. Quy trình huấn luyện Agent với GRPO

Để tối ưu hóa tài nguyên VRAM trên một GPU duy nhất (tránh việc nạp mô hình Qwen hai lần song song), quy trình huấn luyện được thực hiện theo 3 bước tuần tự dưới đây. 

Mặc định, các script đã được tối ưu hóa để sử dụng mô hình nhỏ **Qwen/Qwen2.5-Coder-1.5B-Instruct (~1.5B/2B)** giúp bạn chạy thử nghiệm toàn bộ luồng huấn luyện cực kỳ nhẹ nhàng và nhanh chóng. Khi muốn huấn luyện mô hình 30B lớn, bạn chỉ cần thay đổi tham số chỉ định mô hình.

### Bước 4.1: Khởi động API Server phục vụ workflow
Mở một terminal riêng và chạy script để khởi động vLLM Server:

*   **Chạy thử mô hình nhỏ (1.5B - Mặc định):**
    ```bash
    cd rl
    ./serve_vllm.sh
    ```
*   **Chạy mô hình lớn (30B local đã tải ở Mục 1):**
    ```bash
    cd rl
    ./serve_vllm.sh local
    ```

### Bước 4.2: Chuẩn bị dữ liệu prompt đầu vào
Mở một terminal mới (vẫn giữ vLLM Server đang bật ở Bước 4.1):

*   **Cách A (Khuyên dùng - Tự động sinh dữ liệu tiếng Việt miễn phí):**
    ```bash
    cd rl
    python3 generate_synthetic_prompts.py
    ```
    *Script này sẽ truy vấn trực tiếp model đang chạy trên vLLM để tự sinh ra 200 mẫu prompt slide tiếng Việt chất lượng cao.*
*   **Cách B (Trích xuất từ file Docx có sẵn):**
    Cấu hình đường dẫn file Word mẫu của bạn trong `generate_dataset.py` và chạy:
    ```bash
    cd rl
    python3 generate_dataset.py
    ```

> [!IMPORTANT]
> **HÀNH ĐỘNG BẮT BUỘC:** Sau khi file `slidegen_rl_dataset.json` được lưu thành công ra đĩa, bạn phải **tắt vLLM Server** ở Bước 4.1 (ấn `Ctrl + C` trên terminal đó) để giải phóng hoàn toàn bộ nhớ GPU trước khi chạy lệnh train ở Bước 4.3.

### Bước 4.3: Khởi chạy huấn luyện GRPO
Tiến hành chạy huấn luyện tối ưu hóa Agent:

*   **Huấn luyện mô hình nhỏ (1.5B - Mặc định):**
    ```bash
    # Cài đặt thư viện (nếu chưa có)
    uv pip install trl peft
    
    # Chạy train
    python3 train.py
    ```
*   **Huấn luyện mô hình lớn (30B local đã tải ở Mục 1):**
    ```bash
    # Cấu hình biến môi trường trỏ vào model 30B
    export TRAINING_MODEL_ID="./model"
    
    # Chạy train
    python3 train.py
    ```

Sau khi hoàn tất, trọng số tối ưu nhất sẽ được lưu tại thư mục `./qwen3_slidegen_grpo`. Bạn chỉ cần khởi động lại vLLM trỏ vào thư mục này để đưa Agent đã tinh chỉnh vào chạy chính thức cho Backend.
