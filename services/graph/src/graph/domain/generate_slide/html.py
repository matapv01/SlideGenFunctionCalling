from __future__ import annotations

def create_default_html(content_text: str) -> str:
    if not content_text:
        content_text = "Default slide content"
    lines = content_text.split('\n')
    title = lines[0] if lines else "Slide"
    content = '<br>'.join(lines[1:]) if len(lines) > 1 else content_text
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .slide {{ width: 800px; height: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 40px; position: relative; }}
        .title {{ font-size: 32px; color: #2c3e50; margin-bottom: 30px; text-align: center; }}
        .content {{ font-size: 24px; line-height: 1.5; color: #34495e; }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="title">{title}</div>
        <div class="content">{content}</div>
    </div>
</body>
</html>"""
    return html
