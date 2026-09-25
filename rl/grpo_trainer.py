"""GRPO trainer helpers for token-normalized DAPO with rollout accumulation."""

from __future__ import annotations

import json
from pathlib import Path

from trl import GRPOTrainer


class DapoAccumulationGRPOTrainer(GRPOTrainer):
    """Average token-normalized rollout losses over one optimizer update."""

    model_id: str | None = None
    dapo_accumulation_factor: int = 1

    def _compute_loss(self, model, inputs):
        loss = super()._compute_loss(model, inputs)
        if self.loss_type in {"dapo", "cispo", "vespo"} and model.training:
            steps_per_generation = self.args.steps_per_generation
            accumulated_steps = self.current_gradient_accumulation_steps
            update_factor = accumulated_steps / steps_per_generation
            loss = loss / max(1.0, update_factor)
        return loss

    def _checkpoint_metadata_path(self, checkpoint: str | Path) -> Path:
        return Path(checkpoint) / "rl_checkpoint_metadata.json"

    def _save_checkpoint(self, model, trial):
        super()._save_checkpoint(model, trial)
        if not self.is_world_process_zero():
            return
        checkpoint = Path(self.args.output_dir) / f"checkpoint-{self.state.global_step}"
        checkpoint.mkdir(parents=True, exist_ok=True)
        metadata = {
            "model_id": self.model_id,
            "loss_type": self.loss_type,
            "dapo_accumulation_factor": self.dapo_accumulation_factor,
        }
        self._checkpoint_metadata_path(checkpoint).write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

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
