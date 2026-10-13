"""Render chosen test-set outputs through the reward path (for eyeballing a pipeline/reward change).

Usage: python scripts/render_testset_samples.py <out_dir> <system> <key>[,<key>...] [sample]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import testset_generate as t  # noqa: E402
from backend.infrastructure.rag.gemini_provider import LocalEmbeddingToolRetrieveProvider  # noqa: E402
from rl.rewards import composite_reward  # noqa: E402
from rl.rewards.content_reward import set_text_embedder  # noqa: E402
from rl.slidegen_adapter import TOOLS_DICT  # noqa: E402

out, system, keys = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
sample = int(sys.argv[4]) if len(sys.argv) > 4 else 0
rows = {row["key"]: row for row in json.loads(t.ROWS.read_text(encoding="utf-8"))}
records = {r["key"]: r for r in t._read_jsonl(t.OUTPUTS / f"{system}.jsonl") if r["sample"] == sample}
picked = [records[key] for key in keys]
retriever = LocalEmbeddingToolRetrieveProvider(TOOLS_DICT, str(t.RETRIEVER_INDEX))
set_text_embedder(retriever.embeddings.model)
names = [f"{system}-{key}" for key in keys]
composite_reward.configure_sample_dump(out, [(name, 0) for name in names])
meta = [rows[key] for key in keys]
rewards = composite_reward.slidegen_composite_reward(
    prompts=[m["prompt"] for m in meta], completions=[r["completion"] for r in picked],
    assigned_tool_name=[m["assigned_tool_name"] for m in meta], source_content=[m["source_content"] for m in meta],
    deck_style=[m["deck_style"] for m in meta], approved_images=[m["approved_images"] for m in meta],
    image_mode=[m["image_mode"] for m in meta], numeric_facts=[m["numeric_facts"] for m in meta],
    source_doc_id=names, slide_index=[0] * len(names))
for name, reward in zip(names, rewards):
    detail = json.loads((Path(out) / "step_0000" / f"{name}_slide00.json").read_text(encoding="utf-8"))
    print(name, round(reward, 2), detail.get("dom_issues"), detail.get("min_contrast"))
