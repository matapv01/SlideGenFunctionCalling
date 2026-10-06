# Tổng quan hệ thống huấn luyện GRPO

## Mục đích và phạm vi

Thư mục `rl/` hiện triển khai huấn luyện trực tiếp policy sinh function call cho
SlideGen bằng `Qwen/Qwen3-8B` + LoRA + TRL. Không có giai đoạn SFT/SDFT trước
GRPO. Model policy sinh đúng một serialized `<tool_call>` chứa một XML tool đã
được chỉ định cho slide; code backend/frontend sản xuất được dùng lại để gán
layout, thực thi và render.

Corpus train là corpus offline đã rebuild, không phải tool call cũ trong file
nguồn lịch sử. `scripts/rebuild_grpo_corpus.py` gọi planner, image search, Qwen-VL
duyệt ảnh và lưu nội dung/style/ảnh được duyệt. Khi train, loader đọc corpus cùng
ảnh local; policy Qwen3-8B chạy local trên máy train. Training không gọi planner
LLM hay image-search API. Renderer reward cần BE/FE SlideGen tương thích đang
chạy; vì vậy contract có lưu dấu cấu hình và code render.

## Luồng dữ liệu và mục tiêu tối ưu

```text
JSON slide nguồn
  -> rebuild corpus bằng pipeline BE mới
  -> nội dung đã refine + deck style + ảnh được duyệt (hoặc không ảnh)
  -> loader offline kiểm tra schema, provenance và file ảnh local
  -> chia train/eval theo document; gán layout bằng retriever/tool BE
  -> Qwen3-8B + LoRA sinh N completion cho từng prompt
  -> kiểm tra canonical tool call, tool assignment, schema và XML execution
  -> render song song qua frontend production; lấy text, DOM, trạng thái ảnh
  -> chấm ViT + metric text/số liệu + weighted scalar reward
  -> TRL group-relative advantages + DAPO loss + optimizer update
  -> evaluation, checkpoint và training-contract kiểm tra resume
```

Qwen native format/tool/schema là hard gate: completion không hợp lệ nhận
`RL_INVALID_REWARD` (mặc định `-2.0`) và không đưa qua renderer/ViT. Với
completion hợp lệ, các reward component đều trong `[0,1]` và được cộng đúng một lần:

```text
R = 0.5*lexical + 0.7*semantic + 1.0*numeric_fact
  + 1.5*dom + 1.5*aesthetic + 0.25*image_loaded
```

Đây là scalar reward đưa vào GRPO/DAPO, không phải mỗi rule là một loss
vi phân độc lập. Numeric literal bị loại khỏi lexical/semantic inputs; tín hiệu numeric không
được đếm lại ở hai metric đó. Text bị cắt/tràn, vượt biên slide hoặc va chạm
textbox đặt `dom=0`; lỗi DOM không bị trừ thêm lần nữa ngoài component này. Tải
ảnh chỉ thuộc `image_loaded`. Nếu sample không cần ảnh, `image_loaded=1.0` (không
áp dụng, không phạt). Các trọng số ưu tiên bố cục và thẩm mỹ ngang với tổng tín
hiệu nội dung tối đa.
Aesthetic dùng ViT-Base pairwise một logit: điểm cao là slide được ưa thích.
Score = sigmoid((logit - center) / temperature), mặc định center=0, temperature=1.
Đây là mapping bounded chưa hiệu chuẩn, không phải xác suất đúng.
ViT chỉ là reward model cố định: toàn bộ tham số bị khóa gradient, model ở chế độ
eval và forward nằm trong `torch.inference_mode()`. Optimizer GRPO chỉ cập nhật
LoRA của Qwen3-8B; không train lại ViT. Khi chuyển máy chỉ cần checkpoint ViT,
không cần bộ dữ liệu, notebook hay các experiment khác của ViT.

