# Bàn giao SlideGen DAPO sang máy RTX 5880 (prompt cho Claude)

Dán nguyên phần dưới đây làm tin nhắn đầu tiên cho Claude Code trên máy mới.

---

Bạn tiếp tục dự án nghiên cứu SlideGen DAPO (paper nhắm A*). Trả lời tôi bằng tiếng Việt, tự quyết dựa trên số liệu và ảnh thật, báo mọi quyết định kèm lý do và số liệu. Không in giá trị token ra màn hình, không đưa credential vào URL, không commit `.env`, `slidegen_data/`, checkpoint. Repo GitHub `matapv01/SlideGenFunctionCalling` là **công khai**.

## Bối cảnh (đã xong trên H100, không chạy lại)

- Model: Qwen3.5-35B-A3B + LoRA DAPO. Bản chốt = round 4, seed 42, checkpoint-175 (HF `mata01/Qwen3.5-35B-A3B-SlideGen-DAPO`, thư mục `round4/`). Không cần tải checkpoint: mọi output của nó đã có sẵn.
- Paper chỉ có 3 đóng góp: (1) dữ liệu 1.929 cặp slide đẹp–xấu gán tay + reward ViT, (2) pipeline SlideGen + thư viện XML, (3) train DAPO. Các sửa môi trường/reward là chi tiết, KHÔNG đưa vào paper như đóng góp.
- Báo cáo đầy đủ, đọc trước tiên: `BAO_CAO_DAPO.md` (nhánh `minh/rl`), và `experiments/2026-10-14-dapo-round4-keypoint-three-seeds/RESULTS.md`.
- Kết quả chính:
  - Tập test giữ riêng `testset_v2` (337 slide, chạy một lần, T=0.3): slide dùng được base 90,2% -> DAPO 94,7%; lỗi nhìn thấy 4,7% -> 3,0%; keypoint 0,811 -> 0,788. Best-of-4 (T=1.0): base 97,0% ≈ DAPO 97,3%.
  - Tập phát triển (291 slide), 3 seed: lỗi nhìn thấy 7,6% -> 4,6% ± 0,7. Xác suất người chọn dự đoán 0,507 ± 0,008 (chưa có ý nghĩa).
  - Reward thẩm mỹ: bộ cặp nhân tạo ViT 97,9%, VLM 35B zero-shot 97,4%, CLIP 47,9%; trên slide do model sinh có người chấm: ViT 60,4%, reward 69,8%, VLM 71,6% (thẩm mỹ).
  - Gemini cũ (vòng 1, prompt cũ, T=1.0) trên tập dev: keypoint 0,858 nhưng cắt chữ 15,8%; so sánh chưa công bằng.

## Bước 1: khôi phục tối thiểu (không cần GPU lớn)

```bash
git clone -b minh/rl https://github.com/matapv01/SlideGenFunctionCalling.git && cd SlideGenFunctionCalling
# .env: tôi sẽ tự tạo, gồm HF_TOKEN, GITHUB_TOKEN, VERCEL_TOKEN, GEMINI_API_KEY (key mới). Kiểm tra dòng đầu .env đúng dạng KEY=value.
```

- Môi trường Python: dùng `uv` theo `pyproject.toml`/`uv.lock` (`uv sync --locked`); trình duyệt render: `uv run playwright install chromium`; frontend: `cd frontend && npm ci && npm run build` (renderer dùng `frontend/dist` qua backend).
- Chạy renderer: `uv run uvicorn backend.api.app:app --host 127.0.0.1 --port 12008` trong tmux, kiểm tra `curl 127.0.0.1:12008/health`.
- Chỉ tải từ HF dataset riêng tư `mata01/SlideGen-data` những gì cần (dùng `huggingface_hub.snapshot_download(..., allow_patterns=[...])`, token từ env, đặt vào `slidegen_data/` và `models/`):
  - `models/vit/best_model_pairwise.pt` (reward ViT, chép vào `models/vit/`)
  - `testset_v2/eval_rows_r4.json`, `testset_v2/wiki_testset_*.json`, `testset_v2/outputs/*.jsonl`, `testset_v2/scored_final/*.jsonl`
  - `testset/eval_rows_r4.json`, `testset/outputs/*.jsonl`, `testset/scored_r4/*.jsonl`, `testset/wiki_testset_*.json`
  - `annotation/ratings.json`, `annotation/secret_mapping.json`, `annotation/report/*` (bảng ánh xạ bí mật: chỉ để phân tích, KHÔNG deploy, KHÔNG push)
  - `pairs/*` (bộ cặp + `baselines.json`)
  - Không tải `anh_slide/`, ảnh `png/`, checkpoint, model Qwen.
- Ảnh render có thể tạo lại bằng lệnh `score` (không cần ảnh cũ).

## Bước 2: Gemini 3.5 Flash trên tập test giữ riêng (công bằng với DAPO)

