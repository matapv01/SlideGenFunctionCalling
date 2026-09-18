from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from workflows.slidegen_workflow.tools.xml_tool import (  # noqa: E402
    generate_best_selling_product_chart_slide_xml,
)


OUTPUT = Path("ai_adoption_chart_slide.xml")


def main() -> None:
    xml = generate_best_selling_product_chart_slide_xml(
        title="XU HƯỚNG ỨNG DỤNG AI",
        chart_data=[
            {"category": "2020", "series": {"Machine Learning": 18, "Generative AI": 8, "AI Agent": 3}},
            {"category": "2021", "series": {"Machine Learning": 29, "Generative AI": 13, "AI Agent": 5}},
            {"category": "2022", "series": {"Machine Learning": 41, "Generative AI": 24, "AI Agent": 9}},
            {"category": "2023", "series": {"Machine Learning": 55, "Generative AI": 39, "AI Agent": 18}},
            {"category": "2024", "series": {"Machine Learning": 69, "Generative AI": 58, "AI Agent": 31}},
            {"category": "2025", "series": {"Machine Learning": 82, "Generative AI": 76, "AI Agent": 49}},
        ],
        footer_text=(
            "Dữ liệu minh họa cho thấy mức độ ứng dụng AI tăng đều, "
            "trong đó Generative AI và AI Agent tăng nhanh ở giai đoạn gần đây."
        ),
        background_color="#FFFFFF",
        panel_color="#F8F8F8",
        title_color="#2B8FB4",
        coral_color="#FF7375",
        peach_color="#F3C580",
        green_color="#A6CE91",
        grid_color="#C9C9C9",
        axis_text_color="#161616",
        footer_color="#626262",
    )
    OUTPUT.write_text(xml, encoding="utf-8")
    print(OUTPUT.resolve())


if __name__ == "__main__":
    main()
