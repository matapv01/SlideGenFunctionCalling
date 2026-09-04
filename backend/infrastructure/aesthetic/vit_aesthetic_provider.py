import os
import torch
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification


def _remap_state_dict(state_dict: dict) -> dict:
    """
    Remap key names from Kaggle training format to HuggingFace transformers format.
    
    Kaggle format:  vit.layers.X.attention.{q,k,v,o}_proj  / vit.layers.X.layernorm_{before,after} / vit.layers.X.mlp.fc{1,2}
    HF format:      vit.encoder.layer.X.attention.attention.{query,key,value} / vit.encoder.layer.X.attention.output.dense
                    vit.encoder.layer.X.layernorm_before / vit.encoder.layer.X.layernorm_after
                    vit.encoder.layer.X.intermediate.dense / vit.encoder.layer.X.output.dense
    """
    new_sd = {}
    for key, value in state_dict.items():
        new_key = key
        
        # Map vit.layers.X -> vit.encoder.layer.X
        if key.startswith("vit.layers."):
            new_key = key.replace("vit.layers.", "vit.encoder.layer.", 1)
            
            # Map attention projections
            new_key = new_key.replace(".attention.q_proj.", ".attention.attention.query.")
            new_key = new_key.replace(".attention.k_proj.", ".attention.attention.key.")
            new_key = new_key.replace(".attention.v_proj.", ".attention.attention.value.")
            new_key = new_key.replace(".attention.o_proj.", ".attention.output.dense.")
            
            # Map MLP layers
            new_key = new_key.replace(".mlp.fc1.", ".intermediate.dense.")
            new_key = new_key.replace(".mlp.fc2.", ".output.dense.")
        
        new_sd[new_key] = value
    
    return new_sd


class ViTAestheticProvider:
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = ViTForImageClassification.from_pretrained(
            'WinKawaks/vit-small-patch16-224',
            num_labels=5,
            ignore_mismatched_sizes=True
        )
        if model_path and os.path.exists(model_path):
            raw_sd = torch.load(model_path, map_location=self.device)
            # Handle checkpoint dict vs raw state_dict
            if isinstance(raw_sd, dict) and "model_state_dict" in raw_sd:
                raw_sd = raw_sd["model_state_dict"]
            remapped_sd = _remap_state_dict(raw_sd)
            self.model.load_state_dict(remapped_sd)
            print(f"[ViT] Loaded trained weights from: {model_path}")
        else:
            print(f"[ViT] WARNING: No trained weights found at '{model_path}', using base pretrained weights only.")
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 5 tiêu chuẩn đánh giá thẩm mỹ chuẩn từ notebook huấn luyện:
        # ['Màu nền', 'Màu chữ', 'Size chữ', 'Đè nhau', 'Tràn nội dung']
        # Giá trị: gần 1.0 = Tốt (Đạt), dưới 0.5 = Lỗi (Xấu)
        self.criteria_meta = [
            {
                "name": "Màu nền",
                "alias": "Background Quality",
                "error_desc": "Màu nền xấu, tương phản kém hoặc họa tiết làm chìm nội dung",
                "threshold": 0.5
            },
            {
                "name": "Màu chữ",
                "alias": "Text Readability",
                "error_desc": "Màu chữ bị chìm vào nền, độ tương phản kém, khó đọc",
                "threshold": 0.5
            },
            {
                "name": "Size chữ",
                "alias": "Text Size",
                "error_desc": "Kích thước chữ quá nhỏ hoặc không có phân cấp tiêu đề / nội dung rõ ràng",
                "threshold": 0.5
            },
            {
                "name": "Đè nhau",
                "alias": "Layout/Overlap",
                "error_desc": "Bố cục lộn xộn, các khối thẻ (card), chữ hoặc hình bị đè chồng lấn lên nhau",
                "threshold": 0.5
            },
            {
                "name": "Tràn nội dung",
                "alias": "Content Overflow",
                "error_desc": "Chữ hoặc phần tử bị tràn ra khỏi mép khung slide (vượt tỷ lệ 16:9)",
                "threshold": 0.5
            },
        ]
        self.criteria_names = [c["name"] for c in self.criteria_meta]

    def evaluate(self, image_path: str) -> dict:
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.model(pixel_values=tensor).logits
            probs = torch.sigmoid(logits)[0].cpu().tolist()

        scores = {}
        detected_errors = []
        error_details = []
        report_lines = []

        for meta, prob in zip(self.criteria_meta, probs):
            name = meta["name"]
            score = round(float(prob), 4)
            is_good = score >= meta["threshold"]
            scores[name] = score

            if not is_good:
                detected_errors.append(name)
                error_details.append(f"{name} ({score:.3f} < {meta['threshold']}): {meta['error_desc']}")
                report_lines.append(f"  [x] {name}: {score:.3f} -> LỖI ({meta['error_desc']})")
            else:
                report_lines.append(f"  [v] {name}: {score:.3f} -> ĐẠT")

        overall_score = round(sum(probs) / len(probs), 4)
        is_pass = len(detected_errors) == 0

        summary = (
            "Slide Đẹp (Đạt chuẩn thẩm mỹ)"
            if is_pass
            else f"Phát hiện {len(detected_errors)} lỗi: {', '.join(detected_errors)}"
        )

        formatted_report = (
            f"[ViT Thẩm Mỹ] Điểm TB: {overall_score:.3f}/1.0 | Kết luận: {summary}\n"
            + "\n".join(report_lines)
        )

        return {
            "overall_score": overall_score,
            "scores": scores,
            "detected_errors": detected_errors,
            "error_details": error_details,
            "is_pass": is_pass,
            "summary": summary,
            "formatted_report": formatted_report,
            # Giữ tương thích ngược với code cũ mong đợi dict[str, float]
            **scores
        }

