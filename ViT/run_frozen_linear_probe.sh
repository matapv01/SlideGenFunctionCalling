#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

protocol_dir="ViT/experiments/train_test_protocol"
sweep_dir="$protocol_dir/frozen_linear_probe_sweep"
log_file="$sweep_dir/run.log"
mkdir -p "$sweep_dir"
export CUDA_VISIBLE_DEVICES=0

for lr in 1e-4 5e-4 1e-3; do
  output_dir="$sweep_dir/lr_${lr}"
  mkdir -p "$output_dir"
  printf '%s training frozen ViT-Base linear probe, lr=%s\n' "$(date -Is)" "$lr" | tee -a "$log_file"
  .venv/bin/python ViT/train_vit_multilabel.py \
    --data-dir "$protocol_dir/data" \
    --output-dir "$output_dir" \
    --model google/vit-base-patch16-224-in21k \
    --epochs 30 --batch-size 128 --learning-rate "$lr" \
    --patience 5 --workers 8 --seed 45 --device cuda:0 \
    --freeze-backbone 2>&1 | tee "$output_dir/train.log" | tee -a "$log_file"
done

best_dir="$(.venv/bin/python -c 'import json, pathlib; root=pathlib.Path("ViT/experiments/train_test_protocol/frozen_linear_probe_sweep"); candidates=list(root.glob("lr_*/metrics.json")); best=max(candidates, key=lambda p: json.loads(p.read_text())["metrics_at_0_5"]["macro_f1"]); print(best.parent)')"
printf '%s selected %s by internal macro F1 at threshold 0.5\n' "$(date -Is)" "$best_dir" | tee -a "$log_file"

.venv/bin/python ViT/evaluate_train_test_protocol.py \
  --data-dir "$protocol_dir/data" \
  --test-csv "$protocol_dir/data/test_dataset.csv" \
  --shared-dir "$protocol_dir/shared_base" \
  --frozen-dir "$best_dir" \
  --binary-color-dir "$protocol_dir/binary_small" \
  --binary-structural-dir "$protocol_dir/binary_base_structural" \
  --output-dir "$protocol_dir/test_evaluation_with_frozen" \
  --device cuda:0 --batch-size 64 --workers 8 \
  2>&1 | tee -a "$log_file"

printf '%s frozen ViT-Base baseline completed\n' "$(date -Is)" | tee -a "$log_file"
