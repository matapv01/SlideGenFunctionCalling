import inspect

from backend.application.services.slidegen_workflow_service import (
    SlideGenWorkflowService,
)
from backend.domain.canonical_chunks import normalize_canonical_chunks
from backend.workflows.slidegen_workflow import main as slide_workflow_main


def test_canonical_chunks_discard_misaligned_positional_metadata():
    normalized = normalize_canonical_chunks(
        [{"heading": "First"}, {"heading": "Second"}],
        slide_positions=[["1"]],
        slide_context_maps=["first", "second"],
        section_ids=["one", "two"],
    )

    assert [chunk["heading"] for chunk in normalized["slide_chunks"]] == [
        "First",
        "Second",
    ]
    assert normalized["slide_positions"] == []
    assert normalized["slide_context_maps"] == ["first", "second"]
    assert normalized["section_ids"] == ["one", "two"]


def test_renderer_has_one_canonical_entry_point_and_no_manual_dependency():
    constructor = inspect.signature(SlideGenWorkflowService.__init__)

    assert "document_preprocessor" not in constructor.parameters
    assert hasattr(slide_workflow_main, "run_canonical_slide_workflow")
    assert "manual_workflow" not in inspect.getsource(slide_workflow_main)
