import json
import re
from typing import List

from backend.workflows.slidegen_workflow.utils.helper import parse_tool_call_json


def extract_text_from_json(json_str: str) -> str:
    try:
        data = parse_tool_call_json(json_str)
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


def clean_words(text: str) -> List[str]:
    text = text.lower()
    words = re.findall(r'\b\w{2,}\b', text)
    stopwords = {"và", "của", "các", "cho", "trong", "để", "này", "được", "với", "như", "một", "những"}
    return [w for w in words if w not in stopwords]


def content_preservation_reward(prompts: List[str], completions: List[str], **kwargs) -> List[float]:
    rewards = []

    for prompt, completion in zip(prompts, completions):
        generated_text = extract_text_from_json(completion)
        if not generated_text:
            rewards.append(0.0)
            continue

        match = re.search(r"\[CONTENT\]\n(.+?)(?:\n\nOutput:|$)", prompt, re.DOTALL)
        prompt_content = (
            match.group(1).strip() if match else prompt[-1200:]
        )

        original_words = clean_words(prompt_content)
        generated_words = clean_words(generated_text)

        if not original_words:
            rewards.append(1.0)
            continue

        original_set = set(original_words)
        generated_set = set(generated_words)

        preserved_keywords = original_set.intersection(generated_set)
        overlap_ratio = len(preserved_keywords) / len(original_set)

        ratio_len = len(generated_words) / len(original_words)
        length_penalty = 1.0
        if ratio_len < 0.3:
            length_penalty = ratio_len / 0.3

        final_score = overlap_ratio * length_penalty
        final_score = max(0.0, min(1.0, final_score))
        rewards.append(final_score)

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    print(f"  [Content Reward] scores=[{scores_str}]")
    return rewards
