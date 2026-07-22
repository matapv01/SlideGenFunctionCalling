# RL Training

Pipeline training slide function calling của repo.

## Stack hiện tại

- Function-call SFT: Transformers `Trainer` + completion-only cross-entropy + frozen-base KL + PEFT LoRA.
- GRPO: TRL `GRPOTrainer` + rollout/reward custom của repo.
- Legacy context-distillation code còn ở `rl/sdft_official/train_slidegen.py` để tham khảo, nhưng không còn là launcher mặc định.

## Chiến lược

1. Validate tool call do Gemini sinh.
2. Completion-only SFT để học trực tiếp golden tool name và arguments.
3. Frozen-base forward KL (`0.03` mặc định) để hạn chế adapter lệch khỏi base model.
4. Early stopping trên validation loss; split train/eval/test theo `doc_id`.
5. GRPO sau khi SFT vượt base trên test set để tối ưu execution/render/content/aesthetic.

## Function-call SFT + base KL

Input chính là `rl/data/sft_function_call_dataset.json`. Mỗi sample dùng prompt thật và target:

```text
<tool_call>{"name": "...", "arguments": {...}}</tool_call>
```

Loss chỉ áp dụng trên assistant completion:

```text
loss = completion_cross_entropy + 0.03 * KL(frozen_base || LoRA_student)
```

Các bảo vệ dữ liệu/token:

- Split ổn định theo `doc_id`: hiện tại 340 train / 41 validation / 33 test với seed 42.
- Correct tool luôn nằm trong sáu offered tools.
- Tool schema được compact nhưng giữ name/type/default/required/items.
- Budget prompt/completion tách riêng: 4096/3072 tokens.
- Sample vượt budget làm training fail-fast; không truncate âm thầm.
- Best checkpoint được chọn theo `eval_loss`; test generation chạy sau training.

Chạy:

```bash
TRAINING_GPU=2 uv run python rl/sdft.py
```

Hoặc gọi trực tiếp:

```bash
TRAINING_GPU=2 uv run python rl/sft_toolcall.py \
  --model_name Qwen/Qwen3-4B-Instruct-2507 \
  --kl_coef 0.03 \
  --epochs 3
```

Output:

- Adapter: `qwen_slidegen_sft/final_adapter`.
- Log: `rl/log/sft_toolcall/run_<timestamp>/`.
- Test: `test_report.json` và `test_predictions.jsonl`.

## GRPO hiện tại
GRPO trong repo dùng `GRPOTrainer` của TRL, nhưng phần rollout là custom cho SlideGen:
- planner sinh plan
- preparer sinh design instruction
- tool retriever chọn tool
- Qwen generate function call
- execute tool, render HTML, lấy reward

Model load hiện tại dùng `AutoModelForCausalLM` + PEFT LoRA. Nếu có checkpoint `final_adapter` từ SFT, GRPO load đúng base model từ `adapter_config.json` rồi attach adapter trainable.

Reward funcs hiện có:
- aesthetic
- content preservation
- visual consistency
- conciseness
- text embedding

## Chạy
Mặc định train dùng GPU2. Có thể truyền GPU ngay trong lệnh chạy:

```bash
TRAINING_GPU=2 uv run python rl/sdft.py
TRAINING_GPU=2 uv run python rl/train.py
```

Alias cũng được hỗ trợ: `GPU_ID=2`, `GPU=2`, `PREFERRED_GPU=2`. Nếu set trực tiếp `CUDA_VISIBLE_DEVICES=2` thì biến này có ưu tiên cao nhất.

## Biến môi trường quan trọng
| Variable | Default | Ý nghĩa |
|---|---:|---|
| `TRAINING_MODEL_ID` | `Qwen/Qwen3-4B-Instruct-2507` | Base model |
| `TRAINING_GPU` | `2` | GPU vật lý dùng cho train; alias: `GPU_ID`, `GPU`, `PREFERRED_GPU` |
| `SFT_OUTPUT_DIR` | `./qwen_slidegen_sft` | Nơi lưu adapter cuối |
| `SFT_LEARNING_RATE` | `1e-5` | Learning rate LoRA |
| `SFT_EPOCHS` | `3` | Số epoch tối đa; có early stopping |
| `SFT_KL_COEF` | `0.03` | Hệ số frozen-base KL |
| `SFT_MAX_PROMPT_LENGTH` | `4096` | Budget prompt; vượt budget sẽ báo lỗi |
| `SFT_MAX_COMPLETION_LENGTH` | `3072` | Budget golden tool call |
| `SDFT_ADAPTER_PATH` | `./qwen_slidegen_sft/final_adapter` | Adapter SFT để GRPO load |
| `GRPO_OUTPUT_DIR` | `./qwen_slidegen_grpo` | Nơi lưu checkpoint GRPO |
| `TOTAL_STEPS` | `500` | Số bước GRPO |
| `BATCH_DOCS` | `5` | Số doc rollout mỗi step |
| `GRPO_RESUME` | `true` | Tự load adapter GRPO hoàn chỉnh mới nhất và bỏ qua step đã xong |
| `MAX_COMPLETION_LENGTH` | `2048` | Giảm xuống `1024` hoặc `512` nếu OOM lúc generate |

