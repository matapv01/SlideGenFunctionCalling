#!/usr/bin/env bash
set -uo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 RUN_ID" >&2
    exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
run_id="$1"
host_run_dir="$project_root/report_paper/ablation_runs/$run_id"
container_docs_dir="/tmp/slidegen_ablation_docs_$run_id"
container_runner="/tmp/run_ablation_study_$run_id.py"
container_output_root="/app/static/ablation_study"

mkdir -p "$host_run_dir"
exec > >(tee -a "$host_run_dir/tmux.log") 2>&1

echo "Ablation run: $run_id"
echo "Started: $(date --iso-8601=seconds)"
echo "Input: report_paper/img/doc (3 DOCX files expected)"
echo "Generation-time ViT: disabled"

docker exec slidegen mkdir -p "$container_docs_dir"
docker cp "$project_root/report_paper/img/doc/." "slidegen:$container_docs_dir/"
docker cp "$project_root/scripts/run_ablation_study.py" "slidegen:$container_runner"

docker exec \
    -e PYTHONPATH=/app \
    -e ENABLE_VIT_EVALUATION=false \
    slidegen \
    python "$container_runner" \
        --docs-dir "$container_docs_dir" \
        --output-root "$container_output_root" \
        --run-id "$run_id"
generation_status=$?

docker cp "slidegen:$container_output_root/$run_id/." "$host_run_dir/"

evaluation_status=0
if [[ -d "$host_run_dir/evaluation_input" ]]; then
    CUDA_VISIBLE_DEVICES=0 "$project_root/.venv/bin/python" \
        "$project_root/ViT/evaluate_generated_outputs.py" \
        --input-dir "$host_run_dir/evaluation_input" \
        --output-dir "$host_run_dir/vit_evaluation" \
        --device cuda:0 \
        --workers 4
    evaluation_status=$?
else
    echo "No final PNG collection found; skipping offline ViT evaluation."
    evaluation_status=1
fi

echo "Finished: $(date --iso-8601=seconds)"
echo "Generation status: $generation_status"
echo "Offline ViT status: $evaluation_status"

if [[ $generation_status -ne 0 || $evaluation_status -ne 0 ]]; then
    exit 1
fi
