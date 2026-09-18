from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import struct
import zlib
from zipfile import ZIP_DEFLATED, ZipFile


OUT = Path("triet_tue_nhan_tao_ai.docx")


def esc(value: str) -> str:
    return escape(value, quote=True)


def paragraph(text: str = "", style: str = "Normal", align: str | None = None,
             before: int | None = None, after: int | None = None,
             keep_next: bool = False) -> str:
    ppr = [f'<w:pStyle w:val="{esc(style)}"/>']
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    spacing = []
    if before is not None:
        spacing.append(f'w:before="{before}"')
    if after is not None:
        spacing.append(f'w:after="{after}"')
    if spacing:
        ppr.append(f'<w:spacing {" ".join(spacing)}/>')
    if keep_next:
        ppr.append('<w:keepNext/>')
    runs = []
    if text:
        runs.append(f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r>')
    return f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{"".join(runs)}</w:p>'


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table_cell(text: str, header: bool = False) -> str:
    shading = '<w:shd w:fill="0F766E"/>' if header else ''
    color = '<w:color w:val="FFFFFF"/>' if header else ''
    bold = '<w:b/>' if header else ''
    run = f'<w:r><w:rPr>{bold}{color}<w:font w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/></w:rPr><w:t>{esc(text)}</w:t></w:r>'
    return f'<w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/>{shading}</w:tcPr><w:p><w:pPr><w:jc w:val="center"/></w:pPr>{run}</w:p></w:tc>'


def data_table() -> str:
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    values = ["18", "29", "41", "55", "69", "82"]
    rows = [
        '<w:tr>' + table_cell("Năm", True) + table_cell("Chỉ số ứng dụng AI", True) + '</w:tr>'
    ]
    for year, value in zip(years, values):
        rows.append('<w:tr>' + table_cell(year) + table_cell(value) + '</w:tr>')
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="6000" w:type="dxa"/>'
        '<w:jc w:val="center"/></w:tblPr><w:tblGrid><w:gridCol w:w="3000"/><w:gridCol w:w="3000"/></w:tblGrid>'
        + ''.join(rows) + '</w:tbl>'
    )


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def chart_png() -> bytes:
    """Create a small dependency-free PNG line chart for maximum Word compatibility."""
    width, height = 900, 500
    background = (247, 251, 251, 255)
    pixels = [bytearray(background * width) for _ in range(height)]

    def set_pixel(x: int, y: int, color: tuple[int, int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            offset = x * 4
            pixels[y][offset:offset + 4] = bytes(color)

    def draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int], thickness: int = 1) -> None:
        dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
        error = dx + dy
        radius = max(0, thickness // 2)
        while True:
            for yy in range(y0 - radius, y0 + radius + 1):
                for xx in range(x0 - radius, x0 + radius + 1):
                    set_pixel(xx, yy, color)
            if x0 == x1 and y0 == y1:
                break
            double = 2 * error
            if double >= dy:
                error += dy
                x0 += sx
            if double <= dx:
                error += dx
                y0 += sy

    def draw_circle(cx: int, cy: int, radius: int, color: tuple[int, int, int, int]) -> None:
        r2 = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                    set_pixel(x, y, color)

    left, right, top, bottom = 105, 835, 95, 405
    values = [18, 29, 41, 55, 69, 82]
    x_step = (right - left) / 5
    to_xy = lambda i, value: (round(left + i * x_step), round(bottom - value / 100 * (bottom - top)))
    grid = (215, 228, 228, 255)
    axis = (73, 98, 100, 255)
    teal = (15, 118, 110, 255)
    for value in range(0, 101, 20):
        y = round(bottom - value / 100 * (bottom - top))
        draw_line(left, y, right, y, grid, 1)
    draw_line(left, top, left, bottom, axis, 2)
    draw_line(left, bottom, right, bottom, axis, 2)
    points = [to_xy(i, value) for i, value in enumerate(values)]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        draw_line(x0, y0, x1, y1, teal, 5)
    for x, y in points:
        draw_circle(x, y, 8, (255, 255, 255, 255))
        draw_circle(x, y, 5, teal)

    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", zlib.compress(raw, 9)) + _png_chunk(b"IEND", b"")


def chart_svg() -> bytes:
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    values = [18, 29, 41, 55, 69, 82]
    left, right, top, bottom = 105, 835, 95, 405
    max_value = 100
    x_step = (right - left) / (len(years) - 1)

    def x_at(index: int) -> float:
        return left + index * x_step

    def y_at(value: int) -> float:
        return bottom - value / max_value * (bottom - top)

    points = " ".join(f"{x_at(i):.1f},{y_at(v):.1f}" for i, v in enumerate(values))
    grid = []
    for value in range(0, 101, 20):
        y = y_at(value)
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#D7E4E4" stroke-width="1"/>'
            f'<text x="82" y="{y + 5:.1f}" text-anchor="end" font-size="15" fill="#526568">{value}</text>'
        )
    ticks = []
    for i, year in enumerate(years):
        x = x_at(i)
        ticks.append(
            f'<line x1="{x:.1f}" y1="{bottom}" x2="{x:.1f}" y2="{bottom + 7}" stroke="#496264" stroke-width="1"/>'
            f'<text x="{x:.1f}" y="{bottom + 32}" text-anchor="middle" font-size="15" fill="#526568">{year}</text>'
        )
    labels = []
    for i, value in enumerate(values):
        x, y = x_at(i), y_at(value)
        labels.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#FFFFFF" stroke="#0F766E" stroke-width="3"/>'
            f'<text x="{x:.1f}" y="{y - 15:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="#0F766E">{value}</text>'
        )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <rect width="900" height="500" rx="18" fill="#F7FBFB"/>
  <text x="450" y="42" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#173C3F">Mức độ ứng dụng AI theo thời gian</text>
  <text x="450" y="70" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#526568">Chỉ số minh họa trên thang 0–100</text>
  {''.join(grid)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#496264" stroke-width="2"/>
  <line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#496264" stroke-width="2"/>
  {''.join(ticks)}
  <polyline points="{points}" fill="none" stroke="#0F766E" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  {''.join(labels)}
  <text x="470" y="466" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#526568">Năm</text>
  <text x="25" y="250" transform="rotate(-90 25 250)" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#526568">Chỉ số ứng dụng AI</text>
</svg>'''
    return svg.encode("utf-8")


def image_paragraph() -> str:
    return '''
<w:p>
  <w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="80"/></w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="5943600" cy="3302000"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="1" name="AI line chart" descr="Biểu đồ đường minh họa mức độ ứng dụng AI theo thời gian"/>
        <wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr><pic:cNvPr id="0" name="ai_line_chart.png"/><pic:cNvPicPr/></pic:nvPicPr>
              <pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="rId4"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
              <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5943600" cy="3302000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>'''


def document_xml() -> str:
    body = []
    body.append(paragraph("TRÍ TUỆ NHÂN TẠO (AI)", "Title", "center", after=80, keep_next=True))
    body.append(paragraph("Tổng quan, công nghệ và ứng dụng", "Subtitle", "center", after=320))

    sections = [
        (
            "1. Tổng quan về Trí tuệ nhân tạo",
            "Trí tuệ nhân tạo (Artificial Intelligence – AI) là lĩnh vực của khoa học máy tính tập trung vào việc xây dựng các hệ thống có khả năng thực hiện những nhiệm vụ thường cần đến sự thông minh của con người. Các khả năng phổ biến gồm học từ dữ liệu, nhận diện hình ảnh, hiểu ngôn ngữ, suy luận, dự đoán và ra quyết định.",
            "AI ngày càng phát triển nhờ sự gia tăng của dữ liệu, năng lực tính toán và các thuật toán học máy hiện đại. Từ các hệ thống đề xuất nội dung đến trợ lý ảo và xe tự hành, AI đang trở thành một thành phần quan trọng trong nhiều lĩnh vực.",
        ),
        (
            "2. Các công nghệ cốt lõi của AI",
            "Một số công nghệ nền tảng của AI gồm Machine Learning (học máy), Deep Learning (học sâu), Computer Vision (thị giác máy tính) và Natural Language Processing (xử lý ngôn ngữ tự nhiên).",
            "Machine Learning cho phép mô hình học quy luật từ dữ liệu thay vì phải lập trình mọi quy tắc thủ công. Deep Learning sử dụng các mạng nơ-ron nhiều lớp để xử lý dữ liệu phức tạp. Computer Vision tập trung vào hình ảnh và video, trong khi NLP giúp máy tính phân tích và sinh ngôn ngữ tự nhiên.",
        ),
        (
            "3. Quy trình xây dựng một hệ thống AI",
            "Một hệ thống AI thường bắt đầu từ việc xác định bài toán và thu thập dữ liệu. Dữ liệu sau đó được làm sạch, gán nhãn hoặc biến đổi để phù hợp với mô hình. Tiếp theo, dữ liệu được chia thành các tập huấn luyện, kiểm thử và đánh giá.",
            "Sau khi lựa chọn thuật toán, mô hình được huấn luyện và tối ưu các tham số. Cuối cùng, mô hình được đánh giá bằng các chỉ số phù hợp và triển khai vào ứng dụng thực tế. Trong quá trình vận hành, hệ thống cần được theo dõi và cập nhật khi dữ liệu hoặc yêu cầu thay đổi.",
        ),
        (
            "4. Ứng dụng của AI trong thực tế",
            "AI được ứng dụng rộng rãi trong y tế, tài chính, giáo dục, sản xuất, giao thông và thương mại. Trong y tế, AI có thể hỗ trợ phân tích ảnh y khoa và dự đoán nguy cơ bệnh. Trong tài chính, AI được dùng để phát hiện giao dịch bất thường và đánh giá rủi ro.",
            "Trong doanh nghiệp, AI còn hỗ trợ chatbot, tìm kiếm thông tin, phân tích tài liệu, tự động hóa quy trình và tạo nội dung. Generative AI cho phép tạo văn bản, hình ảnh, âm thanh và mã nguồn dựa trên yêu cầu của người dùng.",
        ),
        (
            "5. Thách thức và xu hướng phát triển",
            "Bên cạnh tiềm năng lớn, AI vẫn tồn tại các vấn đề như chất lượng dữ liệu, độ chính xác, chi phí tính toán, bảo mật và quyền riêng tư. Mô hình cũng có thể tạo ra kết quả sai hoặc mang thiên kiến nếu dữ liệu và quy trình đánh giá không phù hợp.",
            "Trong tương lai, AI được dự đoán tiếp tục phát triển theo hướng mô hình đa phương thức, AI Agent, hệ thống RAG, mô hình nhỏ chạy trên thiết bị biên và các giải pháp AI có khả năng phối hợp nhiều công cụ. Việc phát triển AI có trách nhiệm, minh bạch và an toàn sẽ ngày càng quan trọng.",
        ),
    ]

    for title, first, second in sections:
        body.append(paragraph(title, "Heading1", before=220, after=100, keep_next=True))
        body.append(paragraph(first, "Normal", after=100))
        body.append(paragraph(second, "Normal", after=140))

    body.append(page_break())
    body.append(paragraph("6. Xu hướng gia tăng mức độ ứng dụng AI", "Heading1", before=80, after=100, keep_next=True))
    body.append(paragraph(
        "Cùng với sự trưởng thành của hạ tầng dữ liệu, điện toán đám mây và các mô hình nền tảng, mức độ ứng dụng AI có xu hướng tăng qua thời gian. Doanh nghiệp thường bắt đầu từ các bài toán có phạm vi rõ ràng như chatbot, tự động hóa quy trình và phân tích dữ liệu, sau đó mở rộng sang các hệ thống hỗ trợ ra quyết định và Generative AI.",
        "Normal", after=100,
    ))
    body.append(paragraph(
        "Biểu đồ đường dưới đây minh họa cách trình bày xu hướng này. Chỉ số được chuẩn hóa trên thang 0–100 để phục vụ mục đích minh họa; khi sử dụng trong báo cáo chính thức, có thể thay bằng dữ liệu khảo sát hoặc số liệu doanh nghiệp thực tế.",
        "Normal", after=120,
    ))
    body.append(image_paragraph())
    body.append(paragraph("Bảng dữ liệu dùng cho biểu đồ", "Heading2", before=100, after=60, keep_next=True))
    body.append(data_table())
    body.append(paragraph(
        "Ghi chú: Số liệu trong bảng là dữ liệu minh họa, không đại diện cho một nguồn thống kê chính thức.",
        "Caption", "left", before=80, after=0,
    ))

    sect_pr = '''<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'''
    body.append(sect_pr)
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>''' + ''.join(body) + '''</w:body>
</w:document>'''


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:lang w:val="vi-VN"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:line="276" w:lineRule="auto" w:after="120"/></w:pPr><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="80"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:b/><w:color w:val="0F766E"/><w:sz w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:pPr><w:jc w:val="center"/><w:spacing w:after="320"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:i/><w:color w:val="526568"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="260" w:after="100"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:b/><w:color w:val="0F766E"/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="60"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:b/><w:color w:val="173C3F"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:i/><w:color w:val="526568"/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>'''


def settings_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>'''


def content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>'''


def root_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def document_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/ai_line_chart.png"/>
</Relationships>'''


def core_xml() -> str:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Trí tuệ nhân tạo (AI) – Tổng quan, công nghệ và ứng dụng</dc:title>
  <dc:subject>Tổng quan, công nghệ, ứng dụng và xu hướng AI</dc:subject>
  <dc:creator>OpenAI</dc:creator>
  <cp:lastModifiedBy>OpenAI</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>'''


def app_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Office Word</Application><DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><Company></Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>'''


def theme_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F497D"/></a:dk2><a:lt2><a:srgbClr val="EEECE1"/></a:lt2><a:accent1><a:srgbClr val="4F81BD"/></a:accent1><a:accent2><a:srgbClr val="C0504D"/></a:accent2><a:accent3><a:srgbClr val="9BBB59"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4><a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="Office"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>'''


def build_docx() -> None:
    with ZipFile(OUT, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types_xml())
        docx.writestr("_rels/.rels", root_rels_xml())
        docx.writestr("word/document.xml", document_xml())
        docx.writestr("word/_rels/document.xml.rels", document_rels_xml())
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/settings.xml", settings_xml())
        docx.writestr("word/media/ai_line_chart.png", chart_png())
        docx.writestr("word/theme/theme1.xml", theme_xml())
        docx.writestr("docProps/core.xml", core_xml())
        docx.writestr("docProps/app.xml", app_xml())


if __name__ == "__main__":
    build_docx()
    print(OUT.resolve())
