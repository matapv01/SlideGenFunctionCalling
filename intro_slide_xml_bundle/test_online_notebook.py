import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_online_notebook_slide_xml

# Test with a very long title to test the overflow="shrink" rule
xml_content = generate_online_notebook_slide_xml(
    title="INTERNATIONAL MACROECONOMICS",
    subtitle="A comprehensive guide to global markets and policies"
)

output_file = "online_notebook_test.xml"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(xml_content)

print(f"Generated {output_file}")
