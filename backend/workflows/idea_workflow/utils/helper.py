from typing import Dict, List
import logging
import base64


def _convert_llm_tree_to_nodes(llm_json_list: List[Dict], parent_level: int) -> List[Dict]:
    """
    Recursively converts the LLM's nested JSON output into the standard
    node format used by the document_structure.
    """
    new_nodes = []
    for item in llm_json_list:
        if "sub_headline" not in item or "sub_content" not in item:
            continue  # Skip malformed items

        new_node = {
            "level": parent_level + 1,
            "title": item["sub_headline"],
            "content": "\n".join(item.get("sub_content", [])),
            "children": []  # Default to empty
        }

        # If there are nested sections, recurse!
        if item.get("sub_sections") and isinstance(item["sub_sections"], list):
            new_node["children"] = _convert_llm_tree_to_nodes(item["sub_sections"], parent_level + 1)

        new_nodes.append(new_node)
    return new_nodes


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    if image_path is None:
        logging.warning("Image path is None, cannot convert to base64")
        return ""

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image to base64: {image_path}, Error: {e}")
        return ""


def create_default_html(content_data) -> str:
    """Create default HTML when unable to get from LLM"""
    # Handle both dict and string formats
    if isinstance(content_data, dict):
        title = content_data.get('heading', 'Slide')
        content_text = content_data.get('text_content', 'Default slide content')
    else:
        content_text = content_data if content_data else "Default slide content"
        title = "Slide"

    lines = content_text.split('\n')
    if not title:
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