## Chạy tiếp sau CUDA OOM

GRPO tự động load adapter hoàn chỉnh mới nhất trong `rl/data/step_XXXX_adapter` khi `GRPO_RESUME=true`. Step đã lưu checkpoint sẽ được bỏ qua; step bị crash giữa chừng sẽ chạy lại từ đầu step đó và dùng lại các file cache đã tạo.

Nếu GPU cũ còn process chiếm VRAM, chọn GPU còn trống và giảm độ dài generation:

```bash
nvidia-smi

# Chọn GPU còn ít memory-used nhất; ví dụ GPU 0
CUDA_VISIBLE_DEVICES=0 \
TRAINING_GPU=0 \
GRPO_RESUME=true \
MAX_COMPLETION_LENGTH=256 \
BATCH_DOCS=1 \
NUM_GENERATIONS=2 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
uv run python rl/train.py
```

Nếu vẫn hết VRAM, trước hết dừng process cũ đang chiếm GPU (chỉ dừng đúng PID của job train), rồi thử `MAX_COMPLETION_LENGTH=128`. Không nên giảm `NUM_GENERATIONS` xuống `1`: GRPO thường cần ít nhất 2 completion để tính reward tương đối. Nếu mọi GPU đều đầy, cần giải phóng GPU hoặc dùng model nhỏ hơn/quantization; đổi `BATCH_DOCS` một mình thường không giải quyết OOM lúc `generate`.

Các checkpoint chỉ được tạo sau khi một GRPO step hoàn tất. Vì vậy không thể khôi phục chính xác phần update đang chạy lúc CUDA OOM; chỉ có thể chạy lại step đó từ checkpoint trước đó.

## Theo dõi metric

Mỗi GRPO step vẫn ghi metric ở thư mục `rl/log/grpo/run_<timestamp>/`:

- `run.log`: log console, gồm `loss` và `mean_reward` sau mỗi update.
- `metrics.jsonl`: metric dạng máy đọc được cho từng step.
- `step_summaries.json`: tổng hợp các step đã hoàn tất.
- `metrics_trend.png`: biểu đồ các metric chính.
- Trong `qwen_slidegen_grpo/checkpoint-*/trainer_state.json` có lịch sử chi tiết nếu trainer tạo checkpoint.

Các chỉ số cần nhìn cùng nhau:

- `reward`: nên tăng hoặc ổn định; dao động mạnh có thể bình thường vì rollout ngẫu nhiên.
- `loss`: không nhất thiết phải giảm đều trong GRPO; dùng cùng reward và `kl`.
- `kl`: quá gần 0 nghĩa là update yếu; tăng đột biến nghĩa là policy lệch xa adapter ban đầu, nên giảm learning rate.
- `grad_norm`: spike lớn hoặc `NaN` là dấu hiệu bất ổn.
- `completion_length`: tăng sát giới hạn thường báo prompt/generation bị quá dài và dễ OOM.

Nếu OOM trước dòng `GRPO: loss=...`, step đó chưa update và chưa có checkpoint mới; chạy lại sẽ dùng cache của step đó nhưng tạo rollout/update lại từ đầu.

## Key files
- `rl/sft_toolcall.py`: completion-only SFT + frozen-base KL trainer.
- `rl/toolcall_data.py`: prompt compact, offered-tool selection và document split.
- `rl/sdft.py`: launcher tương thích, hiện gọi `rl/sft_toolcall.py`.
- `rl/sdft_official/train_slidegen.py`: legacy context-distillation path.
- `rl/train.py`: entrypoint GRPO hiện tại.
- `rl/common.py`: helper chung cho GPU, tokenizer, LoRA constants.
- `rl/sdft_official/distil_trainer.py`: trainer official vendored từ TRL.
- `rl/sdft_official/distil_config.py`: config official vendored từ TRL.

## Đánh giá function-call model

Training loss, KL và entropy chỉ cho biết quá trình tối ưu có chạy hay không; chúng không đủ để kết luận model chọn đúng tool hoặc sinh đúng arguments. Run SDFT hiện tại còn có `rewards=0` và `completions/clipped_ratio` thường trong khoảng 87.5–100%, vì vậy cần đánh giá trực tiếp trên response của model.

