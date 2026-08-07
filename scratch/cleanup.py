import os

# 1. Update xml_tool.py
xml_tool_path = r"backend\workflows\slidegen_workflow\tools\xml_tool.py"
with open(xml_tool_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# We know generate_intro_slide_xml starts at line 3167 (index 3166)
intro_index = -1
for i, line in enumerate(lines):
    if line.startswith("def generate_intro_slide_xml("):
        intro_index = i
        break

if intro_index != -1:
    new_lines = lines[:8] # Keep imports (first 8 lines)
    new_lines.append("\n\n")
    new_lines.append("# ==========================================================\n")
    new_lines.append("# 1. SLIDE INTRO (Giới thiệu, Cover)\n")
    new_lines.append("# ==========================================================\n")
    new_lines.extend(lines[intro_index:])
    
    with open(xml_tool_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


# 2. Update tool_des_xml.py
tool_des_path = r"backend\workflows\slidegen_workflow\tools\tool_des_xml.py"
with open(tool_des_path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove unused imports
content = re.sub(
    r"from backend\.workflows\.slidegen_workflow\.tools\.xml_tool import \([\s\S]*?generate_intro_slide_xml,\n\)",
    "from backend.workflows.slidegen_workflow.tools.xml_tool import (\n    generate_intro_slide_xml,\n)",
    content
)

# Remove unused Pydantic classes
# They are from GenerateContentCreationSlideInput down to just before INTRO_TOOLS = [
class_start = content.find("class GenerateContentCreationSlideInput(BaseModel):")
intro_tools_start = content.find("INTRO_TOOLS = [")

if class_start != -1 and intro_tools_start != -1:
    content = content[:class_start] + "\n# ==========================================================\n# CÁC CÔNG CỤ (TOOLS) ĐƯỢC ĐĂNG KÝ VỚI AI\n# ==========================================================\n" + content[intro_tools_start:]

# Remove references to CONTENT_TOOLS in ALL_TOOLS and TOOLS_DICT
content = content.replace(" + CONTENT_TOOLS", "")
content = content.replace("               'CONTENT_TOOLS': CONTENT_TOOLS,\n", "")

with open(tool_des_path, "w", encoding="utf-8") as f:
    f.write(content)
