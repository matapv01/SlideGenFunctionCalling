"""GRPO trainer helpers for token-normalized DAPO with rollout accumulation."""

from __future__ import annotations

import json
from pathlib import Path

from trl import GRPOTrainer


class DapoAccumulationGRPOTrainer(GRPOTrainer):
    """Average token-normalized rollout losses over one optimizer update."""

    model_id: str | None = None
    dapo_accumulation_factor: int = 1
    training_contract: str | None = None

    def _compute_loss(self, model, inputs):
        loss = super()._compute_loss(model, inputs)
        if self.loss_type in {"dapo", "cispo", "vespo"} and model.training:
            steps_per_generation = self.args.steps_per_generation
            accumulated_steps = self.current_gradient_accumulation_steps
            if accumulated_steps % steps_per_generation:
                raise RuntimeError(
                    "Token-normalized loss requires each optimizer update to contain "
                    "whole generation windows; check the GRPO sampler and accumulation settings"
                )
            generation_windows = accumulated_steps // steps_per_generation
            loss = loss / generation_windows
        return loss

    def _checkpoint_metadata_path(self, checkpoint: str | Path) -> Path:
        return Path(checkpoint) / "rl_checkpoint_metadata.json"

    def _save_checkpoint(self, model, trial):
        if not self.training_contract:
            raise ValueError("Cannot save GRPO checkpoint without a training contract")
        super()._save_checkpoint(model, trial)
        if not self.is_world_process_zero():
            return
        checkpoint = Path(self.args.output_dir) / f"checkpoint-{self.state.global_step}"
        checkpoint.mkdir(parents=True, exist_ok=True)
        metadata = {
            "model_id": self.model_id,
            "loss_type": self.loss_type,
            "dapo_accumulation_factor": self.dapo_accumulation_factor,
            "training_contract": self.training_contract,
        }
        path = self._checkpoint_metadata_path(checkpoint)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        temporary.replace(path)

    def _load_from_checkpoint(self, resume_from_checkpoint, model=None):
        metadata_path = self._checkpoint_metadata_path(resume_from_checkpoint)
        if not metadata_path.is_file():
            raise ValueError(
                f"Checkpoint is missing RL metadata and cannot be resumed safely: "
                f"{resume_from_checkpoint}"
            )
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("Checkpoint RL metadata must be a JSON object")
        if not self.training_contract or metadata.get("training_contract") != self.training_contract:
            raise ValueError("Checkpoint data, reward, code, or training settings do not match this run")
        if metadata.get("model_id") != self.model_id:
            raise ValueError(
                f"Checkpoint base model {metadata.get('model_id')!r} does not match "
                f"configured model {self.model_id!r}"
            )
        if metadata.get("loss_type") != self.loss_type:
            raise ValueError("Checkpoint loss type does not match the current run")
        if metadata.get("dapo_accumulation_factor") != self.dapo_accumulation_factor:
            raise ValueError(
                "Checkpoint DAPO accumulation factor does not match the current run"
            )
        super()._load_from_checkpoint(resume_from_checkpoint, model=model)
