#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

protocol_dir="ViT/experiments/train_test_protocol"
log_file="$protocol_dir/run.log"
mkdir -p "$protocol_dir"

choose_gpu() {
  nvidia-smi --query-gpu=index,memory.free,utilization.gpu --format=csv,noheader,nounits \
    | awk -F',' '{gsub(/ /,"",$0); if ($2 >= 22000 && $3 <= 30) {print $1; exit}}'
}

gpu=""
while [[ -z "$gpu" ]]; do
  gpu="$(choose_gpu || true)"
  if [[ -z "$gpu" ]]; then
    printf '%s waiting for a GPU with >=22 GiB free and <=30%% utilization\n' "$(date -Is)" | tee -a "$log_file"
    sleep 60
  fi
done

printf '%s selected physical GPU %s\n' "$(date -Is)" "$gpu" | tee -a "$log_file"
export CUDA_VISIBLE_DEVICES="$gpu"

.venv/bin/python ViT/train_vit_multilabel.py \
  --data-dir "$protocol_dir/data" \
  --output-dir "$protocol_dir/shared_base" \
  --model google/vit-base-patch16-224-in21k \
  --epochs 30 --batch-size 64 --patience 5 --workers 8 --seed 45 --device cuda:0 \
  2>&1 | tee -a "$log_file"

.venv/bin/python ViT/train_vit_benchmark.py \
  --data-dir "$protocol_dir/data" \
  --output-dir "$protocol_dir/binary_small" \
  --model WinKawaks/vit-small-patch16-224 \
  --criteria mau_nen mau_chu \
  --epochs 30 --batch-size 128 --patience 5 --workers 8 --seed 45 --device cuda:0 \
  2>&1 | tee -a "$log_file"

.venv/bin/python ViT/train_vit_benchmark.py \
  --data-dir "$protocol_dir/data" \
  --output-dir "$protocol_dir/binary_base_structural" \
  --model google/vit-base-patch16-224-in21k \
  --criteria size_chu de_nhau tran_chu \
  --epochs 30 --batch-size 64 --patience 5 --workers 8 --seed 45 --device cuda:0 \
  2>&1 | tee -a "$log_file"

.venv/bin/python ViT/evaluate_train_test_protocol.py \
  --device cuda:0 2>&1 | tee -a "$log_file"

printf '%s train/test protocol completed\n' "$(date -Is)" | tee -a "$log_file"
