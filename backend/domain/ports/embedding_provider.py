from typing import List, Protocol


class EmbeddingProvider(Protocol):
    def __init__(self, device: str = "cpu"):
        ...

    def get_embedding(self, image_path: str) -> List[float]:
        ...