Có thể chạy `python rl/train.py --preflight-only` trước khi nạp policy. Chế độ này
dùng chung luồng chuẩn bị dữ liệu, chia train/eval theo doc, RAG, kiểm tra context,
hợp đồng resume và renderer/ViT với train thật, rồi ghi `preflight.json` và dừng.
Không khởi tạo policy, optimizer hay chạy backward. Trên máy không có CUDA cần
`USE_CPU=true` và thư mục output riêng; trên H100 phải kiểm tra lại với cấu hình
GPU thật. Preflight không thay thế smoke một optimizer step hoặc pilot chất lượng.

ViT đã được train pairwise; các tham số center/temperature và hệ số ghép component
vẫn là baseline chưa hiệu chuẩn trên phân phối rollout. Cần đánh giá chúng trên
tập preference có nhãn độc lập. Numeric attribution cũng là heuristic dựa trên context/cue, không
phải factuality model. Unit test kiểm tra invariant code chứ không chứng minh chất
lượng reward trên corpus; cần audit ví dụ và component distributions trước run H100 dài.

TRL 1.7.1 chuẩn hóa DAPO theo số token của generation window. Trainer custom
chia thêm cho số generation window trọn vẹn trong optimizer update hiện tại;
nếu update kết thúc giữa một generation window thì dừng lỗi thay vì âm thầm cập
nhật sai scale. Mặc định `generation_batch_size=4`, `num_generations=4`,
`steps_per_generation=4`, `gradient_accumulation_steps=16`: một optimizer update
gom bốn prompt group (16 completion). `beta=0` mặc định nên không có KL/reference
penalty; đây là lựa chọn cấu hình cần đánh giá qua pilot, không phải bảo đảm policy
không drift.

Checkpoint chỉ resume khi fingerprint khớp dữ liệu đã chuẩn bị, ảnh local, model
(revision hoặc hash các file model local), cấu hình reward/render, code nguồn liên
quan và package versions. Hash checkpoint model local cần đọc toàn bộ weight file
một lượt lúc lập contract; đây là I/O bổ sung có chủ đích để tránh dùng nhầm
base model khi resume.

## Giải thích từng file Python

| File | Trách nhiệm và ranh giới |
|---|---|
| `__init__.py` | Package marker của `rl`; không khởi tạo model hay runtime. |
| `common.py` | Hằng số LoRA và chọn GPU khi chạy CLI. Không còn chọn GPU/load `.env` chỉ vì import module. |
| `train.py` | Entrypoint/orchestrator: đọc cấu hình, khởi tạo tokenizer/model LoRA, tạo `GRPOConfig`, kiểm tra resume, chạy trainer/eval, lưu adapter/metrics và đóng renderer. Không chứa logic chuẩn hóa job/prompt. |
| `train_data.py` | Chuẩn hóa slide từ corpus mới; yêu cầu `style_context` sản xuất thay vì tự bịa palette; tạo retrieval query từ topic/content/layout/ảnh; gọi BE `assign_layouts`; build prompt/tool schema; trích numeric facts; tách document train/eval. |
| `grpo_trainer.py` | Mở rộng TRL trainer cho DAPO/CISPO/VESPO token-normalized loss scaling qua nhiều generation window; fail-fast nếu optimizer update không chứa số nguyên generation window; ghi và kiểm tra metadata resume. Mặc định run dùng DAPO. |
| `training_contract.py` | Tạo hash chuẩn hóa cho dataset đã chuẩn bị, corpus, ảnh, reward weights, code/backend/frontend/package lock, runtime render và model. Với model local, hash config/tokenizer/weight shards để chặn resume nhầm checkpoint nền. |
| `slidegen_adapter.py` | Cầu nối RL–BE/FE: expose XML tools, thực thi một tool, định dạng tool schema cho Qwen, dựng user prompt và render XML qua frontend; thu text, DOM issue và image load status bằng script trình duyệt. |
| `render_runtime.py` | Quản lý một Playwright/Chromium lâu dài trên thread asyncio riêng; mỗi sample dùng page riêng, chạy đồng thời có semaphore/timeout, luôn đóng page/browser khi kết thúc. |
| `image_assets.py` | Trích/resolve ảnh trong corpus cũ và v2+, đọc manifest VLM, kiểm tra confidence/path/file, ràng buộc ảnh cache trong `static/output` để frontend tải được. |
| `toolcall_data.py` | Chia evaluator offline theo document ID ổn định, tránh đưa slide cùng document sang nhiều split. Chỉ phục vụ đánh giá tool-call offline. |
| `eval_tooluse.py` | CLI đánh giá response tool-call ngoài rollout: parse JSON/tag, so tool/arguments, tính metrics, bootstrap CI và paired comparison; ghi `evaluation_report.json` cùng `predictions.jsonl`. Dataset gold mặc định là `data/sft_function_call_dataset.json`, chỉ dùng cho offline eval, không được `train.py` nạp để train. |
| `run_artifacts.py` | Tee stdout/stderr; ghi runtime/Git/GPU metadata, JSON logs, biểu đồ metric và ảnh tóm tắt run. Không tham gia tính loss/reward. |
| `rewards/__init__.py` | Expose API công khai cho composite reward, preflight và setter text embedder. |
| `rewards/content_reward.py` | Metric thuần nội dung: token/keyword overlap; heuristic giữ số và liên hệ số–ngữ cảnh/cue tăng-giảm; semantic embedding theo chunk với cache LRU có giới hạn. Numeric heuristic không phải bộ kiểm chứng entailment. |
| `rewards/aesthetic_reward.py` | Nạp ViT-Base pairwise local strict; khóa gradient, chia batch inference; sigmoid utility với center/temperature cố định; log raw score và saturation. |
| `rewards/composite_reward.py` | Bộ điều phối online reward: strict parse/schema/tool gate; áp deck style và ảnh được duyệt; chạy BE XML; render FE; ghép lexical/semantic/numeric/DOM/image/ViT thành scalar weighted reward và log metrics/timing. |
| `test_eval_tooluse.py` | Regression test cho parser, scoring response và holdout evaluator offline. |
| `test_grpo_pipeline.py` | Regression test cho split theo doc, gán layout/tool, strict validity, nội dung render, DAPO scaling, model/checkpoint và ViT reward. |
| `test_grpo_runtime.py` | Regression test cho numeric/content metrics, image URL matching, browser lifecycle, reward bounds và fingerprint contract. |

