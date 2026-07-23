from typing import Dict, List


def _convert_llm_tree_to_nodes(llm_json_list: List[Dict], parent_level: int) -> List[Dict]:
    """
    Recursively convert nested LLM JSON output into document_structure node format.
    """
    new_nodes = []
    for item in llm_json_list:
        if "sub_headline" not in item or "sub_content" not in item:
            continue

        new_node = {
            "level": parent_level + 1,
            "title": item["sub_headline"],
            "content": "\n".join(item.get("sub_content", [])),
            "children": [],
        }

        if item.get("sub_sections") and isinstance(item["sub_sections"], list):
            new_node["children"] = _convert_llm_tree_to_nodes(
                item["sub_sections"], parent_level + 1
            )

        new_nodes.append(new_node)

    return new_nodes
