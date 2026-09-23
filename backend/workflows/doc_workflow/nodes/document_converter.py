import json
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.runnables import RunnableConfig
from markitdown import MarkItDown

from backend.workflows.doc_workflow.graph.stage import State


def parse_markdown_to_hierarchical_json(markdown_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Parse markdown into hierarchical sections by heading levels."""
    lines = markdown_text.strip().split("\n")
    root_nodes: List[Dict[str, Any]] = []
    ancestry_stack: List[Dict[str, Any]] = []
    preamble_lines: List[str] = []
    first_heading_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        heading_match = re.match(r"^(#+)\s+(.*)", line)

        if heading_match:
            first_heading_found = True
            level = len(heading_match.group(1))
            raw_title = heading_match.group(2).strip().replace("**", "")
            clean_title = re.sub(r"^\s*(\d+(\.\d+)*)\.?\s*", "", raw_title).strip()

            new_node = {
                "level": level,
                "title": clean_title,
                "content": [],
                "children": [],
            }

            while ancestry_stack and ancestry_stack[-1]["level"] >= level:
                ancestry_stack.pop()

            if not ancestry_stack:
                root_nodes.append(new_node)
            else:
                ancestry_stack[-1]["children"].append(new_node)

            ancestry_stack.append(new_node)
        else:
            if not first_heading_found:
                preamble_lines.append(line.replace("**", ""))
            elif ancestry_stack:
                ancestry_stack[-1]["content"].append(line)

    def _join_content_recursively(node: Dict[str, Any]) -> None:
        node["content"] = "\n".join(node.get("content", [])).strip()
        for child in node.get("children", []):
            _join_content_recursively(child)

    for root_node in root_nodes:
        _join_content_recursively(root_node)

    preamble_content = "\n".join(preamble_lines).strip()
    return preamble_content, root_nodes


def convert_document(state: State, config: Optional[RunnableConfig] = None) -> State:
    """Convert DOCX to markdown and detect heading-based structure."""
    print("\n---------------- Executing Node: convert_document ----------------")

    if state.get("slide_chunks"):
        print("Skipping convert_document: slide_chunks already exists")
        return state

    start_time = time.time()
    docx_file = state["docx_file"]

    if config:
        configurable = config.get("configurable", {})
        stream_callback = configurable.get("stream_callback")
        if stream_callback:
            stream_callback(
                "status",
                {
                    "step": 1,
                    "title": "Analyze Content",
                    "description": "Reading and converting document...",
                    "message": f"Processing file: {os.path.basename(docx_file) if docx_file else 'Unknown'}",
                },
            )

    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The specified DOCX file was not found: {docx_file}")

    converter = MarkItDown()
    markdown_text = converter.convert(docx_file).text_content

    preamble, structure = parse_markdown_to_hierarchical_json(markdown_text)

    state["plain_text"] = markdown_text
    state["document_preamble"] = preamble

    has_structure = len(structure) > 0
    workflow_mode = state.get("workflow_mode", "auto")

    if workflow_mode == "auto_heading" and not has_structure:
        raise ValueError(
            "Document does not contain heading structure, but mode auto_heading was selected. "
            "Please add headings to document or use auto_no_heading mode."
        )

    if has_structure:
        # A DOCX title is metadata, not the whole pre-heading block. Keep the
        # complete block in document_preamble for the mixed-structure pass.
        title = next((line.strip() for line in preamble.splitlines() if line.strip()), "")
        if not title:
            title = os.path.splitext(os.path.basename(docx_file))[0]
        state["document_title"] = title
        state["document_structure"] = structure
        state["document_structure_origin"] = "headings"
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    else:
        # No explicit headings means the complete document is the one
        # unstructured region. auto_structure will process plain_text as a
        # whole and the preamble remains available as the source of truth.
        state["document_title"] = os.path.splitext(os.path.basename(docx_file))[0]
        state["document_structure"] = []
        state["document_structure_origin"] = "unstructured"

    end_time = time.time()
    print(f"Document conversion took {end_time - start_time:.2f} seconds.")

    return state
