import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

def generate_elegant_education_slide_xml(
    title: str = "Elegant Education\nPack for Students",
    subtitle: str = "Here is where your presentation begins",
    background_color: str = "#FFFFFF",
    title_color: str = "#3F474A",
    subtitle_color: str = "#515558",
) -> str:
    """
    Sinh XML cho slide Elegant Education Title với SVG patterns và co giãn text tự động.
    """
    if not title.strip():
        raise ValueError("title không được để trống")

    canvas_width = 1600
    canvas_height = 900
    content_max_width = 1300
    content_max_height = 500
    content_x = (canvas_width - content_max_width) / 2

    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_black = "C:/Windows/Fonts/ariblk.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Black.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # ---------------- NATIVE SHAPES INSTEAD OF SVG ----------------
    
    # Top Left Gray Blob (organic polygon approximation using bezier points)
    top_left_points = (
        "0,0 700,0 698,28 692,54 684,78 672,99 658,119 641,136 623,151 602,165 580,177 "
        "556,188 531,198 505,206 479,214 452,220 425,226 399,231 373,236 347,241 323,245 "
        "300,250 277,255 256,262 235,272 216,283 196,295 178,309 160,323 144,339 127,356 "
        "112,373 97,391 84,409 70,428 58,446 46,465 35,483 25,500 16,518 7,534 0,550"
    )
    ET.SubElement(slide, "polygon", points=top_left_points, fill="#9D9C8D", line_color="none")
    
    # Bottom Left Gray Blob
    ET.SubElement(slide, "shape", type="circle", x="200", y="650", width="100", height="130", fill="#A4A69B", line_color="none")
    
    # Right Brown Blob (positioned at middle right edge)
    ET.SubElement(slide, "shape", type="circle", x="1400", y="150", width="380", height="380", fill="#CDA590", line_color="none")
    
    # Bottom Brown Bar (thinner)
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="840", width="1600", height="60", fill="#C8A590", line_color="none")
    
    # Top Right Geometric Pattern (Honeycomb Polygons)
    R = 40
    dx = R * math.sqrt(3)  # 69.28
    dy = R * 1.5           # 60
    
    start_x = 1250
    start_y = -30
    centers = []
    for row in range(5):
        y = start_y + row * dy
        x_offset = start_x if row % 2 == 0 else start_x + dx / 2
        for col in range(6):
            x = x_offset + col * dx
            centers.append((x, y))
            
    for cx, cy in centers:
        pts = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            pts.append(f"{int(cx + R * math.cos(angle_rad))},{int(cy + R * math.sin(angle_rad))}")
        ET.SubElement(slide, "polygon", points=" ".join(pts), fill="none", line_color="#3F474A", line_width="1")

    # Title TextBox
    title_tb = ET.SubElement(
        slide, "textbox",
        x=str(content_x), y="300",
        width=str(content_max_width), height="200",
        font="Arial Black", font_path=font_path_black,
        size="100", min_font_size="48",
        color=title_color, align="center", vertical_align="bottom",
        single_line="false", max_lines="3", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.1", bold="true"
    )
    title_tb.text = title

    # Subtitle TextBox
    if subtitle.strip():
        sub_tb = ET.SubElement(
            slide, "textbox",
            x=str(content_x), y="520",
            width=str(content_max_width), height="100",
            font="Segoe UI", font_path=font_path_regular,
            size="36", min_font_size="24",
            color=subtitle_color, align="center", vertical_align="top",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2"
        )
        sub_tb.text = subtitle

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

# Let's write the whole file content back to xml_tool.py!
target_files = [
    r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\intro_slide_xml_bundle\xml_tool.py",
    r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\backend\workflows\slidegen_workflow\tools\xml_tool.py"
]

for tf in target_files:
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("# 5. ELEGANT EDUCATION TITLE SLIDE")
    if len(parts) > 1:
        import inspect
        new_content = parts[0] + "# 5. ELEGANT EDUCATION TITLE SLIDE\n# ==========================================================\n" + inspect.getsource(generate_elegant_education_slide_xml)
        with open(tf, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {tf}")

