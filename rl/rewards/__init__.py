"""Reward functions used by direct GRPO training."""

from .composite_reward import (
    preflight_reward_runtime,
    set_text_embedder,
    slidegen_composite_reward,
)

__all__ = [
    "preflight_reward_runtime",
    "set_text_embedder",
    "slidegen_composite_reward",
]
