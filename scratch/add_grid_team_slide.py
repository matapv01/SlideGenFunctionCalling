import os

new_function = """

# ==========================================================
# 4. SLIDE GRID TEAM (2x2 Grid)
# ==========================================================
def generate_grid_team_slide_xml(
    title: str = "Add a Team\\nMembers\\nPage",
    members: list[dict] = None,
    background_color: str = "#F8FAFC",
    title_color: str = "#1A2530",
) -> str:
    \"\"\"
    Sinh ra file XML cho slide Add a Team Members Page với Grid 2x2.
    \"\"\"
    if members is None:
        members = [
            {"name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&h=300&fit=crop"},
            {"name": "Ben Carter", "role": "Frontend Developer", "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop"},
            {"name": "Aisha Khan", "role": "Project Manager", "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop"},
            {"name": "Leo Martinez", "role": "Marketing Head", "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&h=300&fit=crop"},
        ]
        
    members = members[:4]

    slide_width = 1600
    slide_height = 900

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(slide_width),
        height=str(slide_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        background=background_color,
    )

    import sys
    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_bold = "C:/Windows/Fonts/segoeuib.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Bold.ttf"

    def add_textbox(**kwargs):
        tb = ET.SubElement(slide, "textbox")
        for k, v in kwargs.items():
            if k == 'text':
                tb.text = str(v)
            else:
                tb.set(k, str(v))
        return tb

    # 1. Title (Left side)
    add_textbox(
        text=title,
        x=150,
        y=280,
        width=500,
        height=300,
        font="Segoe UI",
        font_path=font_path_bold,
        size=72,
        min_font_size=48,
        color=title_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=3,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.1,
        safety_ratio=1.0,
        margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        bold="true",
    )
    
    # Colorful gradient line below title
    colors = ["#8E44AD", "#27AE60", "#E74C3C", "#F1C40F"]
    line_y = 570
    for i, color in enumerate(colors):
        ET.SubElement(
            slide, "shape", type="rectangle",
            x=str(150 + i * 25), y=str(line_y),
            width="25", height="5",
            fill=color
        )

    # 2. Grid (Right side)
    card_width = 320
    card_height = 180
    img_size = 120
    col_gap = 40
    row_gap = 100
    
    start_x = 750
    start_y = 200

    for i, member in enumerate(members):
        col = i % 2
        row = i // 2
        
        x = start_x + col * (card_width + col_gap)
        y = start_y + row * (card_height + row_gap)
        color = colors[i % len(colors)]
        
        # Shadow
        ET.SubElement(
            slide, "shape", type="rounded_rectangle",
            x=str(x + 5), y=str(y + 8),
            width=str(card_width), height=str(card_height),
            fill="#EAECEE"
        )
        
        # White Card
        ET.SubElement(
            slide, "shape", type="rounded_rectangle",
            x=str(x), y=str(y),
            width=str(card_width), height=str(card_height),
            fill="#FFFFFF"
        )
        
        # Image Border Ring
        img_x = x + (card_width - img_size) / 2
        img_y = y - (img_size / 2)
        ET.SubElement(
            slide, "shape", type="circle",
            x=str(img_x - 5), y=str(img_y - 5),
            width=str(img_size + 10), height=str(img_size + 10),
            fill=color
        )
        # Inner white ring
        ET.SubElement(
            slide, "shape", type="circle",
            x=str(img_x - 2), y=str(img_y - 2),
            width=str(img_size + 4), height=str(img_size + 4),
            fill="#FFFFFF"
        )
        
        # Image (circle shaped)
        ET.SubElement(
            slide, "image",
            x=str(img_x), y=str(img_y),
            width=str(img_size), height=str(img_size),
            src=member.get("image_url", ""),
            shape="circle"
        )
        
        # Name
        name_y = img_y + img_size + 15
        add_textbox(
            text=member.get("name", "Name"),
            x=x, y=name_y,
            width=card_width, height=40,
            font="Segoe UI", font_path=font_path_bold,
            size=28, min_font_size=20,
            color="#2C3E50", align="center", vertical_align="middle",
            single_line="true", max_lines=1, overflow="shrink", reflow_on_resize="true",
            line_spacing=1.0, safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            bold="true",
        )
        
        # Role
        role_y = name_y + 40
        add_textbox(
            text=member.get("role", "Role"),
            x=x, y=role_y,
            width=card_width, height=30,
            font="Segoe UI", font_path=font_path_regular,
            size=18, min_font_size=14,
            color="#7F8C8D", align="center", vertical_align="middle",
            single_line="true", max_lines=1, overflow="shrink", reflow_on_resize="true",
            line_spacing=1.0, safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content
"""

with open(r"backend\workflows\slidegen_workflow\tools\xml_tool.py", "a", encoding="utf-8") as f:
    f.write(new_function)

print("Appended generate_grid_team_slide_xml to xml_tool.py")