- `scripts/testset_generate.py gemini` hiện cố định temperature 1.0 trong `_gemini_call`. Thêm tham số `--temperature` (truyền vào `generationConfig`), giữ mặc định 1.0.
- Dùng đúng prompt vòng 4 (gợi ý sức chứa đã nằm trong `eval_rows_r4.json`, không thêm `--capacity-hints`):
  ```bash
  export TESTSET_DIR=testset_v2 TESTSET_ROWS=eval_rows_r4.json RL_HL_QUOTED=true RL_CAPACITY_FILE=rl/data/tool_text_capacity_v2_joint.json
  uv run python scripts/testset_generate.py gemini --temperature 0.3 --samples 1 --output gemini_final_t03.jsonl
  uv run python scripts/testset_generate.py gemini --temperature 1.0 --samples 4 --output gemini_final_t10.jsonl
  export TESTSET_SCORED_DIR=scored_final RL_FOREIGN_TEXT_CHECK=true RL_LENIENT_JSON=true RL_REWARD_RENDER_WORKERS=8
  uv run python scripts/testset_generate.py score --systems gemini_final_t03
  uv run python scripts/testset_generate.py score --discard-png --systems gemini_final_t10
  ```
  Key Gemini gửi qua header `x-goog-api-key` (code đã làm vậy); nếu lỗi 403 spend cap thì báo tôi.
- Bảng: `uv run python scripts/dev_eval_table.py base=../testset_v2/scored_final/base_final_t03 dapo=../testset_v2/scored_final/dapo_final_t03 gemini=../testset_v2/scored_final/gemini_final_t03 base_b4=../testset_v2/scored_final/base_final_t10:4 dapo_b4=../testset_v2/scored_final/dapo_final_t10:4 gemini_b4=../testset_v2/scored_final/gemini_final_t10:4`, và `scripts/predicted_preference.py ../testset_v2/scored_final base_final_t03 dapo_final_t03 gemini_final_t03`.
- Xem ảnh thật: lấy 12 slide ngẫu nhiên + các slide khác trạng thái lỗi giữa Gemini và DAPO, ghép cạnh nhau, đọc ảnh rồi mới kết luận.

## Bước 3: chấm người đợt 2 trên Vercel

- Sửa `scripts/build_annotation_set.py` cho đợt 2 (hiện viết cho vòng 1: thư mục `testset`, hệ thống `best8`): nguồn `slidegen_data/testset_v2/scored_final`, hệ thống `dapo_final_t03` (sample 0), `base_final_t03`, `base_best4` (base_final_t10 chọn bằng reward), `gemini_final_t03`.
- So sánh: DAPO vs base, DAPO vs base best-of-4, DAPO vs Gemini; khoảng 400 cặp không hòa mỗi so sánh (tỉ lệ hòa vòng 1 là 34–60%, nên lấy đủ cặp). 3 người chấm, ~5% cặp kiểm tra chú ý.
- Sửa giao thức trong `annotation_web/public/app.js`: tiêu chí tổng thể bắt buộc chọn A hoặc B (bỏ "ngang nhau" ở tiêu chí này), đặt thời gian tối thiểu mỗi cặp (ví dụ 15 giây), viết lại câu hỏi đầy đủ/trung thực cho rõ (độ đồng thuận vòng 1 chỉ 0,13–0,14).
- Ảnh cặp: upload lên HF dataset `mata01/slidegen-human-eval-images` (tên file ngẫu nhiên), `pairs.json`/`assignments.json` vào `annotation_web/public/data/`. Tạo mã người chấm mới và `ADMIN_TOKEN` mới, đặt bằng Vercel env (không commit), lưu bản riêng vào `slidegen_data/annotation/credentials.json`.
- Deploy: `npx vercel --cwd annotation_web deploy --prod --yes --token "$VERCEL_TOKEN"`. Kiểm tra trang chạy, đăng nhập thử bằng một mã, chấm thử một cặp rồi xóa.
- Lấy kết quả qua `api/export` (header `x-admin-token`), phân tích bằng `scripts/analyze_annotations.py` (sửa cho đợt 2): tỉ lệ thắng có CI bootstrap theo bộ slide, độ đồng thuận, kiểm tra chú ý, tốc độ chấm.

## Bước 4: paper

- Đọc `BAO_CAO_DAPO.md` và skill `/data/ai-research-skill` (nếu có trên máy, nếu không thì clone `github.com/matapv01/ai-research-skill`) trước khi viết.
- Khung: Introduction (3 đóng góp), Dataset (bộ cặp + baselines CLIP/VLM/ViT, và độ khớp người trên slide do model sinh), System (pipeline + thư viện XML), Method (DAPO, reward tổng hợp), Experiments (tập test giữ riêng, base/DAPO/Gemini, best-of-4, 3 seed, chấm người đợt 2), Analysis (ví dụ ảnh), Limitations, Ethics.
- Phải nói thẳng: best-of-4 của base ngang DAPO best-of-4 (RL giảm chi phí suy luận, chưa nâng trần); keypoint giảm 0,02; reward thẩm mỹ khớp người chỉ 60–72% trên slide thật; tập phát triển đã dùng để chọn checkpoint. Kết luận về sở thích người dựa vào chấm người đợt 2, không dựa vào xác suất dự đoán.
- Mọi số trong paper sinh bằng script từ file kết quả; base model luôn là hàng đầu.

## Nếu sau chấm người cần train thêm (cần GPU lớn, không làm trên 5880)

Ghi lại đề xuất cho lần thuê GPU sau: chưng cất VLM vào ViT hoặc tinh chỉnh ViT trên slide do model sinh có người chấm; phạt thẩm mỹ thấp bằng phép nhân (slide cảm ơn 18 ô có ViT 0,07 nhưng reward 5,04); xử lý lỗi vượt số mục tối đa của layout.
