import asyncio
import xml.etree.ElementTree as ET

import pytest

from backend.workflows.slidegen_workflow.utils.xml_contrast import (
    contrast_ratio,
    enforce_xml_text_contrast,
)


def _transition_xml() -> str:
    return '''<presentation width="1600" height="900">
  <slide background="#F8FAFC">
    <image src="https://example.com/ai.jpg" x="0" y="0" width="1600" height="900" />
    <polygon points="0,0 760,0 340,900 0,900" fill="#292A30" line_color="none" />
    <textbox x="70" y="343" width="440" height="72" size="36" bold="true" color="#0F172A">1. Giới thiệu</textbox>
    <textbox x="70" y="447" width="374" height="110" size="18" color="#475569">Nhu cầu và xu hướng sử dụng AI</textbox>
  </slide>
</presentation>'''


def test_final_xml_guard_repairs_transition_panel_colors() -> None:
    result, report = enforce_xml_text_contrast(
        _transition_xml(),
        preferred_colors=["#0D9488", "#0F172A", "#475569"],
    )

    textboxes = ET.fromstring(result).findall("./slide/textbox")
    assert textboxes[0].get("color") == "#0D9488"
    assert textboxes[1].get("color") == "#FFFFFF"
    assert contrast_ratio(textboxes[0].get("color"), "#292A30") >= 3.0
    assert contrast_ratio(textboxes[1].get("color"), "#292A30") >= 4.5
    assert not any(item["kind"] == "backplate" for item in report)


def test_final_xml_guard_repairs_explicit_rich_run_color() -> None:
    xml = '''<presentation><slide background="#111827">
      <shape type="rect" x="0" y="0" width="800" height="300" fill="#111827" />
      <textbox x="100" y="100" width="600" height="80" size="18" color="#FFFFFF">
        <run>Readable </run><run color="#334155">unreadable</run>
      </textbox>
    </slide></presentation>'''

    result, report = enforce_xml_text_contrast(xml)
    run = ET.fromstring(result).find('./slide/textbox/run[@color]')

    assert run.get("color") == "#FFFFFF"
    assert any(item.get("run_index") == 1 for item in report)


def test_final_xml_guard_adds_backplate_for_direct_image_text() -> None:
    xml = '''<presentation><slide background="#FFFFFF">
      <image src="https://example.com/photo.jpg" x="0" y="0" width="1600" height="900" />
      <textbox x="100" y="100" width="600" height="80" size="20" color="#475569">Caption</textbox>
    </slide></presentation>'''

    result, report = enforce_xml_text_contrast(xml)
    textbox = ET.fromstring(result).find("./slide/textbox")

    assert textbox.get("contrast_backplate") == "true"
    assert contrast_ratio(textbox.get("color"), textbox.get("fill")) >= 4.5
    assert any(item["kind"] == "backplate" for item in report)


def test_final_xml_guard_keeps_already_readable_text_unchanged() -> None:
    xml = '''<presentation><slide background="#FFFFFF">
      <textbox x="100" y="100" width="600" height="80" size="20" color="#111827">Readable</textbox>
    </slide></presentation>'''

    result, report = enforce_xml_text_contrast(xml)

    assert result == xml
    assert report == []


def test_powerpoint_converter_preserves_contrast_backplate(tmp_path) -> None:
    pytest.importorskip("pptx")
    from backend.infrastructure.converter.convert_universal import (
        XMLSlideConverter,
    )

    converter = XMLSlideConverter(
        xml_path=tmp_path / "input.xml",
        output_path=tmp_path / "output.pptx",
        open_after_convert=False,
    )
    slide = converter.prs.slides.add_slide(converter.prs.slide_layouts[6])
    textbox = ET.fromstring(
        '''<textbox x="100" y="100" width="600" height="80"
             font="Arial" size="20" color="#475569" fill="#FFFFFF"
             line_color="none" overflow="clip">Caption</textbox>'''
    )

    converter.render_textbox(slide, textbox)
    rendered = slide.shapes[-1]

    assert str(rendered.fill.fore_color.rgb) == "FFFFFF"


def test_xml_renderer_enforces_contrast_after_all_rewrites(tmp_path) -> None:
    from backend.workflows.slidegen_workflow.nodes.xml_renderer import render_xml

    state = {
        "current_slide_index": 1,
        "retry_count": 0,
        "current_xml_content": _transition_xml(),
        "deck_style_plan": {
            "accent_color": "#0D9488",
            "primary_color": "#0F172A",
            "secondary_color": "#475569",
        },
        "all_debug_info": [],
        "current_tool_call": {"name": "generate_transition_headline_slide_xml"},
    }
    config = {"configurable": {"temp_dir": str(tmp_path)}}

    asyncio.run(render_xml(state, config))

    saved = ET.parse(tmp_path / "xml" / "slide_2.xml").getroot()
    textboxes = saved.findall("./slide/textbox")
    assert textboxes[0].get("color") == "#0D9488"
    assert textboxes[1].get("color") == "#FFFFFF"
    assert len(state["current_contrast_report"]) == 2
