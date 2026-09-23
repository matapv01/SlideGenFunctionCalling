import os
from pathlib import Path
from threading import Lock

import numpy as np

from rl.slidegen_adapter import (
    execute_tool,
    parse_tool_call_json,
    render_xml_to_png,
    sanitize_to_placeholders,
)
from rl.vision_embedding import DINOv2EmbeddingProvider


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_EMBEDDER = None
_EMBEDDER_LOCK = Lock()


def _get_embedder() -> DINOv2EmbeddingProvider:
    global _EMBEDDER
    if _EMBEDDER is None:
        with _EMBEDDER_LOCK:
            if _EMBEDDER is None:
                _EMBEDDER = DINOv2EmbeddingProvider(device="cpu")
    return _EMBEDDER


def visual_consistency_reward(prompts, completions, previous_slide_embedding, **kwargs):
    del prompts, kwargs
    rewards = []
    temp_dir = PROJECT_ROOT / "rl" / "temp_rl_renders"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for idx, completion in enumerate(completions):
        temp_img_path = temp_dir / f"consistency_{os.getpid()}_{idx}.png"
        try:
            tool_call = parse_tool_call_json(completion)
            if not tool_call:
                rewards.append(-1.0)
                continue
            xml_content = execute_tool(sanitize_to_placeholders(tool_call))
            render_xml_to_png(xml_content, str(temp_img_path))
            current = _get_embedder().get_embedding_np(str(temp_img_path))
            previous = np.asarray(previous_slide_embedding[idx], dtype=np.float32)
            norm = np.linalg.norm(current) * np.linalg.norm(previous)
            # The first slide has no predecessor and should be neutral.
            rewards.append(float(np.dot(current, previous) / norm) if norm > 0 else 0.0)
        except Exception:
            rewards.append(-1.0)
        finally:
            temp_img_path.unlink(missing_ok=True)

    rewards = [max(-1.0, min(1.0, score)) for score in rewards]
    print(f"  [Consistency Reward] scores=[{' '.join(f'{s:.3f}' for s in rewards)}]")
    return rewards
