import json
import re


def _extract_json_span(text: str) -> tuple[int, int] | None:
    """Find the last valid JSON object/array in text, return (start, end+1)."""
    i = text.rfind("{")
    if i >= 0:
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        json.loads(text[i:j+1])
                        return (i, j+1)
                    except Exception:
                        pass
                    break
    i = text.rfind("[")
    if i >= 0:
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
                if depth == 0:
                    try:
                        json.loads(text[i:j+1])
                        return (i, j+1)
                    except Exception:
                        pass
                    break
    return None


def conciseness_reward(prompts, completions, **kwargs):
    """Reward high ratio of valid JSON content to total output.
    If output is purely JSON (ratio ≈ 1.0) → 1.0 (no penalty).
    If output has extra text before/after JSON → penalized by ratio^2.
    If no valid JSON found → -1.0 (heavy penalty)."""
    rewards = []
    for completion in completions:
        span = _extract_json_span(completion.strip())
        if span is None:
            rewards.append(-1.0)
            continue

        total_len = len(completion.strip())
        json_len = span[1] - span[0]
        ratio = json_len / total_len if total_len > 0 else 0.0

        # Square ratio for stronger penalty — 0.5 ratio → 0.25 reward
        rewards.append(max(-1.0, ratio ** 2))

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    print(f"  [Conciseness Reward] scores=[{scores_str}]")
    return rewards
