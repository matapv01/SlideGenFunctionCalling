# File: backend/domain/ports/parser_provider.py

from typing import Protocol, Dict, Any, Tuple

class ParserProvider(Protocol):
    def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse document file to title and structured content.
        Returns: (title, hierarchical_structure)
        """
        ...