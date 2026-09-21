from pathlib import Path

from langchain_core.runnables import RunnableLambda

from backend.application.services.document_rag_service import DocumentRagService
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


def test_ocr_markdown_records_exact_pdf_image_count():
    markdown, atomic_titles = DocumentRagService._ocr_markdown_with_metadata(
        OcrResult(text="Paper text", pages=2),
        document_title="paper.pdf",
        pdf_image_count=18,
    )

    assert "exactly 18 embedded image occurrences" in markdown
    assert "Embedded images" in atomic_titles


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
