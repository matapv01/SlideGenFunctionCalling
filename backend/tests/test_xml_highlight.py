import xml.etree.ElementTree as ET

import pytest

from backend.workflows.slidegen_workflow.utils.rich_text import (
    DEFAULT_HIGHLIGHT_COLOR,
    MAX_HIGHLIGHTS_PER_SLIDE,
    apply_highlights_to_xml,
    extract_highlight_markers,
    materialize_math_fields_in_xml,
)


def test_extract_highlights_recursively_and_remove_layout_markers():
    arguments = {
        "title": (
            'AI giúp [[hl color="#2563EB"]]'
            "tăng hiệu suất 40%[[/hl]]"
        ),
        "items": [
            {
                "description": (
                    'Giảm [[hl color="#16A34A"]]'
                    "chi phí vận hành[[/hl]]"
                )
            }
        ],
    }

    clean_arguments, highlights = extract_highlight_markers(arguments)

    assert clean_arguments == {
        "title": "AI giúp tăng hiệu suất 40%",
        "items": [{"description": "Giảm chi phí vận hành"}],
    }
    assert [highlight.text for highlight in highlights] == [
        "tăng hiệu suất 40%",
        "chi phí vận hành",
    ]
    assert highlights[0].text_color == "#2563EB"
    assert highlights[1].source_path == "items[0].description"


def test_invalid_color_receives_safe_fallback():
    arguments = {
        "title": (
            '[[hl color="not-a-color"]]'
            "Readable phrase[[/hl]]"
        )
    }

    clean_arguments, highlights = extract_highlight_markers(arguments)

    assert clean_arguments["title"] == "Readable phrase"
    assert highlights[0].text_color == DEFAULT_HIGHLIGHT_COLOR


def test_highlight_must_be_a_unique_phrase_from_source_content():
    clean_arguments, highlights = extract_highlight_markers(
        {
            "title": (
                'AI tạo [[hl color="#2563EB"]]kết quả bịa thêm[[/hl]]'
            )
        },
        source_content="AI tạo kết quả chính xác",
    )

    assert clean_arguments["title"] == "AI tạo kết quả bịa thêm"
    assert highlights == []


def test_repeated_source_phrase_is_not_highlighted_ambiguously():
    _, highlights = extract_highlight_markers(
        {"title": '[[hl color="#2563EB"]]tăng trưởng[[/hl]]'},
        source_content="Tăng trưởng doanh thu và tăng trưởng lợi nhuận",
    )

    assert highlights == []


def test_literal_math_field_text_becomes_an_xml_node():
    xml_content = (
        '<presentation><slide><textbox color="#111111">'
        'Revenue: &lt;math-field&gt;\\frac{a}{b}&lt;/math-field&gt;'
        '</textbox></slide></presentation>'
    )

    result = materialize_math_fields_in_xml(xml_content)
    textbox = ET.fromstring(result).find("./slide/textbox")

    assert textbox.text == "Revenue: "
    field = textbox.find("./math-field")
    assert field is not None
    assert field.text == r"\frac{a}{b}"


def test_legacy_background_marker_keeps_only_its_foreground_color():
    clean_arguments, highlights = extract_highlight_markers(
        {
            "title": (
                '[[hl bg="#DBEAFE" fg="#1E3A8A"]]'
                "Legacy phrase[[/hl]]"
            )
        }
    )

    assert clean_arguments["title"] == "Legacy phrase"
    assert highlights[0].text_color == "#1E3A8A"


def test_extra_markers_are_cleaned_but_not_rendered_as_highlights():
    marked = " ".join(
        f'[[hl color="#2563EB"]]Phrase {index}[[/hl]]'
        for index in range(MAX_HIGHLIGHTS_PER_SLIDE + 1)
    )

    clean_arguments, highlights = extract_highlight_markers({"text": marked})

    assert "[[hl" not in clean_arguments["text"]
    assert len(highlights) == MAX_HIGHLIGHTS_PER_SLIDE


def test_apply_highlights_creates_flat_runs_and_preserves_visible_text():
    arguments = {
        "title": (
            'AI giúp [[hl color="#2563EB"]]'
            "tăng hiệu suất 40%[[/hl]] trong năm nay"
        )
    }
    clean_arguments, highlights = extract_highlight_markers(arguments)
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation width="1600" height="900">
  <slide background="#FFFFFF">
    <textbox x="100" y="100" width="900" height="100" color="#111111">{clean_arguments["title"]}</textbox>
  </slide>
</presentation>'''

    result = apply_highlights_to_xml(xml_content, highlights)
    root = ET.fromstring(result)
    textbox = root.find("./slide/textbox")
    runs = textbox.findall("./run")

    assert "".join(run.text or "" for run in runs) == clean_arguments["title"]
    assert [run.text for run in runs] == [
        "AI giúp ",
        "tăng hiệu suất 40%",
        " trong năm nay",
    ]
    assert runs[1].get("emphasis") == "highlight"
    assert runs[1].get("highlight") is None
    assert runs[1].get("color") == "#2563EB"
    assert runs[1].get("bold") is None


def test_highlight_matching_tolerates_case_and_inserted_line_breaks():
    clean_arguments, highlights = extract_highlight_markers(
        {
            "title": (
                '[[hl color="#FACC15"]]'
                "Business Growth[[/hl]]"
            )
        }
    )
    xml_content = (
        '<presentation><slide><textbox color="#FFFFFF">'
        "BUSINESS\nGROWTH"
        "</textbox></slide></presentation>"
    )

    result = apply_highlights_to_xml(xml_content, highlights)
    highlighted_run = ET.fromstring(result).find(
        './slide/textbox/run[@emphasis="highlight"]'
    )

    assert clean_arguments["title"] == "Business Growth"
    assert highlighted_run is not None
    assert highlighted_run.text == "BUSINESS\nGROWTH"


def test_converter_writes_colored_text_without_marker_background_when_available(
    tmp_path,
):
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
        '''<textbox x="100" y="100" width="800" height="100"
             font="Arial" size="32" color="#111111" overflow="clip">
             <run>AI giúp </run>
             <run color="#1E3A8A" bold="true">tăng 40%</run>
           </textbox>'''
    )

    converter.render_textbox(slide, textbox)
    slide_xml = slide._element.xml

    assert "<a:highlight>" not in slide_xml
    assert 'val="1E3A8A"' in slide_xml
    assert "tăng 40%" in slide_xml


def test_converter_converts_webp_images_before_adding_them_to_powerpoint(
    tmp_path,
):
    pytest.importorskip("pptx")
    from PIL import Image

    from backend.infrastructure.converter.convert_universal import (
        XMLSlideConverter,
    )

    source = tmp_path / "source.webp"
    Image.new("RGB", (32, 24), (24, 96, 160)).save(source, format="WEBP")

    converter = XMLSlideConverter(
        xml_path=tmp_path / "input.xml",
        output_path=tmp_path / "output.pptx",
        open_after_convert=False,
    )
    slide = converter.prs.slides.add_slide(converter.prs.slide_layouts[6])
    source_uri = str(source).replace("\\", "/")
    image = ET.fromstring(
        f'<image src="{source_uri}" '
        'x="0" y="0" width="320" height="240" />'
    )

    converter.render_image(slide, image)
    converter.prs.save(tmp_path / "output.pptx")

    assert len(slide.shapes) == 1
