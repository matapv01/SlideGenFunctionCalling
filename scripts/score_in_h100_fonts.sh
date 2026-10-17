#!/usr/bin/env bash
# Run a command with the exact font set the H100 scoring runs had, so slides render and measure the same.
#
# Layout (text measurement in xml_tool) and Chromium both pick fonts from /usr/share/fonts. The H100
# container had the Playwright font set only (Liberation, FreeFont, IPAGothic, WenQuanYi, Loma, Unifont,
# Noto Color Emoji) and no DejaVu; a machine with more fonts wraps text differently and changes the
# text_cutoff/text_height verdicts. The slidegen image has that set plus DejaVu, which is hidden here.
# Python packages come from uv.lock (separate venv .venv-h100fonts), the renderer is the host's :12008;
# fontconfig gets its own cache so host fonts never leak in.
#
# Usage: GPU=1 scripts/score_in_h100_fonts.sh python scripts/testset_generate.py score --systems ...
set -euo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)
IMAGE=${IMAGE:-slidegen:latest}
ENV_ARGS=()
for name in $(compgen -e | grep -E '^(TESTSET_|RL_|REWARD_|EMBEDDING_|OMP_|HF_HUB_)'); do ENV_ARGS+=(-e "$name"); done
exec docker run --rm --network host --gpus "\"device=${GPU:-0}\"" \
  --user "$(id -u):$(id -g)" --tmpfs /usr/share/fonts/truetype/dejavu \
  -v "$HOME:$HOME" -w "$REPO" -e HOME="$HOME" \
  -e UV_PROJECT_ENVIRONMENT="$REPO/.venv-h100fonts" -e UV_PYTHON=3.12 \
  -e XDG_CACHE_HOME="$REPO/.cache-h100fonts" -e UV_CACHE_DIR="$HOME/.cache/uv" \
  -e HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}" -e PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright" \
  "${ENV_ARGS[@]}" --entrypoint bash "$IMAGE" -c \
  "fc-cache >/dev/null 2>&1; $HOME/.local/bin/uv sync --locked -q && $HOME/.local/bin/uv run --locked $(printf '%q ' "$@")"
