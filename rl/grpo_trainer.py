"""GRPO trainer extension with an actual historical baseline fallback."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass

import torch
from trl import GRPOTrainer


@dataclass
class HistoricalRewardBaseline:
    decay: float = 0.99
    sigma_floor: float = 0.05
    value: float | None = None
    scale: float | None = None

    def update(self, rewards: torch.Tensor) -> tuple[float | None, float]:
        finite = rewards[torch.isfinite(rewards)]
        if finite.numel() == 0:
            return self.value, self.scale or self.sigma_floor
        previous = self.value
        mean = float(finite.mean().item())
        sigma = float(finite.std(unbiased=False).item()) if finite.numel() > 1 else 0.0
        if self.value is None:
            self.value = mean
            self.scale = max(sigma, self.sigma_floor)
        else:
            self.value = self.decay * self.value + (1.0 - self.decay) * mean
            self.scale = self.decay * self.scale + (1.0 - self.decay) * max(
                sigma, self.sigma_floor
            )
        return previous, max(self.scale or self.sigma_floor, self.sigma_floor)


class HistoricalBaselineGRPOTrainer(GRPOTrainer):
    """Use a historical baseline only for groups whose reward variance collapsed."""

    historical_baseline: HistoricalRewardBaseline | None = None
    _latest_rewards_per_func: torch.Tensor | None = None

    def _baseline_path(self, checkpoint: str | Path) -> Path:
        return Path(checkpoint) / "historical_reward_baseline.json"

    def _save_checkpoint(self, model, trial):
        super()._save_checkpoint(model, trial)
        baseline = self.historical_baseline
        if baseline is None or not self.is_world_process_zero():
            return
        checkpoint = Path(self.args.output_dir) / (
            f"checkpoint-{self.state.global_step}"
        )
        checkpoint.mkdir(parents=True, exist_ok=True)
        self._baseline_path(checkpoint).write_text(
            json.dumps(
                {
                    "decay": baseline.decay,
                    "sigma_floor": baseline.sigma_floor,
                    "value": baseline.value,
                    "scale": baseline.scale,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _load_from_checkpoint(self, resume_from_checkpoint, model=None):
        super()._load_from_checkpoint(resume_from_checkpoint, model=model)
        path = self._baseline_path(resume_from_checkpoint)
        if self.historical_baseline is not None and path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            for field in ("decay", "sigma_floor", "value", "scale"):
                if field in payload:
                    setattr(self.historical_baseline, field, payload[field])

    def _calculate_rewards(self, *args, **kwargs):
        rewards = super()._calculate_rewards(*args, **kwargs)
        self._latest_rewards_per_func = rewards.detach()
        return rewards

    def _generate_and_score_completions(self, *args, **kwargs):
        output = super()._generate_and_score_completions(*args, **kwargs)
        if not self.model.training:
            return output
        baseline = self.historical_baseline
        per_func = self._latest_rewards_per_func
        if baseline is None or per_func is None:
            return output

        weights = self.reward_weights.to(per_func.device).unsqueeze(0)
        unscorable = torch.isnan(per_func).all(dim=1)
        rewards = (per_func * weights).nansum(dim=1)
        rewards[unscorable] = torch.nan
        generations = self.num_generations
        if rewards.numel() % generations:
            return output

        grouped = rewards.view(-1, generations)
        group_std = torch.nan_to_num(
            grouped.std(dim=1, unbiased=False), nan=0.0
        )
        collapsed = group_std < baseline.sigma_floor
        previous_value, historical_scale = baseline.update(rewards)
        if previous_value is None or not collapsed.any():
            return output

        fallback = ((grouped - previous_value) / historical_scale).clamp(-5.0, 5.0)
        global_advantages = torch.where(
            collapsed.unsqueeze(1),
            torch.nan_to_num(fallback, nan=0.0),
            torch.zeros_like(fallback),
        ).reshape(-1)

        local_count = output["advantages"].numel()
        start = self.accelerator.process_index * local_count
        stop = start + local_count
        local_fallback = global_advantages[start:stop]
        local_collapsed = (
            collapsed.unsqueeze(1)
            .expand(-1, generations)
            .reshape(-1)[start:stop]
        )
        output["advantages"] = torch.where(
            local_collapsed,
            local_fallback.to(output["advantages"].device),
            output["advantages"],
        )
        mode = "train" if self.model.training else "eval"
        self._metrics[mode]["ema_fallback_fraction"].append(
            float(local_collapsed.float().mean().item())
        )
        return output
