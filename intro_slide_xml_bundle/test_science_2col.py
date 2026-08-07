import sys
from backend.workflows.slidegen_workflow.tools.xml_tool import generate_science_2col_slide_xml

def main():
    xml_str = generate_science_2col_slide_xml(
        main_title="From molecules to life",
        col1_title="Fact 1",
        col1_desc="Mercury is the closest planet to the Sun and the smallest one in the entire Solar System. Contrary to popular belief, this planet's name has nothing to do with the liquid metal. Mercury was, instead, named after the famous Roman messenger god Mercurius",
        col2_title="Fact 2",
        col2_desc="Mercury takes a little more than 58 days to complete its rotation, so try to imagine how long days must be there! Since the temperatures are so extreme, albeit not as extreme as on Venus, Mercury has been deemed to be non-habitable for humans"
    )
    
    with open("science_2col_test.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print("Generated science_2col_test.xml")

if __name__ == "__main__":
    main()
