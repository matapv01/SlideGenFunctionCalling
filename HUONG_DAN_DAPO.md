# Hướng dẫn: train DAPO SlideGen, sinh slide tập test, chấm người, phân tích

Tài liệu này mô tả toàn bộ quy trình đã dùng cho run cuối `final_v3_20261005`, theo thứ tự thực hiện.

## 0. Tài nguyên

| Thứ | Ở đâu |
|---|---|
| Code | GitHub `matapv01/SlideGenFunctionCalling`, nhánh `minh/rl` |
| Adapter LoRA tốt nhất (step 150) + checkpoint 150/225/250 + metric + ảnh mẫu | HF model (riêng tư) `mata01/Qwen3.5-35B-A3B-SlideGen-DAPO` |
| Ảnh slide blind cho người chấm | HF dataset (công khai) `mata01/slidegen-human-eval-images` |
| Trang chấm | https://slidegen-annotation.vercel.app (Vercel project `slidegen-annotation`, Postgres Neon) |
| Dữ liệu cặp slide gán tay (reward model) | Kaggle `pvmkt1/data-rewardmodel-slidegen` → `slidegen_data/` (không push) |
| Metric, cấu hình, bảng điểm tập test của run cuối | `rl/runs/final_v3_20261005/` |

Không bao giờ commit: `.env`, `slidegen_data/` (gồm `annotation/secret_mapping.json` và `annotation/credentials.json`), thư mục run `qwen3_*`.

## 1. Môi trường (container H100)

Mọi thứ cần giữ nằm trên `/data`: `/data/hf_cache`, `/data/venvs/qwen35` (transformers 5.17 + TRL 1.7.1), `/data/venvs/kernels*` (flash-linear-attention, causal-conv1d, tilelang), `/data/playwright`, `/data/uv_cache`, `/data/tools/node-v22.11.0-linux-x64`.

Sau khi container khởi động lại: `bash /data/claude_backup/restore.sh` (xem `/data/claude_backup/README_KHOI_PHUC.md`). Script cài lại tmux/rsync, thư viện Chromium và bật renderer ở cổng 12008.

`.env` cần: `HF_TOKEN`, `GEMINI_API_KEY`, `LLM_API_KEY`, `GITHUB_TOKEN`, `VERCEL_TOKEN`, `KAGGLE`, `REWARD_MODEL_DEVICE`, `EMBEDDING_DEVICE`.

## 2. Train DAPO

```bash
tmux new -s qwen35-dapo-content
bash rl/runs/final_v3_20261005/launch.sh        # sửa GRPO_OUTPUT_DIR nếu chạy run mới
GRPO_RESUME=true bash <run_dir>/launch.sh        # tiếp tục sau khi bị ngắt
python3 <run_dir>/status.py                      # tình trạng, eval mới nhất, cảnh báo
```

- Cấu hình: QLoRA NF4 (expert MoE giữ BF16), LoRA r16 trên q/k/v/o + gate/up/down, `loss_type=dapo`, 4 mẫu/prompt, grad accumulation 16, LR 1e-5, temperature 1.0, top-p 0.95, eval/save mỗi 25 bước, early stopping patience 4.
- Reward (`rl/rewards/composite_reward.py`) = (0.5·lexical + 0.7·semantic + 1.0·numeric_fact + 1.5·dom + 1.0·aesthetic(ViT) + 0.25·image_loaded) × language; output không hợp lệ = −2.
- Sửa bất kỳ file `rl/*.py`, `rl/rewards`, `backend/workflows` sẽ đổi training contract và chặn resume; script phụ đặt trong `scripts/`.
- Sau khi train: `python scripts/export_run_metrics.py <run_dir> <run_dir>/metrics` (cần matplotlib: `PYTHONPATH=/data/venvs/plot`), `python scripts/sample_grid.py <run_dir>/samples --steps 0,150,250`.
- Bước nạp lại checkpoint tốt nhất ở cuối train lỗi do PEFT 0.19.1 + transformers 5.17 (`WeightConverter ... distributed_operation`); không ảnh hưởng: checkpoint đã lưu đầy đủ. Muốn nạp adapter thì dùng `GRPO_INIT_ADAPTER=<checkpoint>` (copy trọng số theo tên).

## 3. Tập test (Wikipedia tiếng Việt, chủ đề không trùng tập train)

