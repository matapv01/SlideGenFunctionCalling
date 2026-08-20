import random
import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.utils.xml_transitions import (
    RANDOM_TRANSITION_TYPES,
    apply_random_slide_transitions,
)


def test_random_transition_is_added_to_each_slide():
    xml = """<presentation><slide /><slide /></presentation>"""

    result, applied = apply_random_slide_transitions(xml, rng=random.Random(4))
    root = ET.fromstring(result)

    assert len(applied) == 2
    assert len(root.findall("./slide")) == 2
    assert all(item["type"] in RANDOM_TRANSITION_TYPES for item in applied)
    assert all(slide.get("transition") for slide in root.findall("./slide"))
    assert all(slide.get("transition_duration") == "700" for slide in root.findall("./slide"))
    assert all(slide.get("transition_advance") == "click" for slide in root.findall("./slide"))


def test_invalid_xml_is_left_unchanged():
    xml = "<presentation>"

    result, applied = apply_random_slide_transitions(xml)

    assert result == xml
    assert applied == []
