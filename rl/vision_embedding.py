"""Visual embedding used only by RL rewards (not part of the backend pipeline)."""

from typing import List

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel


class DINOv2EmbeddingProvider:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
        self.model = AutoModel.from_pretrained("facebook/dinov2-base").to(self.device)
        self.model.eval()

    def get_embedding_np(self, image_path: str) -> np.ndarray:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    def get_embedding(self, image_path: str) -> List[float]:
        return self.get_embedding_np(image_path).tolist()
