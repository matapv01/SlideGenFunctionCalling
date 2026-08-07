import sys
import math

def add_online_notebook_to_xml_tool():
    target_files = [
        r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\intro_slide_xml_bundle\xml_tool.py",
        r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\backend\workflows\slidegen_workflow\tools\xml_tool.py"
    ]
    
    new_code = """
# ==========================================================
# 6. ONLINE NOTEBOOK TITLE SLIDE
# ==========================================================
def generate_online_notebook_slide_xml(
    title: str = "ONLINE NOTEBOOK",
    subtitle: str = "Here is where your presentation begins",
    background_color: str = "#FFFFFF",
    title_color: str = "#1D4984",
    subtitle_color: str = "#2C3E50",
) -> str:
    \"\"\"
    Sinh XML cho slide Online Notebook Title với các rule co giãn text nghiêm ngặt.
    \"\"\"
    import sys
    import math
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    if not title.strip():
        raise ValueError("title không được để trống")
        
    words = title.strip().split(" ", 1)
    title1 = words[0]
    title2 = words[1] if len(words) > 1 else ""

    canvas_width = 1600
    canvas_height = 900

    # Fonts
    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_comic = "C:/Windows/Fonts/comic.ttf" if sys.platform == "win32" else "/Library/Fonts/Comic Sans MS.ttf"
    # Dùng Arial Black nếu Comic không có
    font_path_bold = "C:/Windows/Fonts/ariblk.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Black.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # Background Left Polygon (Light Blue)
    bg_pts = [(0, 0), (450, 0), (1600, 900), (0, 900)]
    bg_points_str = " ".join([f"{x},{y}" for x, y in bg_pts])
    ET.SubElement(slide, "polygon", points=bg_points_str, fill="#9BBDF2", line_color="none")
    
    # Left Dark Blue Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="0", width="100", height="900", fill="#6895DD", line_color="none")
    
    # Eraser (Top Left)
    ET.SubElement(slide, "shape", type="rectangle", x="200", y="-50", width="100", height="180", rotation="15", fill="#FFB6B6", line_color="#000000", line_width="3")
    
    # Notebook Paper (Top Right)
    ET.SubElement(slide, "shape", type="rectangle", x="1350", y="-50", width="250", height="350", rotation="-15", fill="#FFFFFF", line_color="#000000", line_width="2")
    
    def rot(x, y, cx, cy, deg):
        rad = math.radians(deg)
        nx = cx + (x - cx)*math.cos(rad) - (y - cy)*math.sin(rad)
        ny = cy + (x - cx)*math.sin(rad) + (y - cy)*math.cos(rad)
        return int(nx), int(ny)
        
    cx, cy = 1350 + 125, -50 + 175
    for i in range(1, 7):
        y_loc = -50 + i * 50
        x1_loc, x2_loc = 1360, 1590
        rx1, ry1 = rot(x1_loc, y_loc, cx, cy, -15)
        rx2, ry2 = rot(x2_loc, y_loc, cx, cy, -15)
        ET.SubElement(slide, "line", x1=str(rx1), y1=str(ry1), x2=str(rx2), y2=str(ry2), color="#000000", width="1")

    # Pen (Bottom Right)
    pen_cx, pen_cy = 1350, 800
    deg = -45
    # Build parts of pen around 0,0 and rotate
    # Body
    body_pts = [(-20, -200), (20, -200), (20, 150), (-20, 150)]
    # Tip
    tip_pts = [(-20, -200), (20, -200), (0, -260)]
    # Cap details
    cap_pts = [(-22, 100), (22, 100), (22, 160), (-22, 160)]
    clip_pts = [(-25, 110), (-25, 60), (-20, 60), (-20, 110)]
    
    for shape_pts, fill in [(tip_pts, "#000000"), (body_pts, "#1A5E8E"), (cap_pts, "#144A70"), (clip_pts, "#B0D4EE")]:
        rot_pts = [rot(px, py, 0, 0, deg) for px, py in shape_pts]
        final_pts = [(rx + pen_cx, ry + pen_cy) for rx, ry in rot_pts]
        pts_str = " ".join([f"{int(x)},{int(y)}" for x, y in final_pts])
        ET.SubElement(slide, "polygon", points=pts_str, fill=fill, line_color="#000000", line_width="2")

    # Center Ticket Badge
    d = 40
    X, Y, W, H = 300, 175, 1000, 550
    ticket_pts = [
        (X+d, Y), (X+W-d, Y),
        (X+W-d, Y+d), (X+W, Y+d),
        (X+W, Y+H-d),
        (X+W-d, Y+H-d), (X+W-d, Y+H),
        (X+d, Y+H),
        (X+d, Y+H-d), (X, Y+H-d),
        (X, Y+d),
        (X+d, Y+d)
    ]
    ticket_points_str = " ".join([f"{x},{y}" for x, y in ticket_pts])
    ET.SubElement(slide, "polygon", points=ticket_points_str, fill="#FFFFFF", line_color="#000000", line_width="2")

    # Divider Line
    if title2:
        ET.SubElement(slide, "line", x1="450", y1="450", x2="1150", y2="450", color="#1D4984", width="4")

    # Title Part 1
    title1_tb = ET.SubElement(
        slide, "textbox",
        x="350", y="230",
        width="900", height="210",
        font="Arial Black", font_path=font_path_bold,
        size="110", min_font_size="40",
        color=title_color, align="center", vertical_align="bottom",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    title1_tb.text = title1

    # Title Part 2
    if title2:
        title2_tb = ET.SubElement(
            slide, "textbox",
            x="350", y="460",
            width="900", height="210",
            font="Arial Black", font_path=font_path_bold,
            size="110", min_font_size="40",
            color=title_color, align="center", vertical_align="top",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="true"
        )
        title2_tb.text = title2

    # Subtitle TextBox
    if subtitle.strip():
        sub_tb = ET.SubElement(
            slide, "textbox",
            x="400", y="600" if not title2 else "660",
            width="800", height="100",
            font="Segoe UI", font_path=font_path_regular,
            size="36", min_font_size="20",
            color=subtitle_color, align="center", vertical_align="middle" if not title2 else "top",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2"
        )
        sub_tb.text = subtitle

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
"""

    for file_path in target_files:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(new_code)
        print(f"Appended to {file_path}")

if __name__ == "__main__":
    add_online_notebook_to_xml_tool()
