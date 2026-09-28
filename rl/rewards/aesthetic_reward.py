import os
from pathlib import Path
from threading import Lock

import torch
from PIL import Image

from torchvision import transforms
from transformers import ViTConfig, ViTForImageClassification
from backend.infrastructure.aesthetic.vit_aesthetic_provider import ViTAestheticProvider


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MODEL = None
_MODEL_LOCK = Lock()


def _model_path() -> Path:
    configured = os.getenv("REWARD_MODEL_PATH")
    if configured:
        return Path(configured).expanduser()
    return PROJECT_ROOT / "ViT" / "experiments" / "vit_multilabel_small" / "best.pt"

def _get_model() -> ViTAestheticProvider:
    """Load the local trained checkpoint strictly, without a Hub dependency."""
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                path = _model_path()
                if not path.is_file():
                    raise FileNotFoundError(
                        f"Aesthetic checkpoint not found: {path}. "
                        "Set REWARD_MODEL_PATH to a compatible 5-label "
                        "ViT-small checkpoint."
                    )
                payload = torch.load(path, map_location="cpu", weights_only=True)
                expected_criteria = ["mau_nen", "mau_chu", "size_chu", "de_nhau", "tran_chu"]
                if not isinstance(payload, dict):
                    raise ValueError(f"Invalid aesthetic checkpoint payload: {path}")
                if payload.get("label_semantics") != "1=error,0=no_error":
                    raise ValueError(
                        "ViT checkpoint must declare label_semantics="
                        "'1=error,0=no_error' so the GRPO reward direction is known"
                    )
                if payload.get("criteria") != expected_criteria:
                    raise ValueError(
                        f"Unexpected ViT criteria/order: {payload.get('criteria')!r}"
                    )
                state_dict = payload.get("model_state_dict")
                if not isinstance(state_dict, dict):
                    raise ValueError(
                        f"Invalid aesthetic checkpoint state_dict: {path}"
                    )

                provider = ViTAestheticProvider.__new__(ViTAestheticProvider)
                provider.device = torch.device(
                    os.getenv("REWARD_MODEL_DEVICE", "cpu")
                )
                provider.model = ViTForImageClassification(
                    ViTConfig(
                        image_size=224,
                        patch_size=16,
                        num_channels=3,
                        hidden_size=384,
                        num_hidden_layers=12,
                        num_attention_heads=6,
                        intermediate_size=1536,
                        hidden_act="gelu",
                        layer_norm_eps=1e-12,
                        qkv_bias=True,
                        num_labels=5,
                    )
                )
                provider.model.load_state_dict(state_dict, strict=True)
                provider.model.requires_grad_(False)
                provider.model.to(provider.device)
                provider.model.eval()
                provider.transform = transforms.Compose(
                    [
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225],
                        ),
                    ]
                )
                provider.label_names = [
                    "Màu nền",
                    "Màu chữ",
                    "Size chữ",
                    "Bố cục",
                    "Tràn nội dung",
                ]
                _MODEL = provider
    return _MODEL


def _evaluate_batch(model: ViTAestheticProvider, image_paths: list[Path]) -> list[float]:
    """Return mean clean-slide probability for each rendered image."""
    if not image_paths:
        return []

    tensors = []
    for image_path in image_paths:
        with Image.open(image_path) as image:
            tensors.append(model.transform(image.convert("RGB")))
    pixel_values = torch.stack(tensors).to(model.device)
    with torch.inference_mode():
        logits = model.model(pixel_values=pixel_values).logits
        error_probabilities = torch.sigmoid(logits)
    if error_probabilities.shape != (len(image_paths), 5):
        raise RuntimeError(
            "Aesthetic ViT must return one five-label error vector per image"
        )
    quality = 1.0 - error_probabilities.mean(dim=1)
    if not torch.isfinite(quality).all():
        raise RuntimeError("Aesthetic ViT returned non-finite reward scores")
    return quality.clamp(0.0, 1.0).cpu().tolist()