Evaluator nằm tại `rl/sdft_official/eval_tooluse.py`. Script chấm response đã sinh ở dạng JSON hoặc JSONL và không cần GPU:

```bash
uv run python rl/sdft_official/eval_tooluse.py \
  --responses candidate.jsonl \
  --output_dir rl/log/evaluation/sdft
```

Mỗi phần tử input có thể là chuỗi response hoặc object chứa một trong các field `response`, `completion`, `text`. Ví dụ JSONL:

```json
{"response":"<tool_call>{\"name\":\"generate_title_slide\",\"arguments\":{\"main_title\":\"Demo\"}}</tool_call>"}
```

Mặc định generator và evaluator dùng test split 10% theo `doc_id`, giống training. Có thể chọn `--split train`, `--split eval`, `--split test`, hoặc `--split all`; phải giữ cùng seed và split cho base/candidate/evaluator.

Các tên `candidate.jsonl`, `sdft_responses.jsonl` và `base_responses.jsonl` là file đầu ra cần sinh trước, không phải file có sẵn trong repository. Quy trình đầy đủ để so sánh adapter SFT với base model:

1. Sinh response của adapter SFT:

```bash
CUDA_VISIBLE_DEVICES=0 uv run python rl/sdft_official/generate_eval_responses.py \
  --model_path qwen_slidegen_sft/final_adapter \
  --output sdft_responses.jsonl
```

2. Sinh response của base model trên cùng holdout và cùng decoding config:

```bash
CUDA_VISIBLE_DEVICES=0 uv run python rl/sdft_official/generate_eval_responses.py \
  --model_path Qwen/Qwen3-4B-Instruct-2507 \
  --output base_responses.jsonl
```

Có thể dùng GPU khác bằng cách đổi `CUDA_VISIBLE_DEVICES`. Để smoke test trước khi chạy toàn bộ holdout, thêm `--max_samples 8` vào **cả ba** lệnh. Có thể giảm `--batch_size 1` nếu thiếu VRAM.

3. Chấm và so sánh paired:

```bash
uv run python rl/sdft_official/eval_tooluse.py \
  --responses sdft_responses.jsonl \
  --baseline_responses base_responses.jsonl \
  --output_dir rl/log/evaluation/base_vs_sdft
```

Hai file response phải có cùng số lượng và cùng thứ tự sample. Khi sinh response cần giữ cố định dataset, seed, danh sách distractor tools, prompt template và decoding config.

Evaluator ghi hai artifact:

- `evaluation_report.json`: metric tổng hợp, bootstrap 95% confidence interval, breakdown và paired comparison.
- `predictions.jsonl`: kết quả chi tiết từng sample để phân tích lỗi.

Các metric chính:

- `parse_success`: response có parse được thành JSON function call.
- `format_exact`: chỉ có một function call nằm đúng trong `<tool_call>...</tool_call>`.
- `tool_name_accuracy`: chọn đúng tool so với golden call.
- `valid_tool_rate`: tên tool tồn tại trong tool registry/dataset.
- `argument_key_precision` và `argument_key_recall`: mức đúng/đủ của arguments, bao gồm field lồng nhau.
- `argument_value_f1`: kết hợp độ đúng của key và value; màu hex được so sánh không phân biệt hoa thường, số thực dùng tolerance nhỏ.
- `arguments_exact`: toàn bộ arguments khớp golden call.
- `exact_match`: cả tool name và toàn bộ arguments đều khớp.
- `exact_match_ci95`: bootstrap 95% confidence interval của exact match.
- `tool_confusion`, `parse_errors`: nhóm lỗi chọn tool và lỗi định dạng thường gặp.
- Breakdown theo `category` và `gold_tool`: phát hiện model yếu ở nhóm slide/tool cụ thể.
- `paired_comparison`: delta exact match, số sample candidate thắng, baseline thắng và hòa.

Chạy test evaluator:

```bash
uv run pytest rl/sdft_official/test_eval_tooluse.py -q
```

### Cảnh báo training leakage

Adapter SDFT hiện tại đã train trên toàn bộ 414 sample trong `rl/data/sft_function_call_dataset.json`. Việc lấy 20% từ chính dataset này để đánh giá adapter đã train xong vẫn là đánh giá trên dữ liệu model từng thấy, dù evaluator chia theo `doc_id` lúc chấm.

Muốn có kết quả đáng tin cậy cần tạo holdout theo `doc_id` trước khi train, loại hoàn toàn các document đó khỏi training, sau đó sinh response của cả base model và adapter trên cùng holdout. Không dùng training loss hoặc kết quả trên 414 sample đã thấy để khẳng định model tổng quát hóa tốt hơn.
