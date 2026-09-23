"""Compatibility adapter for the old DOCX generation endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.application.services.document_preprocessing_service import (
    DocumentPreprocessingService,
)
from backend.application.services.slidegen_workflow_service import (
    SlideGenWorkflowService,
)


class LegacyDocxGenerationService:
    """Compose DOCX preprocessing with the canonical chunk renderer.

    This adapter exists only for ``/generate/docx`` and its SSE companion.
    It keeps their contract stable while ensuring they no longer make the
    renderer understand DOCX modes or own a second slide-generation graph.
    """

    def __init__(
        self,
        document_preprocessor: DocumentPreprocessingService,
        slide_workflow: SlideGenWorkflowService,
    ) -> None:
        self.document_preprocessor = document_preprocessor
        self.slide_workflow = slide_workflow

    def is_available(self) -> bool:
        return (
            self.document_preprocessor.is_available()
            and self.slide_workflow.is_available()
        )
    async def generate_from_docx(
        self,
        *,
        docx_path: str,
        output_folder: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """Preprocess DOCX and send its chunks to the canonical renderer."""
        slide_options: Dict[str, Any] = dict(kwargs.pop("slide_options", {}) or {})
        callback = kwargs.pop("callback", None)
        workflow_mode = str(
            slide_options.get("workflow_mode", "auto_no_heading")
        )

        doc_state = await self.document_preprocessor.preprocess_for_slide_generation(
            docx_file=docx_path,
            workflow_mode=workflow_mode,
            slide_options=slide_options,
            callback=callback,
        )

        prepared_slide_count = len(doc_state.get("slide_chunks") or [])
        try:
            max_docx_slides = int(slide_options.get("max_docx_slides", -1))
        except (TypeError, ValueError):
            max_docx_slides = -1
        if max_docx_slides != -1 and prepared_slide_count > max_docx_slides:
            raise ValueError(
                f"Tài liệu quá dài: nội dung được chia thành {prepared_slide_count} "
                f"slide, vượt quá giới hạn {max_docx_slides} slide của gói hiện tại. "
                "Vui lòng rút ngắn tài liệu hoặc nâng cấp lên Ultra rồi thử lại."
            )

        return await self.slide_workflow.generate_from_chunks(
            slide_chunks=doc_state.get("slide_chunks", []),
            title=str(doc_state.get("document_title") or "Untitled presentation"),
            output_folder=output_folder,
            callback=callback,
            slide_options=slide_options,
            slide_positions=doc_state.get("slide_positions", []),
            slide_context_maps=doc_state.get("slide_context_maps", []),
            section_ids=doc_state.get("section_ids", []),
            max_retries_per_slide=kwargs.pop("max_retries_per_slide", 1),
        )
