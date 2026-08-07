import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

def add_classic_toc_to_xml_tool():
    target_files = [
        r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\intro_slide_xml_bundle\xml_tool.py",
        r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\backend\workflows\slidegen_workflow\tools\xml_tool.py"
    ]
    
    new_code = """
# ==========================================================
# 7. CLASSIC TABLE OF CONTENTS SLIDE
# ==========================================================
def generate_classic_toc_slide_xml(
    title: str = "Table of contents",
    items: list = None,
    background_color: str = "#EBE4D5",
    theme_color: str = "#4A3F35",
) -> str:
    \"\"\"
    Sinh XML cho slide Mục lục phong cách cổ điển (Classic/Vintage TOC).
    Có khung viền hoàng gia và hỗ trợ lưới 2x3 (tối đa 6 mục).
    \"\"\"
    import sys
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    if items is None:
        items = []

    canvas_width = 1600
    canvas_height = 900

    # Fonts
    # Ưu tiên các font Serif cổ điển
    if sys.platform == "win32":
        font_path_serif = "C:/Windows/Fonts/georgia.ttf"
        font_path_serif_bold = "C:/Windows/Fonts/georgiab.ttf"
    else:
        font_path_serif = "/Library/Fonts/Georgia.ttf"
        font_path_serif_bold = "/Library/Fonts/Georgia Bold.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # --- DECORATIVE BORDERS ---
    # Outer Border
    ox, oy, ow, oh = 40, 40, 1520, 820
    ET.SubElement(slide, "shape", type="rectangle", x=str(ox), y=str(oy), width=str(ow), height=str(oh), fill="none", line_color=theme_color, line_width="2")
    
    # Inner Border
    ix, iy, iw, ih = 60, 60, 1480, 780
    ET.SubElement(slide, "shape", type="rectangle", x=str(ix), y=str(iy), width=str(iw), height=str(ih), fill="none", line_color=theme_color, line_width="1")
    
    # 4 Corner Squares
    # Each square is placed such that its center is exactly where the outer and inner border would meet or just decorative.
    # The image shows squares placed at the 4 corners between inner and outer borders.
    sq_size = 30
    corners = [
        (ox - 5, oy - 5), # Top-left
        (ox + ow - sq_size + 5, oy - 5), # Top-right
        (ox - 5, oy + oh - sq_size + 5), # Bottom-left
        (ox + ow - sq_size + 5, oy + oh - sq_size + 5) # Bottom-right
    ]
    for cx, cy in corners:
        ET.SubElement(slide, "shape", type="rectangle", x=str(cx), y=str(cy), width=str(sq_size), height=str(sq_size), fill="none", line_color=theme_color, line_width="2")
        
    # --- MAIN TITLE ---
    title_tb = ET.SubElement(
        slide, "textbox",
        x="400", y="120",
        width="800", height="100",
        font="Georgia", font_path=font_path_serif,
        size="72", min_font_size="36",
        color=theme_color, align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="false"
    )
    title_tb.text = title

    # --- GRID ITEMS (Max 6) ---
    max_items = 6
    display_items = items[:max_items]
    
    # Tọa độ tâm các cột và hàng
    centers_x = [300, 800, 1300]
    centers_y = [380, 680]
    
    for idx, item in enumerate(display_items):
        row = idx // 3
        col = idx % 3
        
        cx = centers_x[col]
        cy = centers_y[row]
        
        box_width = 380
        start_x = cx - box_width // 2
        
        number = item.get("number", f"{idx+1:02d}")
        item_title = item.get("title", f"Section {idx+1}")
        description = item.get("description", "You can describe the topic of the section here")
        
        # Top line for number
        ET.SubElement(slide, "line", x1=str(cx - 50), y1=str(cy - 80), x2=str(cx + 50), y2=str(cy - 80), color=theme_color, width="2")
        
        # Number Textbox
        num_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy - 80),
            width=str(box_width), height="60",
            font="Georgia", font_path=font_path_serif_bold,
            size="50", min_font_size="20",
            color=theme_color, align="center", vertical_align="middle",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="true"
        )
        num_tb.text = number
        
        # Bottom line for number
        ET.SubElement(slide, "line", x1=str(cx - 50), y1=str(cy - 10), x2=str(cx + 50), y2=str(cy - 10), color=theme_color, width="2")
        
        # Item Title Textbox
        it_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy),
            width=str(box_width), height="60",
            font="Georgia", font_path=font_path_serif_bold,
            size="40", min_font_size="20",
            color=theme_color, align="center", vertical_align="top",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="true"
        )
        it_tb.text = item_title
        
        # Description Textbox
        desc_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy + 60),
            width=str(box_width), height="90",
            font="Georgia", font_path=font_path_serif,
            size="24", min_font_size="16",
            color=theme_color, align="center", vertical_align="top",
            single_line="false", max_lines="3", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2", bold="false"
        )
        desc_tb.text = description

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
"""

    for file_path in target_files:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(new_code)
        print(f"Appended to {file_path}")

if __name__ == "__main__":
    add_classic_toc_to_xml_tool()
