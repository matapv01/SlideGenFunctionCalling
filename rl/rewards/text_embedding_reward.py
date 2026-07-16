import json
import re
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sentence_transformers import SentenceTransformer
from backend.workflows.slidegen_workflow.utils.helper import parse_tool_call_json


embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")


def extract_text_from_completion(completion: str) -> str:
    try:
        data = parse_tool_call_json(completion)
        if not data:
            return ""
        text_parts = []

        def recurse(node):
            if isinstance(node, str):
                text_parts.append(node)
            elif isinstance(node, list):
                for item in node:
                    recurse(item)
            elif isinstance(node, dict):
                for val in node.values():
                    recurse(val)

        recurse(data.get("arguments", {}))
        return " ".join(text_parts)
    except Exception:
        return ""


def extract_content_from_prompt(prompt: str) -> str:
    match = re.search(r'\[CONTENT\]\n(.+?)(?:\n\nOutput:|$)', prompt, re.DOTALL)
    if match:
        return match.group(1).strip()
    return prompt[-1000:]


def text_embedding_reward(prompts, completions, **kwargs):
    rewards = []

    texts_a = []
    texts_b = []
    for prompt, completion in zip(prompts, completions):
        gen_text = extract_text_from_completion(completion)
        input_text = extract_content_from_prompt(prompt)
        texts_a.append(gen_text if gen_text else ".")
        texts_b.append(input_text if input_text else ".")

    has_valid = any(t != "." for t in texts_a)
    if not has_valid:
        rewards = [0.0] * len(completions)
        scores_str = " ".join(f"{s:.3f}" for s in rewards)
        print(f"  [TextEmbedding Reward] scores=[{scores_str}]")
        return rewards

    embs_a = embedder.encode(texts_a, normalize_embeddings=True, show_progress_bar=False)
    embs_b = embedder.encode(texts_b, normalize_embeddings=True, show_progress_bar=False)

    for gen_text, emb_a, emb_b in zip(texts_a, embs_a, embs_b):
        if gen_text == ".":
            rewards.append(0.0)
        else:
            sim = float(np.dot(emb_a, emb_b))
            sim = max(0.0, min(1.0, sim))
            rewards.append(sim)

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    print(f"  [TextEmbedding Reward] scores=[{scores_str}]")
    return rewards
