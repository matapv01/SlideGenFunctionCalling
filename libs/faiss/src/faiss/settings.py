from __future__ import annotations

from base import BaseModel

from typing import Dict
from typing import List
from typing import Any

class FaissSettings(BaseModel):

    index_path: str
    tools_dict: Dict[str, List[Any]]
