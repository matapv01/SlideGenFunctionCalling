from backend.workflows.slidegen_workflow.utils.layout_similarity import (
    build_layout_signature,
    find_layout_duplicate,
    layout_similarity,
)


def _xml(title: str, color: str, second_x: int = 100) -> str:
    return f"""<presentation><slide background="{color}">
    <textbox x="100" y="100" width="900" height="100" color="{color}">{title}</textbox>
    <textbox x="{second_x}" y="300" width="900" height="300">Different body</textbox>
    </slide></presentation>"""


def test_signature_ignores_text_and_color():
    first = build_layout_signature(_xml("First title", "#FFFFFF"))
    second = build_layout_signature(_xml("Completely different", "#000000"))

    assert layout_similarity(first, second) == 1.0
    duplicate = find_layout_duplicate(
        second,
        2,
        [{"index": 0, "signature": first, "exempt": False}],
    )
    assert duplicate is not None


def test_signature_detects_geometry_change():
    first = build_layout_signature(_xml("A", "#FFFFFF"))
    moved = build_layout_signature(_xml("B", "#FFFFFF", second_x=700))

    assert layout_similarity(first, moved) < 0.92


def test_transition_signature_can_be_exempted():
    signature = build_layout_signature(_xml("A", "#FFFFFF"))
    assert find_layout_duplicate(
        signature,
        1,
        [{"index": 0, "signature": signature, "exempt": True}],
    ) is None