## File ngoài `rl/` tham gia luồng

- `scripts/rebuild_grpo_corpus.py`: chạy planner và pipeline ảnh production để tạo corpus mới.
- `scripts/generate_challenge_dataset.py`: loader/validator offline, chuyển corpus thành danh sách document cho train.
- `scripts/cache_grpo_image_assets.py`: tải/kiểm tra ảnh được duyệt vào cache portable để chép sang H100.
- `backend/config.py`: cấu hình model/API của bước rebuild, embedding, browser preview và viewport.
- `backend/workflows/slidegen_workflow/`: tool schema, layout retrieval, deck styling và XML execution dùng lại.
- `frontend/src/components/XmlSlideCanvas.tsx`, `frontend/src/lib/xmlSlide.ts`: render XML và DOM được reward đọc.
- `models/vit/best_model_pairwise.pt`: checkpoint aesthetic reward local; không tải pretrained ViT từ Hub trong lúc train.

## Trạng thái khoa học và giới hạn

Reward là một tổ hợp engineering signal, không phải ground-truth judge. Semantic
cosine có thể nhầm paraphrase/contradiction; lexical có thể đánh giá thấp cách
viết lại; numeric context có thể bỏ sót phủ định, quy đổi đơn vị hoặc số viết bằng
chữ; ViT đo preference đã học, không bảo đảm toàn diện thẩm mỹ. Vì vậy, trước
train tốn kém nên tạo tập completion đối chứng có nhãn, đo pairwise accuracy và
xem ablation từng component/weight trên holdout. Khi chưa có kết quả đó, không
nên gọi trọng số mặc định là “đã tối ưu” hay “đã hiệu chuẩn”.

Pairwise settings và preprocessing được fingerprint trong training contract. Đổi
checkpoint/calibration cần run mới. RL_VIT_BATCH_SIZE=4 giới hạn mỗi forward.
Theo dõi reward_pairwise/saturated_fraction và score_std; không chuẩn hóa theo
từng rollout batch.
