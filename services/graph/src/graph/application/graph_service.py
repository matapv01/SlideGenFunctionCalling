from __future__ import annotations

from base import BaseModel
from base import BaseService

from logger import get_logger

logger = get_logger(__name__)

class GraphInput(BaseModel):
    pass


class GraphOutput(BaseModel):
    pass

class GraphService(BaseService):
    pass