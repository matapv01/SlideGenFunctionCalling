import os
from xml_tool import generate_content_2col_slide_xml

xml_str = generate_content_2col_slide_xml()
with open("content_2col_test.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)
print("Generated content_2col_test.xml")
