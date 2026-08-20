import os
import torch
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VIT_MODEL_DIR = PROJECT_ROOT / "models" / "vit"
DEFAULT_VIT_MODEL_FILENAME = "best_model_multilabel_DX_10_0.77.pt"


def _resolve_vit_model_path() -> Path:
    """Resolve the ViT checkpoint from the project model directory."""
    configured_dir = os.getenv("VIT_MODEL_DIR")
    model_dir = Path(configured_dir).expanduser() if configured_dir else DEFAULT_VIT_MODEL_DIR
    if not model_dir.is_absolute():
        model_dir = (PROJECT_ROOT / model_dir).resolve()

    model_filename = os.getenv("VIT_MODEL_FILENAME", DEFAULT_VIT_MODEL_FILENAME)
    model_path = model_dir / model_filename
    if not model_path.is_file():
        raise FileNotFoundError(
            f"ViT checkpoint not found at '{model_path}'. "
            "Place the checkpoint in 'models/vit' or configure "
            "VIT_MODEL_DIR and VIT_MODEL_FILENAME."
        )
    return model_path


class ViTAestheticProvider:
    def __init__(self, model_path: str = None, device: str = None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        print(f"Initializing ViTAestheticProvider on {self.device}")
        
        # Set HuggingFace mirror to avoid connection timeout issues
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        
        self.model = ViTForImageClassification.from_pretrained(
            'WinKawaks/vit-small-patch16-224',
            num_labels=5,
            ignore_mismatched_sizes=True
        )
        
        if model_path and os.path.exists(model_path):
            print(f"Loading weights from {model_path}")
            state_dict = torch.load(model_path, map_location=self.device)
            
            # Map keys if they come from a different ViT implementation
            new_state_dict = {}
            for k, v in state_dict.items():
                nk = k.replace('vit.layers.', 'vit.encoder.layer.')
                nk = nk.replace('.attention.q_proj.', '.attention.attention.query.')
                nk = nk.replace('.attention.k_proj.', '.attention.attention.key.')
                nk = nk.replace('.attention.v_proj.', '.attention.attention.value.')
                nk = nk.replace('.attention.o_proj.', '.attention.output.dense.')
                nk = nk.replace('.mlp.fc1.', '.intermediate.dense.')
                nk = nk.replace('.mlp.fc2.', '.output.dense.')
                new_state_dict[nk] = v

            self.model.load_state_dict(new_state_dict, strict=False)
        else:
            print(f"Warning: model_path '{model_path}' not found. Using untrained base model.")
            
        self.model.to(self.device)
        self.model.eval()

        # Augmentation for testing/inference
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.label_names = ['Màu nền', 'Màu chữ', 'Size chữ', 'Bố cục', 'Tràn nội dung']
        self.thresholds = np.array([0.9] * 5)

    def evaluate(self, image_path: str) -> Tuple[bool, List[str], Dict[str, float]]:
        """
        Dự đoán chất lượng slide từ đường dẫn ảnh.
        Returns:
            is_accept: True nếu không có lỗi nào, False nếu có lỗi
            errors: Danh sách các lỗi (ví dụ: ['Màu chữ', 'Tràn nội dung'])
            detailed_scores: Xác suất (từ 0-1) của từng nhãn (càng gần 1 càng tốt, gần 0 là lỗi)
        """
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(pixel_values=pixel_values).logits
            probs = torch.sigmoid(logits).cpu().numpy()[0]

        detected_errors = [
            self.label_names[i] for i, p in enumerate(probs) if p < self.thresholds[i]
        ]
        
        detailed_scores = {self.label_names[i]: float(probs[i]) for i in range(5)}
        is_accept = len(detected_errors) == 0

        return is_accept, detected_errors, detailed_scores


# Singleton pattern
_vit_evaluator_instance = None

def get_vit_evaluator() -> ViTAestheticProvider:
    global _vit_evaluator_instance
    if _vit_evaluator_instance is None:
        model_path = _resolve_vit_model_path()
        _vit_evaluator_instance = ViTAestheticProvider(model_path=str(model_path))
    return _vit_evaluator_instance
