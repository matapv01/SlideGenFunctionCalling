import os
import sys
import traceback

# Thêm thư mục gốc vào path để import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_intro_slide_xml,
    generate_warm_intro_slide_xml,
    generate_creative_team_slide_xml,
    generate_grid_team_slide_xml,
)

def save_xml(filename, content):
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {filename}")

def test_all_slides():
    print("Testing all slide generators...")
    
    # 1. Intro Slide
    try:
        xml_content = generate_intro_slide_xml(
            title="Intro Template",
            subtitle="Choose a topic and audience to generate a tailored introductory presentation"
        )
        save_xml("intro_slide_test.xml", xml_content)
    except Exception as e:
        print(f"Error generating intro slide: {e}")

    # 2. Warm Intro Slide
    try:
        xml_content = generate_warm_intro_slide_xml(
            title="Intro Template",
            subtitle="Choose a topic and audience to generate a tailored introductory presentation"
        )
        save_xml("warm_intro_test.xml", xml_content)
    except Exception as e:
        print(f"Error generating warm intro slide: {e}")
        traceback.print_exc()

    # 3. Creative Team Slide
    try:
        xml_content = generate_creative_team_slide_xml()
        save_xml("creative_team_test.xml", xml_content)
    except Exception as e:
        print(f"Error generating creative team slide: {e}")
        traceback.print_exc()

    # 4. Grid Team Slide
    try:
        xml_content = generate_grid_team_slide_xml()
        save_xml("grid_team_test.xml", xml_content)
    except Exception as e:
        print(f"Error generating grid team slide: {e}")
        traceback.print_exc()

    # 5. Content Creation Slide (Đã comment để test từng slide một)
    # try:
    #     xml_content = generate_content_creation_slide_xml(
    #         main_title="CONTENT CREATION",
    #         original_title="Original Content",
    #         original_description="Develop unique visuals and copy.",
    #         curated_title="Curated Content",
    #         curated_description="Share valuable curated content."
    #     )
    #     save_xml("content_creation_test.xml", xml_content)
    # except Exception as e:
    #     print(f"Error generating content creation slide: {e}")
    #     traceback.print_exc()

    # 3. AI Content Slide
    # try:
    #     xml_content = generate_ai_content_slide_xml(
    #         title="THE SLIDE TITLE GOES HERE",
    #         intro_text="Do you know what helps you make your point clear?",
    #         bullet_items=["They are simple", "You can organize your ideas clearly"],
    #         footer_text="You can replace the image."
    #     )
    #     save_xml("ai_content_test.xml", xml_content)
    # except Exception as e:
    #     print(f"Error generating AI content slide: {e}")
    #     traceback.print_exc()

    # 4. Two Ideas Slide
    # try:
    #     xml_content = generate_two_ideas_slide_xml(
    #         title="TWO IDEAS",
    #         idea_titles=["Venus", "Mercury"],
    #         idea_descriptions=["Venus is the second planet.", "Mercury is the closest planet."]
    #     )
    #     save_xml("two_ideas_test.xml", xml_content)
    # except Exception as e:
    #     print(f"Error generating two ideas slide: {e}")

    # 5. Three Ideas Slide
    # try:
    #     xml_content = generate_three_ideas_slide_xml(
    #         title="THREE IDEAS",
    #         idea_titles=["Mercury", "Mars", "Venus"],
    #         idea_descriptions=["Closest planet.", "Red Planet.", "Toxic atmosphere."]
    #     )
    #     save_xml("three_ideas_test.xml", xml_content)
    # except Exception as e:
    #     print(f"Error generating three ideas slide: {e}")

    # 6. Our History Slide
    # try:
    #     xml_content = generate_our_history_slide_xml(
    #         title="OUR HISTORY",
    #         event_titles=["SATURN", "MARS", "NEPTUNE"],
    #         event_descriptions=["Saturn is composed of hydrogen.", "Mars is a cold place.", "Farthest planet."],
    #         event_years=["1998", "2005", "2024"]
    #     )
    #     save_xml("our_history_test.xml", xml_content)
    # except Exception as e:
    #     print(f"Error generating our history slide: {e}")

if __name__ == "__main__":
    test_all_slides()
