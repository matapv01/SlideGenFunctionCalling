import sys
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_thank_you_watching_slide_xml

def main():
    xml_str = generate_thank_you_watching_slide_xml()
    
    with open("thank_you_watching_test.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print("Generated thank_you_watching_test.xml")

if __name__ == "__main__":
    main()
