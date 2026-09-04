import asyncio
import json
import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.nodes import text_overflow_resolver
from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_client_snapshot_slide_xml,
)
from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root


def _presentation_with_overflow() -> ET.Element:
    root = ET.Element(
        "presentation",
        {
            "width": "1600",
            "height": "900",
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )
    slide = ET.SubElement(root, "slide", {"transition": "fade"})
    title = ET.SubElement(
        slide,
        "textbox",
        {
            "x": "100",
            "y": "100",
            "width": "240",
            "height": "45",
            "size": "28",
            "overflow": "clip",
        },
    )
    title.text = "A very long title that wraps into many lines inside a short box"
    formula = ET.SubElement(title, "math-field")
    formula.text = r"E = mc^2"
    body = ET.SubElement(
        slide,
        "textbox",
        {
            "x": "100",
            "y": "920",
            "width": "500",
            "height": "100",
            "size": "22",
            "overflow": "clip",
        },
    )
    body.text = "A body textbox positioned outside the slide"
    return root


def _fitted_presentation() -> ET.Element:
    root = ET.Element(
        "presentation",
        {
            "width": "1600",
            "height": "900",
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )
    slide = ET.SubElement(root, "slide")
    title = ET.SubElement(
        slide,
        "textbox",
        {
            "x": "100",
            "y": "100",
            "width": "600",
            "height": "80",
            "size": "22",
            "overflow": "clip",
        },
    )
    title.text = "Short title"
    formula = ET.SubElement(title, "math-field")
    formula.text = r"E = mc^2"
    body = ET.SubElement(
        slide,
        "textbox",
        {
            "x": "100",
            "y": "220",
            "width": "700",
            "height": "100",
            "size": "18",
            "overflow": "clip",
        },
    )
    body.text = "Short body"
    return root


def test_merge_shortened_arguments_preserves_visuals_lists_and_math() -> None:
    original = {
        "title": "A long but factual presentation title",
        "bullet_items": [
            "A long first supporting point",
            "Revenue follows the formula $R = p \\times q$",
        ],
        "image_url": "https://example.com/original.jpg",
        "accent_color": "#123456",
    }
    candidate = {
        "title": "Factual title",
        "bullet_items": [
            "First point",
            "Changed formula $R = 0$",
        ],
        "image_url": "https://example.com/changed.jpg",
        "accent_color": "#FFFFFF",
    }

    merged, changes = text_overflow_resolver._merge_shortened_arguments(
        original,
        candidate,
    )

    assert changes == 2
    assert merged["title"] == "Factual title"
    assert merged["bullet_items"][0] == "First point"
    assert merged["bullet_items"][1] == original["bullet_items"][1]
    assert merged["image_url"] == original["image_url"]
    assert merged["accent_color"] == original["accent_color"]

    unchanged, unchanged_count = text_overflow_resolver._merge_shortened_arguments(
        ["  Nested bullet"],
        ["Nested bullet"],
    )
    assert unchanged == ["  Nested bullet"]
    assert unchanged_count == 0


def test_browser_measurement_cannot_hide_source_slide_boundary() -> None:
    records = [
        {
            "id": "box-1",
            "reasons": ["slide_boundary"],
            "overflow": True,
            "line_count": 1,
            "max_lines": 1,
            "has_math_field": False,
        }
    ]
    browser_report = {
        "boxes": [
            {
                "id": "box-1",
                "overflow": False,
                "reasons": [],
                "line_count": 1,
                "max_lines": 1,
                "has_math_field": False,
            }
        ]
    }

    text_overflow_resolver._merge_browser_measurement(records, browser_report)

    assert records[0]["overflow"] is True
    assert records[0]["reasons"] == ["slide_boundary"]


def test_overflow_rewrites_complete_slide_and_regenerates_layout(monkeypatch) -> None:
    original_call = {
        "name": "example_slide_xml",
        "arguments": {
            "title": "A very long title that needs coordinated shortening",
            "body": "A long body that also needs coordinated shortening",
            "formula": r"$E = mc^2$",
            "image_url": "https://example.com/image.jpg",
        },
    }
    state = {
        "current_xml_content": ET.tostring(
            _presentation_with_overflow(),
            encoding="unicode",
        ),
        "current_slide_index": 0,
        "current_slide_text": "Complete source content",
        "current_tool_call": original_call,
        "current_tool_plan": [original_call, {"name": "search_ddgs_images"}],
        "retry_count": 0,
    }
    observed = {}

    def fake_rewriter(llm, current_state, records, tool_call, round_number):
        observed["box_texts"] = [record["text"] for record in records]
        observed["overflow_reasons"] = [record["reasons"] for record in records]
        return {
            "title": "Short title",
            "body": "Short body",
            "formula": r"$E = 0$",
            "image_url": "https://example.com/changed.jpg",
        }

    def fake_regenerator(tool_call, *, source_content, previous_root):
        observed["regenerated_arguments"] = tool_call["arguments"]
        observed["source_content"] = source_content
        root = _fitted_presentation()
        text_overflow_resolver._preserve_transition_attributes(
            previous_root,
            root,
        )
        return root

    monkeypatch.setattr(
        text_overflow_resolver,
        "_call_slide_rewriter",
        fake_rewriter,
    )
    monkeypatch.setattr(
        text_overflow_resolver,
        "_regenerate_slide",
        fake_regenerator,
    )

    result = asyncio.run(
        text_overflow_resolver.resolve_text_overflow(
            state,
            {
                "configurable": {
                    "llm": object(),
                    "capture_provider": None,
                    "text_overflow_max_rounds": 3,
                }
            },
        )
    )

    assert len(observed["box_texts"]) == 2
    assert any("slide_boundary" in reasons for reasons in observed["overflow_reasons"])
    assert observed["regenerated_arguments"] == {
        "title": "Short title",
        "body": "Short body",
        "formula": r"$E = mc^2$",
        "image_url": "https://example.com/image.jpg",
    }
    assert observed["source_content"] == "Complete source content"
    assert result["overflow_report"]["status"] == "ok"
    assert result["overflow_report"]["rewrites"] == 2
    assert result["overflow_report"]["protected_math_fields"] == 1
    assert result["overflow_report"]["skipped_math_fields"] == 0
    assert result["overflow_failed"] is False
    assert result["current_tool_call"]["arguments"]["title"] == "Short title"
    assert result["current_tool_plan"][0] == result["current_tool_call"]
    assert "Short body" in result["current_xml_content"]
    regenerated_slide = ET.fromstring(result["current_xml_content"]).find("./slide")
    assert regenerated_slide is not None
    assert regenerated_slide.get("transition") == "fade"


def test_last_round_rewrite_is_measured_before_failure(monkeypatch) -> None:
    original_call = {
        "name": "example_slide_xml",
        "arguments": {"title": "Long title", "body": "Long body"},
    }
    state = {
        "current_xml_content": ET.tostring(
            _presentation_with_overflow(),
            encoding="unicode",
        ),
        "current_slide_index": 0,
        "current_slide_text": "Complete source content",
        "current_tool_call": original_call,
        "current_tool_plan": [original_call],
        "retry_count": 0,
    }

    monkeypatch.setattr(
        text_overflow_resolver,
        "_call_slide_rewriter",
        lambda *args, **kwargs: {"title": "Short", "body": "Body"},
    )
    monkeypatch.setattr(
        text_overflow_resolver,
        "_regenerate_slide",
        lambda *args, **kwargs: _fitted_presentation(),
    )

    result = asyncio.run(
        text_overflow_resolver.resolve_text_overflow(
            state,
            {
                "configurable": {
                    "llm": object(),
                    "text_overflow_max_rounds": 1,
                }
            },
        )
    )

    assert result["overflow_report"]["status"] == "ok"
    assert result["overflow_report"]["overflowing_boxes"] == 0
    assert result["overflow_failed"] is False


def test_overflow_is_accepted_after_retry_budget_and_workflow_can_continue(monkeypatch) -> None:
    original_call = {
        "name": "example_slide_xml",
        "arguments": {
            "title": "A long title that needs shortening",
            "body": "A long body that needs shortening",
        },
    }
    state = {
        "current_xml_content": ET.tostring(
            _presentation_with_overflow(),
            encoding="unicode",
        ),
        "current_slide_index": 0,
        "current_slide_text": "Complete source content",
        "current_tool_call": original_call,
        "current_tool_plan": [original_call],
        # The executor/overflow retry budget is already exhausted.
        "retry_count": 2,
    }

    monkeypatch.setattr(
        text_overflow_resolver,
        "_call_slide_rewriter",
        lambda *args, **kwargs: {"title": "Short", "body": "Body"},
    )
    monkeypatch.setattr(
        text_overflow_resolver,
        "_regenerate_slide",
        lambda *args, **kwargs: _presentation_with_overflow(),
    )

    result = asyncio.run(
        text_overflow_resolver.resolve_text_overflow(
            state,
            {
                "configurable": {
                    "llm": object(),
                    "text_overflow_max_rounds": 1,
                }
            },
        )
    )

    assert result["overflow_failed"] is False
    assert result["overflow_report"]["status"] == "accepted_with_overflow"
    assert result["overflow_report"]["accepted_with_overflow"] is True
    assert result["overflow_report"]["overflowing_boxes"] > 0


def test_real_generator_is_reflowed_after_whole_slide_rewrite() -> None:
    original_details = [
        "Industry: Financial services and banking across multiple regional markets",
        "Team size: 300+ employees across product, sales, operations, and support",
        "Current setup: Disconnected productivity tools, shared drives, manual handoffs, and duplicated reporting",
        "Primary goals: Improve cross-team collaboration and standardize workflows",
        "  Improve cross-team collaboration while preserving local operating context",
        "  Standardize workflows across departments and reporting lines",
        "  Support growth while meeting regulatory and security requirements",
    ]
    revised_arguments = {
        "title": "Client",
        "subtitle": "Overview",
        "client_details": [
            "Industry: Banking",
            "Team: 300",
            "Setup: Unified",
            "Goals:",
            "  Collaborate",
            "  Standardize",
            "  Grow safely",
        ],
    }

    class FakeLLM:
        def __init__(self) -> None:
            self.messages = None

        def invoke(self, messages):
            self.messages = messages
            return {
                "text": json.dumps(
                    {"arguments": revised_arguments},
                    ensure_ascii=False,
                )
            }

    llm = FakeLLM()
    original_call = {
        "name": "generate_client_snapshot_slide_xml",
        "arguments": {
            "title": "Client snapshot, snapshot",
            "subtitle": "About Value Financials and its operating model across regional teams",
            "client_details": original_details,
        },
    }
    initial_xml = generate_client_snapshot_slide_xml(
        **original_call["arguments"]
    )
    assert any(
        record["overflow"]
        for record in analyze_xml_root(ET.fromstring(initial_xml))
    )

    result = asyncio.run(
        text_overflow_resolver.resolve_text_overflow(
            {
                "current_xml_content": initial_xml,
                "current_slide_index": 0,
                "current_slide_text": "Full client source",
                "current_tool_call": original_call,
                "current_tool_plan": [original_call],
                "retry_count": 0,
            },
            {
                "configurable": {
                    "llm": llm,
                    "capture_provider": None,
                    "text_overflow_max_rounds": 3,
                }
            },
        )
    )

    assert llm.messages is not None
    assert result["overflow_report"]["status"] == "ok"
    assert result["overflow_report"]["overflowing_boxes"] == 0
    assert result["current_tool_call"]["arguments"] == revised_arguments
    final_records = analyze_xml_root(
        ET.fromstring(result["current_xml_content"])
    )
    assert max(record["y"] + record["height"] for record in final_records) <= 900