```bash
python scripts/build_wiki_testset.py slidegen_data/testset/wiki_articles.json slidegen_data/testset/wiki_testset_rows.json
# lập kế hoạch + duyệt ảnh bằng pipeline thật (tự tiếp tục nếu lỗi)
./.uv/uv run --locked python scripts/rebuild_grpo_corpus.py --source slidegen_data/testset/wiki_testset_rows.json \
    --output slidegen_data/testset/wiki_testset_planned.json --asset-dir static/output/wiki_test_image_cache
```

Kết quả: 40 bài → 38 bộ / 291 slide (2 bộ thể thao bị loại vì bước duyệt ảnh lỗi cả 3 lần). Nội dung slide được trích nguyên văn từ bài, có `url` + `revid` để tái lập.

## 4. Sinh slide và chấm reward tự động

```bash
python scripts/testset_generate.py prepare                       # prompt giống hệt lúc train
bash rl/runs/final_v3_20261005/testset/run_qwen.sh                # DAPO 4 mẫu + model gốc 8 mẫu (~2 giờ H100)
.venv/bin/python scripts/testset_generate.py gemini --samples 4   # Gemini 3.5 Flash, function calling gốc
bash rl/runs/final_v3_20261005/testset/run_score.sh               # render + reward đầy đủ (~1 giờ, ViT trên GPU)
python3 scripts/testset_summary.py                                # bảng tự động -> slidegen_data/testset/summary.md
```

Mọi bước đều tự tiếp tục từ `slidegen_data/testset/outputs/*.jsonl` và `scored/*.jsonl`. Hệ thống so sánh: `dapo` (mẫu 0), `base` (mẫu 0), `best8` (1 trong 8 mẫu của model gốc có reward cao nhất), `gemini` (mẫu 0).

Lưu ý khi viết paper: bảng tự động là chính hàm mục tiêu lúc train nên có lợi cho DAPO; kết quả chính phải là người chấm.

## 5. Bộ chấm người

```bash
python scripts/build_annotation_set.py --upload
```

- Ghép cặp phân tầng theo loại slide và chế độ ảnh: DAPO–gốc (toàn bộ), DAPO–Gemini (180), DAPO–best8 (150); đảo trái/phải và thứ tự ngẫu nhiên; ~5% cặp lặp lại (đảo bên) để kiểm tra chú ý; cặp có một bên lỗi được xử tự động, không đưa cho người chấm.
- Mỗi cặp 2 người chấm, 15% cặp cả 3 người chấm. Tên ảnh là mã băm có salt bí mật.
- Ghi ra `annotation_web/public/data/{pairs,assignments}.json` (công khai) và `slidegen_data/annotation/secret_mapping.json` (bí mật, cần để giải mã).
- Chạy lại script sẽ tạo salt mới và ghép lại từ đầu: chỉ làm trước khi bắt đầu chấm, sau đó deploy lại.

## 6. Trang chấm (Vercel)

- Mã người chấm và admin token: `slidegen_data/annotation/credentials.json` (không push). Gửi mỗi người một mã riêng.
- Deploy lại sau khi sửa: `npx vercel --cwd annotation_web deploy --prod --yes --token $VERCEL_TOKEN` (cần Node ở `/data/tools/node-v22.11.0-linux-x64/bin`).
- Đổi mã người chấm: `npx vercel env rm ANNOTATOR_CODES production` rồi `env add` lại với dạng `ma1:A1,ma2:A2,ma3:A3`, sau đó deploy lại.
- Hướng dẫn cho người chấm nằm ngay trên trang (nút *Hướng dẫn*) và trong `annotation_web/README.md`.

## 7. Lấy kết quả và phân tích

```bash
curl -s -H "x-admin-token: <admin_token>" https://slidegen-annotation.vercel.app/api/export > ratings.json
python3 scripts/analyze_annotations.py ratings.json slidegen_data/annotation/secret_mapping.json --out slidegen_data/annotation/report
```

Báo cáo gồm: tỉ lệ thắng theo từng tiêu chí với khoảng tin cậy 95% (bootstrap theo bộ slide), có và không tính output lỗi; tỉ lệ cờ lỗi nghiêm trọng của từng hệ thống; Krippendorff's alpha; độ nhất quán ở cặp kiểm tra chú ý; độ khớp giữa người chấm và reward tổng hợp / từng thành phần (faithful↔numeric_fact, coverage↔semantic/lexical, language↔language, layout↔dom, aesthetic↔aesthetic, overall↔composite).

## 8. Trước khi tắt container

```bash
bash /data/claude_backup/backup.sh
```
