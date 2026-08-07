import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

def cubic_bezier(t, p0, p1, p2, p3):
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return x, y

def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    t0 = 0.0
    t1 = 1.0
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0: return None
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if t > t1: return None
                if t > t0: t0 = t
            else:
                if t < t0: return None
                if t < t1: t1 = t
    if t0 <= t1:
        return (x1 + t0*dx, y1 + t0*dy, x1 + t1*dx, y1 + t1*dy)
    return None

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
    
    # Top Left Gray Blob
    pts = [(0, 0), (600, 0)]
    for i in range(1, 21):
        t = i / 20.0
        x, y = cubic_bezier(t, (600, 0), (500, 250), (200, 200), (0, 500))
        pts.append((int(x), int(y)))
    top_left_points = " ".join([f"{x},{y}" for x, y in pts])
    ET.SubElement(slide, "polygon", points=top_left_points, fill="#9D9C8D", line_color="none")
    
    # Bottom Left Gray Blob
    ET.SubElement(slide, "shape", type="circle", x="200", y="650", width="100", height="130", fill="#A4A69B", line_color="none")
    
    # Right Brown Blob (clipped to right edge)
    pts_brown = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        x = 1525 + 175 * math.cos(rad)
        y = 275 + 175 * math.sin(rad)
        if x > 1600:
            x = 1600
        pts_brown.append((int(x), int(y)))
    brown_points = " ".join([f"{x},{y}" for x, y in pts_brown])
    ET.SubElement(slide, "polygon", points=brown_points, fill="#CDA590", line_color="none")
    
    # Bottom Brown Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="840", width="1600", height="60", fill="#C8A590", line_color="none")
    
    # Top Right Geometric Pattern (Honeycomb grid using native <line> elements to avoid opaque fill)
    lines_to_draw = []
    
    R = 45
    dx = R * math.sqrt(3)  # ~78
    dy = R * 1.5           # 67.5
    
    start_x = 1250
    start_y = 0
    centers = []
    for row in range(5):
        y = start_y + row * dy
        x_offset = start_x if row % 2 == 0 else start_x + dx / 2
        for col in range(6):
            x = x_offset + col * dx
            centers.append((x, y))
            
    for cx, cy in centers:
        hex_pts = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            hex_pts.append((cx + R * math.cos(angle_rad), cy + R * math.sin(angle_rad)))
        
        for i in range(6):
            p1 = hex_pts[i]
            p2 = hex_pts[(i+1)%6]
            lines_to_draw.append((p1[0], p1[1], p2[0], p2[1]))

    for x1, y1, x2, y2 in lines_to_draw:
        # Clip to the slide canvas so they don't overflow
        clipped = clip_line(x1, y1, x2, y2, 0, 0, 1600, 900)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ET.SubElement(slide, "line", x1=str(int(cx1)), y1=str(int(cy1)), x2=str(int(cx2)), y2=str(int(cy2)), color="#3F474A", width="1")

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
        new_content = parts[0] + "# 5. ELEGANT EDUCATION TITLE SLIDE\n# ==========================================================\n" + inspect.getsource(cubic_bezier) + "\n" + inspect.getsource(clip_line) + "\n" + inspect.getsource(generate_elegant_education_slide_xml)
        with open(tf, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {tf}")
