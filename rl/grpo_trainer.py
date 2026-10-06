"""GRPO trainer helpers for token-normalized DAPO with rollout accumulation."""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import torch
from trl import GRPOTrainer
from transformers import TrainerCallback, set_seed


class ValidationStopCallback(TrainerCallback):
    """Stop after held-out reward plateaus for several evaluations."""

    def __init__(self, *, metric_name="eval_reward", patience=4, threshold=0.02,
                 min_steps=0, state_path=None):
        self.metric_name = metric_name
        self.patience = max(1, int(patience))
        self.threshold = max(0.0, float(threshold))
        self.min_steps = max(0, int(min_steps))
        self.state_path = Path(state_path) if state_path else None
        self.best_metric = float("-inf")
        self.bad_evaluations = 0
        self.saved_step = 0
        if self.state_path and self.state_path.is_file():
            try:
                saved = json.loads(self.state_path.read_text(encoding="utf-8"))
                if saved.get("metric_name") == self.metric_name:
                    self.best_metric = float(saved.get("best_metric", self.best_metric))
                    self.bad_evaluations = int(saved.get("bad_evaluations", 0))
                    self.saved_step = int(saved.get("step", 0))
            except (OSError, ValueError, TypeError):
                pass

    def on_train_begin(self, args, state, control, **kwargs):
        # A crash can leave controller state from an evaluation after the most
        # recent complete checkpoint. Discard that state when resuming earlier.
        if self.saved_step > int(state.global_step):
            self.bad_evaluations = 0
            checkpoint_best = getattr(state, "best_metric", None)
            self.best_metric = float(checkpoint_best) if checkpoint_best is not None else float("-inf")
            self.saved_step = int(state.global_step)
        return control

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        value = (metrics or {}).get(self.metric_name)
        if value is None or not np.isfinite(float(value)):
            return control
        value = float(value)
        improved = value > self.best_metric + self.threshold
        if improved:
            self.best_metric = value
            self.bad_evaluations = 0
        elif state.global_step >= self.min_steps:
            self.bad_evaluations += 1
        record = {
            "step": int(state.global_step), "metric": self.metric_name,
            "metric_name": self.metric_name, "value": value,
            "best": self.best_metric, "best_metric": self.best_metric,
            "improved": improved,
            "bad_evaluations": self.bad_evaluations, "patience": self.patience,
            "min_steps": self.min_steps,
        }
        if self.state_path:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.state_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(record, indent=2), encoding="utf-8")
            temporary.replace(self.state_path)
        if state.global_step >= self.min_steps and self.bad_evaluations >= self.patience:
            control.should_training_stop = True
        return control


class DapoAccumulationGRPOTrainer(GRPOTrainer):
    """Average token-normalized rollout losses over one optimizer update."""

    model_id: str | None = None
    dapo_accumulation_factor: int = 1
    training_contract: str | None = None

    def evaluate(self, *args, **kwargs):
        """Use the same sampling RNG at each held-out evaluation."""
        python_state = random.getstate()
        numpy_state = np.random.get_state()
        torch_state = torch.random.get_rng_state()
        cuda_states = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
        try:
            set_seed(int(getattr(self.args, "eval_seed", self.args.seed)))
            return super().evaluate(*args, **kwargs)
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
            torch.random.set_rng_state(torch_state)
            if cuda_states is not None:
                torch.cuda.set_rng_state_all(cuda_states)

    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        """Score held-out rollouts only; the GRPO surrogate loss needs full-vocab logits and is not an eval metric."""
        self._prepare_inputs(inputs)
        return torch.zeros((), device=self.accelerator.device), None, None

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
