import os

new_function = """

# ==========================================================
# 3. SLIDE CREATIVE TEAM (Đội ngũ sáng tạo)
# ==========================================================
def generate_creative_team_slide_xml(
    title: str = "Our Creative Team",
    members: list[dict] = None,
    background_color: str = "#FAFAFA",
    title_color: str = "#4A4036",
) -> str:
    \"\"\"
    Sinh ra file XML cho slide Our Creative Team với 4 thẻ ảnh Polaroid nằm nghiêng nghệ thuật.
    \"\"\"
    if members is None:
        members = [
            {"name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&h=500&fit=crop"},
            {"name": "Ben Carter", "role": "Photographer", "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&h=500&fit=crop"},
            {"name": "Aisha Khan", "role": "Content Strategist", "image_url": "https://images.unsplash.com/photo-1531123897727-8f129e1bf98c?w=500&h=500&fit=crop"},
            {"name": "Leo Martinez", "role": "Illustrator", "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=500&h=500&fit=crop"},
        ]
        
    # Giới hạn tối đa 4 thành viên cho layout này
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

    # Các hằng số layout
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

    # 1. Title
    add_textbox(
        text=title,
        x=0,
        y=80,
        width=slide_width,
        height=100,
        font="Segoe UI",
        font_path=font_path_bold,
        size=72,
        min_font_size=48,
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="true",
        max_lines=1,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        bold="true",
    )

    # 2. Polaroids
    # Khung chứa 4 thẻ
    total_cards = len(members)
    card_width = 300
    card_height = 420
    gap = 40
    total_width = total_cards * card_width + (total_cards - 1) * gap
    start_x = (slide_width - total_width) / 2
    start_y = 250
    
    # Góc nghiêng cho 4 thẻ để tạo cảm giác tự nhiên ngẫu nhiên
    rotations = [-3, 2, -1, 4]

    for i, member in enumerate(members):
        x = start_x + i * (card_width + gap)
        y = start_y
        rot = rotations[i % len(rotations)]
        
        # Shadow giả lập đằng sau (Hình chữ nhật xám mờ bị dịch xuống và sang phải)
        rect_shadow = ET.SubElement(
            slide,
            "rect",
            x=str(x + 5),
            y=str(y + 10),
            width=str(card_width),
            height=str(card_height),
            fill="#E0E0E0",
            rotation=str(rot),
        )
        
        # Polaroid Card Background (Hình chữ nhật trắng)
        rect_bg = ET.SubElement(
            slide,
            "rect",
            x=str(x),
            y=str(y),
            width=str(card_width),
            height=str(card_height),
            fill="#FFFFFF",
            rotation=str(rot),
        )
        
        # Ảnh đại diện (vuông)
        img_size = 260
        img_x = x + 20
        img_y = y + 20
        
        img = ET.SubElement(
            slide,
            "image",
            x=str(img_x),
            y=str(img_y),
            width=str(img_size),
            height=str(img_size),
            src=member.get("image_url", ""),
            rotation=str(rot),
        )
        
        # Tên nhân sự
        name_y = img_y + img_size + 20
        add_textbox(
            text=member.get("name", "Name"),
            x=x,
            y=name_y,
            width=card_width,
            height=40,
            font="Segoe UI",
            font_path=font_path_bold,
            size=28,
            min_font_size=20,
            color="#333333",
            align="center",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="shrink",
            reflow_on_resize="true",
            line_spacing=1.0,
            safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            bold="true",
            rotation=str(rot),
        )
        
        # Chức danh
        role_y = name_y + 45
        add_textbox(
            text=member.get("role", "Role"),
            x=x,
            y=role_y,
            width=card_width,
            height=30,
            font="Segoe UI",
            font_path=font_path_regular,
            size=18,
            min_font_size=14,
            color="#777777",
            align="center",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="shrink",
            reflow_on_resize="true",
            line_spacing=1.0,
            safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            rotation=str(rot),
        )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(
        raw_xml
    ).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content
"""

with open(r"backend\workflows\slidegen_workflow\tools\xml_tool.py", "a", encoding="utf-8") as f:
    f.write(new_function)

print("Appended generate_creative_team_slide_xml to xml_tool.py")
