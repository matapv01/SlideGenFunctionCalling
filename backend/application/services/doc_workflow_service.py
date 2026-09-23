"""Compatibility import for the pre-refactor DOCX service name.

New application code must depend on ``DocumentPreprocessingService``. This
module remains only so installed integrations using the old import path keep
working while the legacy generation endpoints are migrated.
"""

from typing import Any, Dict, Optional

from backend.application.services.document_preprocessing_service import (
    DocumentPreprocessingService,
)


class DocWorkflowService(DocumentPreprocessingService):
    """Deprecated name retained for legacy API integrations."""

    async def preprocess_docx(
        self,
        docx_file: str,
        workflow_mode: str = "auto_no_heading",
        slide_options: Optional[Dict[str, Any]] = None,
        callback=None,
    ) -> Dict[str, Any]:
        """Compatibility wrapper for the former DOCX-to-slides API."""
        return await self.preprocess_for_slide_generation(
            docx_file=docx_file,
            workflow_mode=workflow_mode,
            slide_options=slide_options,
            callback=callback,
        )


__all__ = ["DocWorkflowService"]
