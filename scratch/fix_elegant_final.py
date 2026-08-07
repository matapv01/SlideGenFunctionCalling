import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

def cubic_bezier(t, p0, p1, p2, p3):
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return x, y

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

    import sys
    import math
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
    
    # Top Left Gray Blob (organic shape inside the canvas using fewer points to not protrude)
    pts = [(0, 0), (600, 0)]
    for i in range(1, 21):
        t = i / 20.0
        x, y = cubic_bezier(t, (600, 0), (500, 250), (200, 200), (0, 500))
        pts.append((int(x), int(y)))
    top_left_points = " ".join([f"{x},{y}" for x, y in pts])
    ET.SubElement(slide, "polygon", points=top_left_points, fill="#9D9C8D", line_color="none")
    
    # Bottom Left Gray Blob
    ET.SubElement(slide, "shape", type="circle", x="200", y="650", width="100", height="130", fill="#A4A69B", line_color="none")
    
    # Right Brown Blob (inside the canvas, touching the right edge)
    ET.SubElement(slide, "shape", type="circle", x="1350", y="100", width="350", height="350", fill="#CDA590", line_color="none")
    
    # Bottom Brown Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="840", width="1600", height="60", fill="#C8A590", line_color="none")
    
    # Top Right Geometric Pattern (Isometric lines instead of polygons to fix overlap bug in convert_universal.py)
    # Isometric grid
    # Verticals
    xs = [1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550]
    for x in xs:
        ET.SubElement(slide, "line", x1=str(x), y1="0", x2=str(x), y2="250", color="#3F474A", width="1")
    
    # Diagonals (30 degrees and 150 degrees)
    # y = mx + c
    m30 = math.tan(math.radians(30))
    m150 = math.tan(math.radians(150))
    
    y_intercepts_30 = [-750, -700, -650, -600, -550, -500, -450]
    for c in y_intercepts_30:
        y1 = m30 * 1200 + c
        y2 = m30 * 1600 + c
        ET.SubElement(slide, "line", x1="1200", y1=str(int(y1)), x2="1600", y2=str(int(y2)), color="#3F474A", width="1")

    y_intercepts_150 = [800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
    for c in y_intercepts_150:
        y1 = m150 * 1200 + c
        y2 = m150 * 1600 + c
        ET.SubElement(slide, "line", x1="1200", y1=str(int(y1)), x2="1600", y2=str(int(y2)), color="#3F474A", width="1")

    # Title TextBox
    title_tb = ET.SubElement(
        slide, "textbox",
        x=str(content_x), y="320",
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
            x=str(content_x), y="550",
            width=str(content_max_width), height="100",
            font="Segoe UI", font_path=font_path_regular,
            size="40", min_font_size="24",
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
        # Build the final script.
        # We also need to include cubic_bezier function!
        import inspect
        new_content = parts[0] + "# 5. ELEGANT EDUCATION TITLE SLIDE\n# ==========================================================\n" + inspect.getsource(cubic_bezier) + "\n" + inspect.getsource(generate_elegant_education_slide_xml)
        with open(tf, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {tf}")

