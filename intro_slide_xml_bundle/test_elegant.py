import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_elegant_education_slide_xml

xml_content = generate_elegant_education_slide_xml()
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "elegant_education_test.xml"))
with open(output_path, "w", encoding="utf-8") as f:
    f.write(xml_content)
print("Generated elegant_education_test.xml")
