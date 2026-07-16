from typing import Protocol


class AestheticProvider(Protocol):
    def __init__(self, model_path: str = None, device: str = "cpu"):
        ...

    def evaluate(self, image_path: str) -> float:
        ...
