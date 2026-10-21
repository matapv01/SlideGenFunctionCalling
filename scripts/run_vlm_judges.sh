#!/usr/bin/env bash
# Serve each VLM in turn on one GPU, judge both human-eval rounds with it, analyse, stop the server.
# Usage: GPU=1 bash scripts/run_vlm_judges.sh "<hf repo>|<short name>|<extra vllm args>" ...
# Outputs: slidegen_data/annotation/vlm_judge/r{1,2}_<short name>.jsonl and r{1,2}_<short name>_report.md
set -uo pipefail
cd "$(dirname "$0")/.."
GPU=${GPU:-1}
PORT=${PORT:-8004}
OUT=slidegen_data/annotation/vlm_judge
RATINGS=${RATINGS:-slidegen_data/annotation/round2/ratings_latest.json}
mkdir -p "$OUT" rl/log/vlm_server
set -a; . <(grep "^HF_TOKEN=" .env); set +a

for spec in "$@"; do
  IFS='|' read -r repo name extra <<< "$spec"
  echo "=== $name ($repo)"
  .venv/bin/hf download "$repo" > /dev/null 2>&1 || { echo "DOWNLOAD_FAILED $name"; continue; }
  # shellcheck disable=SC2086
  CUDA_VISIBLE_DEVICES=$GPU .venv/bin/vllm serve "$repo" --served-model-name "$name" --host 127.0.0.1 --port "$PORT" \
    --max-model-len 8192 --gpu-memory-utilization 0.6 --limit-mm-per-prompt '{"image": 2}' --max-num-seqs 32 $extra \
    > "rl/log/vlm_server/serve_$name.log" 2>&1 &
  server=$!
  until curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null; do
    kill -0 $server 2> /dev/null || { echo "SERVER_DEAD $name"; break; }
    sleep 10
  done
  if kill -0 $server 2> /dev/null; then
    echo "SERVER_READY $name"
    for round in 2 1; do
      .venv/bin/python scripts/vlm_pairwise_judge.py --round $round --model "$name" --base-url "http://127.0.0.1:$PORT/v1" \
        --out "$OUT/r${round}_$name.jsonl" && \
      .venv/bin/python scripts/analyze_vlm_judge.py --round $round --ratings "$RATINGS" --vlm "$OUT/r${round}_$name.jsonl" \
        --out "$OUT/r${round}_${name}_report.md" > /dev/null && echo "ANALYZED r$round $name"
    done
    kill $server; wait $server 2> /dev/null
  fi
done
echo ALL_DONE
