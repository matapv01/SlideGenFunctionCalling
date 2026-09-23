from pathlib import Path

from langchain_core.runnables import RunnableLambda

from backend.application.services.document_rag_service import DocumentRagService
from backend.application.services.pdf_image_extractor import PdfImageExtractor
from backend.infrastructure.document_ai.document_ai_client import OcrResult
from backend.workflows.doc_workflow.nodes.content_splitter import split_content
from backend.workflows.doc_workflow.nodes.document_converter import convert_document


def test_ocr_markdown_marks_text_and_tables_as_atomic_sections():
    markdown, atomic_titles = DocumentRagService._ocr_markdown_with_metadata(
        OcrResult(
            text="OCR paragraph",
            tables=[{"rows": [["Name", "Value"], ["A", "1"]]}],
        ),
        document_title="sample.pdf",
    )

    assert markdown.startswith("# sample.pdf\n\n## OCR content")
    assert "### Table 1" in markdown
    assert atomic_titles == ["OCR content", "Table 1"]


def test_ocr_markdown_does_not_add_a_synthetic_image_count_section():
    markdown, atomic_titles = DocumentRagService._ocr_markdown_with_metadata(
        OcrResult(text="Paper text", pages=2),
        document_title="paper.pdf",
    )

    assert "embedded image occurrences" not in markdown
    assert "Embedded images" not in atomic_titles


def test_pdf_image_context_uses_nearest_layout_text_without_figure_rules():
    class _TextPage:
        def get_text_bounded(self, left, bottom, right, top):
            if top == 300:
                return "Figure 1. End-to-end GRACE processing pipeline."
            if bottom == 500:
                return "The method is introduced in the paragraph above."
            return ""

    anchor, nearby = PdfImageExtractor._spatial_text_context(
        text_page=_TextPage(),
        bounds=(100.0, 300.0, 500.0, 500.0),
        page_width=600.0,
        page_height=800.0,
    )

    assert anchor == "Figure 1. End-to-end GRACE processing pipeline."
    assert "paragraph above" in nearby
    assert "GRACE processing pipeline" in nearby


def test_pdf_caption_detection_supports_compact_and_multilingual_labels():
    occurrences = PdfImageExtractor._caption_occurrences(
        "Intro\r\nFig. 1. GRACE construction pipeline.\r\n"
        "Hình 2: Kiến trúc tổng thể\r\nConclusion"
    )

    assert [item["number"] for item in occurrences] == ["1", "2"]
    assert occurrences[0]["caption"].startswith("Fig. 1.")
    assert occurrences[1]["caption"].startswith("Hình 2:")


def test_pdf_visual_crop_keeps_caption_and_region_above_it():
    crop = PdfImageExtractor._visual_crop_bounds(
        (100.0, 580.0, 500.0, 595.0),
        page_width=600.0,
        page_height=800.0,
    )

    assert crop[0] == 0.0
    assert crop[1] < 580.0
    assert crop[2] == 600.0
    assert crop[3] == 800.0


def test_document_converter_marks_ocr_sections_as_atomic(tmp_path: Path):
    source = tmp_path / "ocr.txt"
    source.write_text(
        "# sample\n\n## OCR content\n\nOCR paragraph\n\n"
        "### Table 1\n\n| Name | Value |\n| --- | --- |\n| A | 1 |",
        encoding="utf-8",
    )

    state = convert_document(
        {
            "docx_file": str(source),
            "workflow_mode": "auto",
            "atomic_section_titles": ["OCR content", "Table 1"],
        }
    )

    root = state["document_structure"][0]
    ocr_content = root["children"][0]
    table = ocr_content["children"][0]
    assert ocr_content["atomic"] is True
    assert ocr_content["content_kind"] == "atomic"
    assert table["atomic"] is True
    assert table["content_kind"] == "atomic"


def test_content_splitter_does_not_send_atomic_ocr_sections_to_llm():
    def fail_if_called(_input):
        raise AssertionError("atomic OCR content must not be sent to the LLM")

    state = {
        "document_title": "sample",
        "document_structure_origin": "headings",
        "document_structure": [
            {
                "level": 1,
                "title": "sample",
                "content": "",
                "children": [
                    {
                        "level": 2,
                        "title": "OCR content",
                        "content": "x" * 20_000,
                        "children": [],
                        "atomic": True,
                        "content_kind": "table",
                    }
                ],
            }
        ],
        "document_preamble": "",
    }

    result = split_content(
        state,
        {"configurable": {"llm": RunnableLambda(fail_if_called)}},
    )

    assert result["document_structure"][0]["children"][0]["content"].startswith("x")
