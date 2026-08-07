import os
from xml_tool import generate_about_me_slide_xml

xml_str = generate_about_me_slide_xml()
with open("about_me_test.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)
print("Generated about_me_test.xml")
