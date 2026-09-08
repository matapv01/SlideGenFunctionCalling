from backend.workflows.slidegen_workflow.tools.tool_des_xml import get_tool_by_name
from backend.workflows.slidegen_workflow.utils.deck_style import apply_deck_style_to_tool_call


DECK_STYLE = {
    "background_color": "#F8FAFC",
    "primary_color": "#0F172A",
    "secondary_color": "#475569",
    "accent_color": "#0D9488",
    "text_color": "#1F2937",
}


def test_dark_panel_text_is_changed_to_readable_colors() -> None:
    tool = get_tool_by_name("generate_split_content_slide_xml")
    call = {
        "name": tool.name,
        "arguments": {
            "title": "So sánh",
            "column_titles": ["Một", "Hai"],
            "column_descriptions": ["Nội dung một", "Nội dung hai"],
            "dark_panel_color": "#0F172A",
        },
    }

    styled = apply_deck_style_to_tool_call(call, [tool], DECK_STYLE)
    arguments = styled["arguments"]

    assert arguments["title_color"] == "#0D9488"
    assert arguments["heading_color"] == "#FFFFFF"
    assert arguments["body_color"] == "#FFFFFF"


def test_card_text_contrasts_with_dark_card_surface() -> None:
    tool = get_tool_by_name("generate_social_media_points_slide_xml")
    call = {
        "name": tool.name,
        "arguments": {
            "title": "Điểm chính",
            "cards": [{"title": "Một", "description": "Nội dung"}],
            "card_color": "#0F172A",
            "accent_color": "#0D9488",
            "star_color": "#1F2937",
        },
    }

    styled = apply_deck_style_to_tool_call(call, [tool], DECK_STYLE)
    arguments = styled["arguments"]

    assert arguments["card_title_color"] == "#FFFFFF"
    assert arguments["card_body_color"] == "#FFFFFF"
    assert arguments["star_color"] == "#111111"
