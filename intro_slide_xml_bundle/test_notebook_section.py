import sys
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_notebook_section_slide_xml

def main():
    xml_str = generate_notebook_section_slide_xml(
        number="01",
        title="Introduction",
        subtitle="You can enter a subtitle here if you need it",
        background_color="#FFFFFF"
    )
    
    with open("notebook_section_test.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print("Generated notebook_section_test.xml")

if __name__ == "__main__":
    main()
