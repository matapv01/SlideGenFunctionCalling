"""
Markdown to Hierarchical JSON Parser Utility
Reusable parser for generated scripts and the Structure Editor adapter
"""

import re
from typing import Dict, Any, List, Tuple


def parse_markdown_to_hierarchical_json(markdown_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Parses a Markdown string into a hierarchical JSON structure.
    Strips pre-existing numbering from titles (e.g., "1.", "2.1")
    
    Args:
        markdown_text: Markdown formatted text with headings
        
    Returns:
        Tuple of (title_from_preamble, hierarchical_structure)
        
    Example:
        Input:
        ```
        # Chương 1
        Nội dung chương 1
        
        ## Phần 1.1
        Nội dung phần
        ```
        
        Output:
        [
            {
                "level": 1,
                "title": "Chương 1",
                "content": "Nội dung chương 1",
                "children": [
                    {
                        "level": 2,
                        "title": "Phần 1.1",
                        "content": "Nội dung phần",
                        "children": []
                    }
                ]
            }
        ]
    """
    lines = markdown_text.strip().split('\n')
    root_nodes, ancestry_stack, preamble_lines = [], [], []
    first_heading_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        heading_match = re.match(r'^(#+)\s+(.*)', line)

        if heading_match:
            first_heading_found = True
            level = len(heading_match.group(1))
            raw_title = heading_match.group(2).strip().replace('**', '')

            # Strip leading numbers like "1.", "3.1", etc.
            clean_title = re.sub(r'^\s*(\d+(\.\d+)*)\.?\s*', '', raw_title).strip()

            new_node = {"level": level, "title": clean_title, "content": [], "children": []}

            # Navigate ancestry stack to correct insertion point
            while ancestry_stack and ancestry_stack[-1]['level'] >= level:
                ancestry_stack.pop()
                
            if not ancestry_stack:
                root_nodes.append(new_node)
            else:
                ancestry_stack[-1]['children'].append(new_node)
            ancestry_stack.append(new_node)
        else:
            # Non-heading lines are content
            if not first_heading_found:
                preamble_lines.append(line.replace('**', ''))
            elif ancestry_stack:
                ancestry_stack[-1]['content'].append(line)

    # Join content recursively
    def _join_content_recursively(node):
        node['content'] = "\n".join(node.get('content', [])).strip()
        for child in node.get('children', []):
            _join_content_recursively(child)

    for root_node in root_nodes:
        _join_content_recursively(root_node)

    preamble_content = "\n".join(preamble_lines).strip()
    return preamble_content, root_nodes


def validate_markdown_structure(structure: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate hierarchical structure has required fields
    
    Args:
        structure: Hierarchical node structure
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    def validate_node(node: Dict, expected_level: int = 1, path: str = "root"):
        if not isinstance(node, dict):
            errors.append(f"Node at {path} is not a dict")
            return
            
        if 'level' not in node or 'title' not in node:
            errors.append(f"Node at {path} missing 'level' or 'title'")
            return
            
        # Warn if level doesn't match hierarchy
        if node.get('level') != expected_level:
            errors.append(f"Node '{node.get('title')}' has level {node.get('level')}, expected {expected_level}")
            
        # Check for empty title
        if not node.get('title', '').strip():
            errors.append(f"Empty title at {path}")
            
        # Recursively validate children
        for i, child in enumerate(node.get('children', [])):
            validate_node(child, node.get('level', 1) + 1, f"{path}.children[{i}]")
    
    for i, node in enumerate(structure):
        validate_node(node, 1, f"root[{i}]")
    
    return len(errors) == 0, errors


def markdown_to_manual_structure(markdown_text: str, default_title: str = "Document") -> Tuple[str, List[Dict[str, Any]]]:
    """
    Convert markdown to manual structure format (with node_ids for StructureEditor)
    
    Args:
        markdown_text: Raw markdown input
        default_title: Default title if no preamble
        
    Returns:
        Tuple of (document_title, structure_with_node_ids)
    """
    title, structure = parse_markdown_to_hierarchical_json(markdown_text)
    document_title = title if title.strip() else default_title
    
    # Add node_ids and format for StructureEditor
    def add_node_ids(nodes, level=0):
        result = []
        for idx, node in enumerate(nodes):
            node_id = f"md_node_{level}_{idx}"
            result.append({
                "node_id": node_id,
                "level": node.get('level', 1),
                "title": node.get('title', ''),
                "content": node.get('content', ''),
                "children": add_node_ids(node.get('children', []), level + 1),
                "is_transition": False
            })
        return result
    
    structured = add_node_ids(structure)
    return document_title, structured
