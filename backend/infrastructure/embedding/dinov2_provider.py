from typing import List
import os
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModel


class DINOv2EmbeddingProvider:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
        self.model = AutoModel.from_pretrained('facebook/dinov2-base').to(self.device)
        self.model.eval()

    def get_embedding(self, image_path: str) -> List[float]:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embedding.tolist()

    def get_embedding_np(self, image_path: str) -> np.ndarray:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embedding

    def cosine_similarity(self, image_path_a: str, image_path_b: str) -> float:
        emb_a = self.get_embedding_np(image_path_a)
        emb_b = self.get_embedding_np(image_path_b)
        dot = np.dot(emb_a, emb_b)
        norm = np.linalg.norm(emb_a) * np.linalg.norm(emb_b)
        return float(dot / norm) if norm > 0 else 0.0
