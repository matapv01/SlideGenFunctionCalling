import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_classic_toc_slide_xml

items = [
    {
        "number": "01",
        "title": "Introduction",
        "description": "An overview of the presentation topic and objectives."
    },
    {
        "number": "02",
        "title": "Reconstruction Era",
        "description": "Brief overview of the era."
    },
    {
        "number": "03",
        "title": "The Gilded Age",
        "description": "Exploring economic growth and challenges."
    },
    {
        "number": "04",
        "title": "Comparison",
        "description": "Comparing the two eras."
    },
    {
        "number": "05",
        "title": "Conclusion",
        "description": "Final thoughts."
    },
    {
        "number": "06",
        "title": "Activities",
        "description": "Interactive sessions."
    }
]

xml_content = generate_classic_toc_slide_xml(
    title="Table of contents",
    items=items
)

output_file = "classic_toc_test.xml"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(xml_content)

print(f"Generated {output_file}")
