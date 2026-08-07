import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

def rot(x, y, cx, cy, deg):
    rad = math.radians(deg)
    nx = cx + (x - cx)*math.cos(rad) - (y - cy)*math.sin(rad)
    ny = cy + (x - cx)*math.sin(rad) + (y - cy)*math.cos(rad)
    return int(nx), int(ny)

def generate_online_notebook_slide_xml(
    title: str = "ONLINE NOTEBOOK",
    subtitle: str = "Here is where your presentation begins",
    background_color: str = "#FFFFFF",
    title_color: str = "#1E4E8C",
    subtitle_color: str = "#2C3E50",
) -> str:
    """
    Sinh XML cho slide Online Notebook Title với các rule co giãn text nghiêm ngặt.
    Phiên bản Premium: faked shadows, inward circular corners, realistic props, Arial Rounded font.
    """
    if not title.strip():
        raise ValueError("title không được để trống")
        
    words = title.strip().split(" ", 1)
    title1 = words[0]
    title2 = words[1] if len(words) > 1 else ""

    canvas_width = 1600
    canvas_height = 900

    # Fonts
    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    # Dùng Arial Rounded MT Bold cho cảm giác marker/notebook
    font_path_bold = "C:/Windows/Fonts/ARLRDBD.TTF" if sys.platform == "win32" else "/Library/Fonts/Arial Bold.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # 1. Background
    # Left Polygon (Light Blue)
    bg_pts = [(0, 0), (600, 0), (1600, 900), (0, 900)]
    bg_points_str = " ".join([f"{x},{y}" for x, y in bg_pts])
    ET.SubElement(slide, "polygon", points=bg_points_str, fill="#B8D3F8", line_color="none")
    
    # Left Dark Blue Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="0", width="80", height="900", fill="#77A3EA", line_color="none")

    # 2. Ticket Badge (with faked drop shadow)
    R = 40
    X, Y, W, H = 250, 150, 1100, 600
    
    # Build ticket points with circular arcs for inward corners
    ticket_pts = []
    # Top-left cutout: Center (X, Y), arc from 90 to 0 degrees
    for deg in range(90, -1, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X + R*math.cos(rad)), int(Y + R*math.sin(rad))))
    
    # Top-right cutout: Center (X+W, Y), arc from 180 to 90 degrees
    for deg in range(180, 89, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X+W + R*math.cos(rad)), int(Y + R*math.sin(rad))))
        
    # Bottom-right cutout: Center (X+W, Y+H), arc from 270 to 180 degrees
    for deg in range(270, 179, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X+W + R*math.cos(rad)), int(Y+H + R*math.sin(rad))))
        
    # Bottom-left cutout: Center (X, Y+H), arc from 360 to 270 degrees
    for deg in range(360, 269, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X + R*math.cos(rad)), int(Y+H + R*math.sin(rad))))

    # Shadow for Ticket
    shadow_pts = [(x+15, y+15) for x, y in ticket_pts]
    shadow_str = " ".join([f"{x},{y}" for x, y in shadow_pts])
    ET.SubElement(slide, "polygon", points=shadow_str, fill="#9ABAE5", line_color="none") # Drop shadow color blends with bg

    # Ticket Base
    ticket_points_str = " ".join([f"{x},{y}" for x, y in ticket_pts])
    ET.SubElement(slide, "polygon", points=ticket_points_str, fill="#FFFFFF", line_color="#000000", line_width="2")

    # 3. Eraser (Top Left)
    eraser_cx, eraser_cy = 250, 80
    eraser_deg = 20
    ew, eh = 80, 120
    
    eraser_base = [(-ew/2, -eh/2), (ew/2, -eh/2), (ew/2, eh/2), (-ew/2, eh/2)]
    eraser_top = [(-ew/2, -eh/2), (ew/2, -eh/2), (ew/2, 0), (-ew/2, 0)]
    eraser_bot = [(-ew/2, 0), (ew/2, 0), (ew/2, eh/2), (-ew/2, eh/2)]
    
    # Shadow
    e_shadow = [(x+10, y+10) for x, y in eraser_base]
    e_shadow_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in e_shadow]
    e_shadow_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_shadow_rot])
    ET.SubElement(slide, "polygon", points=e_shadow_str, fill="#9ABAE5", line_color="none")
    
    # Pink top
    e_top_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in eraser_top]
    e_top_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_top_rot])
    ET.SubElement(slide, "polygon", points=e_top_str, fill="#FFAFA3", line_color="#000000", line_width="2")
    
    # Beige bottom sleeve
    e_bot_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in eraser_bot]
    e_bot_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_bot_rot])
    ET.SubElement(slide, "polygon", points=e_bot_str, fill="#FFE5D9", line_color="#000000", line_width="2")

    # 4. Notebook Paper (Top Right)
    paper_cx, paper_cy = 1350, 180
    paper_deg = 12
    pw, ph = 240, 320
    paper_base = [(-pw/2, -ph/2), (pw/2, -ph/2), (pw/2, ph/2), (-pw/2, ph/2)]
    
    # Shadow
    p_shadow = [(x+12, y+12) for x, y in paper_base]
    p_shadow_rot = [rot(px, py, 0, 0, paper_deg) for px, py in p_shadow]
    p_shadow_str = " ".join([f"{int(x+paper_cx)},{int(y+paper_cy)}" for x, y in p_shadow_rot])
    # For white background, shadow needs to be light gray
    ET.SubElement(slide, "polygon", points=p_shadow_str, fill="#E0E0E0", line_color="none")
    
    # Paper white base
    p_base_rot = [rot(px, py, 0, 0, paper_deg) for px, py in paper_base]
    p_base_str = " ".join([f"{int(x+paper_cx)},{int(y+paper_cy)}" for x, y in p_base_rot])
    ET.SubElement(slide, "polygon", points=p_base_str, fill="#FFFFFF", line_color="#000000", line_width="2")
    
    # Lines inside paper
    for i in range(1, 7):
        line_y = -ph/2 + i * 45
        x1, x2 = -pw/2 + 20, pw/2 - 20
        rx1, ry1 = rot(x1, line_y, 0, 0, paper_deg)
        rx2, ry2 = rot(x2, line_y, 0, 0, paper_deg)
        ET.SubElement(slide, "line", 
                      x1=str(int(rx1+paper_cx)), y1=str(int(ry1+paper_cy)), 
                      x2=str(int(rx2+paper_cx)), y2=str(int(ry2+paper_cy)), 
                      color="#000000", width="1")

    # 5. Pen (Bottom Right)
    pen_cx, pen_cy = 1300, 750
    deg = -45
    # Build parts of pen around 0,0 and rotate
    pen_w = 26
    pen_l = 360
    
    # Shadow for entire pen (use the body+cap bounding rect)
    pen_shadow_pts = [(-pen_w/2+10, -pen_l/2+10), (pen_w/2+10, -pen_l/2+10), (pen_w/2+10, pen_l/2+10), (-pen_w/2+10, pen_l/2+10)]
    ps_rot = [rot(px, py, 0, 0, deg) for px, py in pen_shadow_pts]
    ps_str = " ".join([f"{int(x+pen_cx)},{int(y+pen_cy)}" for x, y in ps_rot])
    ET.SubElement(slide, "polygon", points=ps_str, fill="#9ABAE5", line_color="none")

    # Body
    body_pts = [(-pen_w/2, -pen_l/2 + 60), (pen_w/2, -pen_l/2 + 60), (pen_w/2, pen_l/2), (-pen_w/2, pen_l/2)]
    # Silver Cone Tip
    cone_pts = [(-pen_w/2, -pen_l/2 + 60), (pen_w/2, -pen_l/2 + 60), (6, -pen_l/2 + 20), (-6, -pen_l/2 + 20)]
    # Black tip
    tip_pts = [(-6, -pen_l/2 + 20), (6, -pen_l/2 + 20), (0, -pen_l/2)]
    # Cap (Top part of pen)
    cap_pts = [(-pen_w/2, pen_l/2 - 100), (pen_w/2, pen_l/2 - 100), (pen_w/2, pen_l/2), (-pen_w/2, pen_l/2)]
    # Clip (Silver piece on cap)
    clip_pts = [(-pen_w/2 - 6, pen_l/2 - 80), (-pen_w/2, pen_l/2 - 80), (-pen_w/2, pen_l/2 - 20), (-pen_w/2 - 6, pen_l/2 - 20)]
    
    shapes = [
        (tip_pts, "#000000"), 
        (cone_pts, "#D9D9D9"), 
        (body_pts, "#15466B"), 
        (cap_pts, "#0C304A"), 
        (clip_pts, "#D9D9D9")
    ]
    
    for shape_pts, fill in shapes:
        rot_pts = [rot(px, py, 0, 0, deg) for px, py in shape_pts]
        final_pts = [(rx + pen_cx, ry + pen_cy) for rx, ry in rot_pts]
        pts_str = " ".join([f"{int(x)},{int(y)}" for x, y in final_pts])
        ET.SubElement(slide, "polygon", points=pts_str, fill=fill, line_color="#000000", line_width="2")

    # Divider Line
    if title2:
        ET.SubElement(slide, "line", x1="450", y1="450", x2="1150", y2="450", color=title_color, width="4")

    # Title Part 1
    title1_tb = ET.SubElement(
        slide, "textbox",
        x="350", y="200",
        width="900", height="240",
        font="Arial Rounded MT Bold", font_path=font_path_bold,
        size="120", min_font_size="40",
        color=title_color, align="center", vertical_align="bottom",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="false"
    )
    title1_tb.text = title1

    # Title Part 2
    if title2:
        title2_tb = ET.SubElement(
            slide, "textbox",
            x="350", y="460",
            width="900", height="200",
            font="Arial Rounded MT Bold", font_path=font_path_bold,
            size="120", min_font_size="40",
            color=title_color, align="center", vertical_align="top",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="false"
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

target_files = [
    r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\intro_slide_xml_bundle\xml_tool.py",
    r"c:\Users\hp\Documents\SlideGenFunctionCalling_minh_rl\backend\workflows\slidegen_workflow\tools\xml_tool.py"
]

for tf in target_files:
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("# 6. ONLINE NOTEBOOK TITLE SLIDE")
    if len(parts) > 1:
        import inspect
        new_content = parts[0] + "# 6. ONLINE NOTEBOOK TITLE SLIDE\n# ==========================================================\n" + inspect.getsource(rot) + "\n" + inspect.getsource(generate_online_notebook_slide_xml)
        with open(tf, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {tf}")

if __name__ == "__main__":
    pass
