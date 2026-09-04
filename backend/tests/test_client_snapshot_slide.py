import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_client_snapshot_slide_xml,
)
from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root


def test_long_detail_label_keeps_value_textbox_usable() -> None:
    long_label = (
        "Extremely long client detail label that must wrap instead of "
        "consuming the complete value column"
    )

    root = ET.fromstring(
        generate_client_snapshot_slide_xml(
            client_details=[f"{long_label}: visible value"]
        )
    )

    value_box = next(
        textbox
        for textbox in root.findall(".//textbox")
        if textbox.text == "visible value"
    )

    assert float(value_box.get("width", "0")) >= 280.0
    assert (
        float(value_box.get("x", "0"))
        + float(value_box.get("width", "0"))
        <= 795.0
    )


def test_market_snapshot_layout_keeps_four_details_inside_slide() -> None:
    root = ET.fromstring(
        generate_client_snapshot_slide_xml(
            title="2.3. PHÂN TÍCH THỊ TRƯỜNG",
            subtitle="Phân khúc, quy mô & xu hướng",
            client_details=[
                "SME: Bán lẻ, sản xuất, dịch vụ",
                "Quy mô: 2 tỷ USD (2025), CAGR 12%",
                "Lợi thế: Tùy biến, chuyên sâu",
                "Xu thế: Cloud, AI, Data, tích hợp",
            ],
        )
    )

    records = analyze_xml_root(root)

    assert not [record for record in records if record["overflow"]]
    assert max(record["y"] + record["height"] for record in records) <= 900
