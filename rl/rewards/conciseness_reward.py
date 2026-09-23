import json
import re


_TOOL_CALL_PATTERN = re.compile(
    r"<tool_call>\s*(\{.*\})\s*</tool_call>",
    re.DOTALL,
)


def conciseness_reward(prompts, completions, **kwargs):
    """Reward one exact serialized tool call and penalize surrounding prose."""
    del prompts, kwargs
    rewards = []
    for completion in completions:
        stripped = completion.strip()
        match = _TOOL_CALL_PATTERN.search(stripped)
        if match is None:
            rewards.append(-1.0)
            continue

        try:
            payload = json.loads(match.group(1))
        except (TypeError, ValueError):
            rewards.append(-1.0)
            continue
        if not isinstance(payload, dict) or not payload.get("name"):
            rewards.append(-1.0)
            continue
        arguments = payload.get("arguments")
        if not isinstance(arguments, dict):
            rewards.append(-1.0)
            continue

        serialized_call = match.group(0)
        ratio = len(serialized_call) / max(1, len(stripped))
        rewards.append(max(-1.0, min(1.0, ratio**2)))

    scores_str = " ".join(f"{score:.3f}" for score in rewards)
    print(f"  [Conciseness Reward] scores=[{scores_str}]")
    return rewards
