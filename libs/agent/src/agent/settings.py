from __future__ import annotations

from base import BaseModel

class AgentSettings(BaseModel):
    api_keys: str
    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1500
    add_stop_token: list[str] = ['---\n', 'STOP_HERE']
    top_p: float = 1.0
    current_key_index: int = 0