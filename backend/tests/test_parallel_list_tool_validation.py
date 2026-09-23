import pytest

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_roman_empire_history_cover_slide_xml,
    generate_split_content_slide_xml,
    generate_three_ideas_slide_xml,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    GenerateSplitContentSlideInput,
    GenerateThreeIdeasSlideInput,
)


def test_three_ideas_rejects_mismatched_list_lengths() -> None:
    with pytest.raises(ValueError, match="exactly three"):
        generate_three_ideas_slide_xml(
            idea_titles=["ONE", "TWO"],
            idea_descriptions=["One.", "Two.", "Three."],
        )


def test_history_cover_uses_current_tool_contract() -> None:
    xml = generate_roman_empire_history_cover_slide_xml(
        subtitle="History",
        title="A historical subject",
    )
    assert "<slide" in xml


def test_split_content_rejects_mismatched_column_count() -> None:
    with pytest.raises(ValueError, match="exactly two"):
        generate_split_content_slide_xml(
            column_titles=["ONE"],
            column_descriptions=["One."],
        )


def test_tool_schemas_reject_invalid_parallel_lists() -> None:
    with pytest.raises(ValueError):
        GenerateThreeIdeasSlideInput(
            title="THREE",
            idea_titles=["ONE", "TWO"],
            idea_descriptions=["One.", "Two."],
        )

    with pytest.raises(ValueError):
        GenerateSplitContentSlideInput(
            title="SPLIT",
            column_titles=["ONE"],
            column_descriptions=["One."],
        )
