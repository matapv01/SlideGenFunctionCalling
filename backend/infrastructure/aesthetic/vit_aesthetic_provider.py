import os
import torch
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification


class ViTAestheticProvider:
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = ViTForImageClassification.from_pretrained(
            'google/vit-base-patch16-224',
            num_labels=1,
            ignore_mismatched_sizes=True
        )
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def evaluate(self, image_path: str) -> float:
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.model(pixel_values=tensor).logits
            score = torch.sigmoid(logits).item()
        return score

vit_evaluator_instance = None
def get_vit_evaluator():
    global vit_evaluator_instance
    if vit_evaluator_instance is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        reward_model_path = os.path.join(project_root, "rl", "model", "best_model_pairwise.pt")
        if not os.path.exists(reward_model_path):
            reward_model_path = os.path.join(project_root, "best_model_pairwise.pt")
        vit_evaluator_instance = ViTAestheticProvider(model_path=reward_model_path, device="cpu")
    return vit_evaluator_instance
