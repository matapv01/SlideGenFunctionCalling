"""Frozen ViT-Base utility scorer trained with Bradley-Terry preferences.

Architecture/preprocessing follow models/vit/reward-model-vit-only.ipynb.
Higher utility means preferred. The bounded score is not a calibrated
probability of slide correctness; calibration stays fixed throughout a run.
"""
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

import torch
from PIL import Image
from torchvision import transforms
from transformers import ViTConfig, ViTForImageClassification

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MODEL = None
_MODEL_LOCK = Lock()


def _model_path() -> Path:
    configured = os.getenv("REWARD_MODEL_PATH")
    if configured:
        return Path(configured).expanduser()
    return PROJECT_ROOT / "models/vit/best_model_pairwise.pt"


def reward_model_settings() -> dict:
    """Serializable scoring contract, checked before loading weights."""
    center = float(os.getenv("RL_PAIRWISE_CENTER", "0"))
    temperature = float(os.getenv("RL_PAIRWISE_TEMPERATURE", "1"))
    batch_size = int(os.getenv("RL_VIT_BATCH_SIZE", "4"))
    if not math.isfinite(center):
        raise ValueError("RL_PAIRWISE_CENTER must be finite")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("RL_PAIRWISE_TEMPERATURE must be finite and positive")
    if batch_size < 1:
        raise ValueError("RL_VIT_BATCH_SIZE must be positive")
    return {
        "kind": "vit_base_patch16_224_pairwise",
        "direction": "higher_is_better",
        "mapping": "sigmoid((logit-center)/temperature)",
        "center": center, "temperature": temperature, "batch_size": batch_size,
        "dtype": "float32", "resize": [224, 224],
        "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225],
    }


@dataclass
class PairwiseRewardModel:
    model: torch.nn.Module
    device: torch.device
    transform: object
    center: float = 0.0
    temperature: float = 1.0
    batch_size: int = 4
    last_metrics: dict = field(default_factory=dict)


def _compatible_vit_state_dict(state_dict: dict, model: torch.nn.Module) -> dict:
    """Rename legacy Transformers ViT keys when loading under Transformers 5."""
    expected = set(model.state_dict())
    if set(state_dict) == expected:
        return state_dict

    attention_names = {"query": "q_proj", "key": "k_proj", "value": "v_proj"}
    migrated = {}
    for key, value in state_dict.items():
        key = re.sub(
            r"^vit\.encoder\.layer\.(\d+)\.attention\.attention\.(query|key|value)\.",
            lambda match: (
                f"vit.layers.{match.group(1)}.attention."
                f"{attention_names[match.group(2)]}."
            ),
            key,
        )
        key = re.sub(
            r"^vit\.encoder\.layer\.(\d+)\.attention\.output\.dense\.",
            r"vit.layers.\1.attention.o_proj.", key,
        )
        key = re.sub(
            r"^vit\.encoder\.layer\.(\d+)\.intermediate\.dense\.",
            r"vit.layers.\1.mlp.fc1.", key,
        )
        key = re.sub(
            r"^vit\.encoder\.layer\.(\d+)\.output\.dense\.",
            r"vit.layers.\1.mlp.fc2.", key,
        )
        key = re.sub(
            r"^vit\.encoder\.layer\.(\d+)\.layernorm_(before|after)\.",
            r"vit.layers.\1.layernorm_\2.", key,
        )
        if key in migrated:
            raise ValueError(f"ViT checkpoint key migration collision: {key}")
        migrated[key] = value

    if set(migrated) != expected:
        return state_dict
    return migrated


def _get_model() -> PairwiseRewardModel:
    """Load local weights strictly; no Hub download or pretrained initialization."""
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                settings = reward_model_settings()
                path = _model_path()
                if not path.is_file():
                    raise FileNotFoundError(
                        f"Pairwise aesthetic checkpoint not found: {path}. "
                        "Set REWARD_MODEL_PATH to the ViT-Base one-logit checkpoint."
                    )
                payload = torch.load(path, map_location="cpu", weights_only=True)
                if not isinstance(payload, dict):
                    raise ValueError(f"Invalid pairwise checkpoint payload: {path}")
                # Notebook best checkpoint is raw; latest_checkpoint wraps weights.
                state_dict = payload.get("model_state_dict", payload)
                if not isinstance(state_dict, dict):
                    raise ValueError(f"Invalid pairwise checkpoint state_dict: {path}")
                model = ViTForImageClassification(ViTConfig(
                    image_size=224, patch_size=16, num_channels=3,
                    hidden_size=768, num_hidden_layers=12,
                    num_attention_heads=12, intermediate_size=3072,
                    hidden_act="gelu", layer_norm_eps=1e-12,
                    qkv_bias=True, num_labels=1,
                ))
                model.load_state_dict(
                    _compatible_vit_state_dict(state_dict, model), strict=True
                )
                model.requires_grad_(False)
                device = torch.device(os.getenv("REWARD_MODEL_DEVICE", "cpu"))
                model.to(device)
                model.eval()
                _MODEL = PairwiseRewardModel(
                    model=model, device=device,
                    transform=transforms.Compose([
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(mean=settings["mean"], std=settings["std"]),
                    ]),
                    center=settings["center"], temperature=settings["temperature"],
                    batch_size=settings["batch_size"],
                )
    return _MODEL


def _evaluate_batch(model: PairwiseRewardModel, image_paths: list[Path]) -> list[float]:
    """Score screenshots in bounded batches, preserving input order."""
    model.last_metrics = {}
    if not image_paths:
        return []
    raw_batches = []
    with torch.inference_mode():
        for start in range(0, len(image_paths), model.batch_size):
            paths = image_paths[start:start + model.batch_size]
            tensors = []
            for image_path in paths:
                with Image.open(image_path) as image:
                    tensors.append(model.transform(image.convert("RGB")))
            pixel_values = torch.stack(tensors).to(model.device)
            logits = model.model(pixel_values=pixel_values).logits
            if logits.shape != (len(paths), 1):
                raise RuntimeError("Pairwise ViT must return exactly one logit per image")
            if not torch.isfinite(logits).all():
                raise RuntimeError("Pairwise ViT returned non-finite raw logits")
            raw_batches.append(logits[:, 0].float().cpu())
    raw = torch.cat(raw_batches)
    quality = torch.sigmoid((raw - model.center) / model.temperature)
    if not torch.isfinite(quality).all():
        raise RuntimeError("Pairwise ViT returned non-finite reward scores")
    model.last_metrics = {
        "raw_mean": raw.mean().item(), "raw_std": raw.std(unbiased=False).item(),
        "raw_min": raw.min().item(), "raw_max": raw.max().item(),
        "score_std": quality.std(unbiased=False).item(),
        "saturated_fraction": ((quality < 0.01) | (quality > 0.99)).float().mean().item(),
    }
    return quality.tolist()
