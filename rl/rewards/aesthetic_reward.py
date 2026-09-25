import concurrent.futures
import os
import uuid
from pathlib import Path
from threading import Lock

import torch
from PIL import Image

from torchvision import transforms
from transformers import ViTConfig, ViTForImageClassification
from backend.infrastructure.aesthetic.vit_aesthetic_provider import ViTAestheticProvider
from rl.slidegen_adapter import execute_tool, parse_tool_call_json, render_xml_to_png


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


def _render_completion(task: tuple[int, str, Path]) -> tuple[int, Path, str | None]:
    idx, completion, temp_dir = task
    temp_img_path = temp_dir / f"aesthetic_{os.getpid()}_{uuid.uuid4().hex}.png"
    try:
        tool_call = parse_tool_call_json(completion)
        if not tool_call:
            return idx, temp_img_path, "invalid tool call"
        xml_content = execute_tool(tool_call)
        render_xml_to_png(xml_content, str(temp_img_path))
        return idx, temp_img_path, None
    except Exception as exc:
        return idx, temp_img_path, str(exc)


def _evaluate_batch(model: ViTAestheticProvider, image_paths: list[Path]) -> list[float]:
    tensors = []
    for image_path in image_paths:
        with Image.open(image_path) as image:
            tensors.append(model.transform(image.convert("RGB")))
    pixel_values = torch.stack(tensors).to(model.device)
    with torch.no_grad():
        logits = model.model(pixel_values=pixel_values).logits
        error_probabilities = torch.sigmoid(logits)
    # The checkpoint labels 1 as an error. GRPO maximizes reward, so reward
    # should be the probability of a clean slide, not the probability of error.
    quality = 1.0 - error_probabilities.mean(dim=1)
    return quality.detach().cpu().tolist()


def slide_aesthetics_reward(prompts, completions, **kwargs):
    del prompts, kwargs
    rewards = [-1.0] * len(completions)
    temp_dir = PROJECT_ROOT / "rl" / "temp_rl_renders"
    temp_dir.mkdir(parents=True, exist_ok=True)
    sample_errors = []
    render_workers = max(
        1,
        min(int(os.getenv("RL_REWARD_RENDER_WORKERS", "4")), len(completions) or 1),
    )
    tasks = [(idx, completion, temp_dir) for idx, completion in enumerate(completions)]

    if tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=render_workers) as executor:
            rendered = list(executor.map(_render_completion, tasks))
    else:
        rendered = []

    valid = []
    try:
        for idx, image_path, error in rendered:
            if error is None:
                valid.append((idx, image_path))
            elif len(sample_errors) < 3:
                sample_errors.append(f"Gen {idx}: {error}")

        if valid:
            try:
                scores = _evaluate_batch(_get_model(), [path for _, path in valid])
                for (idx, _), score in zip(valid, scores):
                    rewards[idx] = float(score)
            except Exception as exc:
                sample_errors.append(f"ViT batch: {exc}")
    finally:
        for _, image_path, _ in rendered:
            image_path.unlink(missing_ok=True)

    print(
        f"  [Aesthetic Reward] workers={render_workers} "
        f"scores=[{' '.join(f'{score:.3f}' for score in rewards)}]"
        + (f" errors={sample_errors[:3]}" if sample_errors else "")
    )
    return rewards
