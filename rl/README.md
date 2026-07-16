# RL Training

Pipeline training slide function calling của repo.

## Stack hiện tại
- SDFT chính thức: Hugging Face Transformers + TRL `DistilTrainer` + PEFT LoRA.
- GRPO hiện tại: TRL `GRPOTrainer` + rollout/reward custom của repo.
- Unsloth: không dùng ở SDFT official; GRPO loader hiện tại vẫn dùng để load model/adapter nhanh.

## Chiến lược
1. SDFT trước để khóa format function call và khả năng chọn tool.
2. GRPO sau để tối ưu chất lượng slide bằng reward.
3. Không trộn hard-label SFT vào path SDFT official; giữ teacher prompt + on-policy distillation.

## SDFT official
Input chính là `rl/data/sft_function_call_dataset.json`.

Mỗi sample được đổi thành:
- `prompt`: prompt thật của bài toán, gồm system prompt + tools + user task.
- `teacher_prompt`: cùng user task nhưng thêm ví dụ in-context với `tool_call` mẫu.

Huấn luyện:
- Student và ref/teacher model cùng khởi tạo từ base model.
- Cùng PEFT LoRA config lấy từ `rl.common`.
- `generate_from_teacher=True`.
- Loss mặc định: forward KL (`alpha=0.0`, `beta=0.0`).
- Ref model sync: `sync_ref_model=True`, `ref_model_mixup_alpha=0.01`.
- `num_loss_tokens_to_skip=3` để bỏ phần token đầu của completion.
- vLLM là tùy chọn; nếu không có thì fallback sang `transformers.generate()`.

Output:
- `./qwen_slidegen_sdft/final_adapter`

Không còn các nhánh cũ kiểu:
- Round 0 / Round 1+
- CPU `ref_state`
- hard-label SFT
- EMA kiểu `pi_ref = alpha * pi_theta + ...`

## GRPO hiện tại
GRPO trong repo dùng `GRPOTrainer` của TRL, nhưng phần rollout là custom cho SlideGen:
- planner sinh plan
- preparer sinh design instruction
- tool retriever chọn tool
- Qwen generate function call
- execute tool, render HTML, lấy reward

Model load hiện tại vẫn dùng `FastLanguageModel` + LoRA để giữ tốc độ và khớp checkpoint `final_adapter` từ SDFT.

Reward funcs hiện có:
- aesthetic
- content preservation
- visual consistency
- conciseness
- text embedding

## Chạy
```bash
uv run python rl/sdft.py
uv run python rl/train.py
```

## Biến môi trường quan trọng
| Variable | Default | Ý nghĩa |
|---|---:|---|
| `TRAINING_MODEL_ID` | `Qwen/Qwen3-8B` cho SDFT, `Qwen/Qwen3-4B-Instruct-2507` cho GRPO | Base model |
| `SDFT_OUTPUT_DIR` | `./qwen_slidegen_sdft` | Nơi lưu adapter cuối của SDFT |
| `SDFT_ADAPTER_PATH` | `./qwen_slidegen_sdft/final_adapter` | Adapter SDFT để GRPO load |
| `SDFT_USE_VLLM` | `true` | Bật vLLM nếu có |
| `SDFT_MIXUP_ALPHA` | `0.01` | Mức sync ref model |
| `SDFT_NUM_LOSS_TOKENS_TO_SKIP` | `3` | Bỏ token đầu khi tính loss |
| `GRPO_OUTPUT_DIR` | `./qwen_slidegen_grpo` | Nơi lưu checkpoint GRPO |
| `TOTAL_STEPS` | `500` | Số bước GRPO |
| `BATCH_DOCS` | `5` | Số doc rollout mỗi step |

## Key files
- `rl/sdft_official/train_slidegen.py`: entrypoint SDFT official.
- `rl/sdft.py`: wrapper tương thích để gọi SDFT official.
- `rl/train.py`: entrypoint GRPO hiện tại.
- `rl/common.py`: helper chung cho GPU, tokenizer, LoRA constants.
- `rl/sdft_official/distil_trainer.py`: trainer official vendored từ TRL.
- `rl/sdft_official/distil_config.py`: config official vendored từ TRL.
