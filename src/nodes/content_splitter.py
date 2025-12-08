# src/nodes/content_splitter.py

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.graph.stage import State
from langchain_core.runnables import RunnableConfig # <-- 1. IMPORT
from src.utils.config import CONTENT_CHAR_LIMIT_FOR_SPLIT
import time

# --- REVISED PROMPTS FOR HIERARCHICAL SPLITTING ---

CONTENT_SPLITTER_SYSTEM_PROMPT = """
You are a master content organizer. Your task is to take a single, large block of text and create a hierarchical (nested) breakdown of its content.

INSTRUCTIONS FOR HIERARCHICAL CONTENT SPLITTING

1.  **Analyze the Input:** You will receive the context (document title, parent headings) and a large block of text to split.
2.  **Identify Nested Structure:** Read the text to understand its internal structure. Identify main topics, which may themselves contain sub-topics.
3.  **Create a Nested Tree:** Your output will be a JSON structure that reflects this hierarchy. Use the "sub_sections" key to nest topics within each other.
4.  **Write New Sub-Headlines:** For every level of the hierarchy, write a clear and concise sub-headline.
5.  **Place Content Correctly:** The "sub_content" key MUST BE A LIST OF STRINGS. Each string in the list should be a paragraph or a logical chunk of text. This avoids newline issues.

## RULE #1: PRESERVE ALL INFORMATION (NON-NEGOTIABLE)
- Your primary goal is to **re-organize, not summarize**.
- **Every single sentence from the original content MUST be present** in the final output, distributed across the various `sub_content` fields in your JSON tree.

## CRITICAL OUTPUT REQUIREMENT:
- You MUST return ONLY a single, syntactically correct JSON array of objects.
- Do not add any introductory text, explanations, or markdown formatting around the JSON.
- Each object must have "sub_headline" and "sub_sections".
- The "sub_content" key MUST BE A LIST OF STRINGS (`["line 1", "line 2", ...]`).

EXAMPLE OUTPUT FORMAT (showing nesting):
```json
[
  {{
    "sub_headline": "Main Topic A",
    "sub_content": [
      "This is the introductory text for Main Topic A.",
      "It can have multiple paragraphs, each as a separate string in the list."
    ],
    "sub_sections": [
      {{
        "sub_headline": "Sub-Topic A.1",
        "sub_content": ["Content specifically about A.1."],
        "sub_sections": []
      }},
      {{
        "sub_headline": "Sub-Topic A.2",
        "sub_content": ["Content specifically about A.2."],
        "sub_sections": []
      }}
    ]
  }},
  {{
    "sub_headline": "Main Topic B",
    "sub_content": ["This is the text for Main Topic B, which has no further sub-sections."],
    "sub_sections": []
  }}
]
```
"""

HUMAN_PROMPT_TEMPLATE = """
---
INPUT CONTEXT FOR THIS TASK:

- **Document Title:** {document_title}
- **Parent Headings:** {parent_headings}
- **Current Section Heading:** {current_heading}

---
CONTENT TO SPLIT:

{content_to_split}
"""

def _convert_llm_tree_to_nodes(llm_json_list: List[Dict], parent_level: int) -> List[Dict]:
    """
    Recursively converts the LLM's nested JSON output into the standard
    node format used by the document_structure.
    """
    new_nodes = []
    for item in llm_json_list:
        if "sub_headline" not in item or "sub_content" not in item:
            continue # Skip malformed items

        new_node = {
            "level": parent_level + 1,
            "title": item["sub_headline"],
            "content": "\n".join(item.get("sub_content", [])),
            "children": [] # Default to empty
        }

        # If there are nested sections, recurse!
        if item.get("sub_sections") and isinstance(item["sub_sections"], list):
            new_node["children"] = _convert_llm_tree_to_nodes(item["sub_sections"], parent_level + 1)

        new_nodes.append(new_node)
    return new_nodes


def split_content(state: State, config: RunnableConfig) -> State: # <-- 2. ADD CONFIG
    """
    Traverses the document structure and uses an LLM to hierarchically split
    any nodes with content exceeding a defined character limit.
    """
    print("\n---------------- Executing Node: split_content ----------------")
    start_time = time.time()
    # --- 3. GET RESOURCES FROM CONFIG ---
    configurable = config["configurable"]
    llm = configurable.get('llm')
    
    # Emit streaming event
    stream_callback = configurable.get('stream_callback')
    if stream_callback:
        stream_callback('status', {
            'step': 2,
            'title': 'Chuẩn bị nội dung',
            'description': 'Đang phân tích và tổ chức nội dung...',
            'message': 'Đang xử lý cấu trúc tài liệu'
        })

    if not llm:
        raise ValueError("LLM is not found in config. Cannot proceed with content splitting.")

    # Get dynamic data from state
    document_title = state.get('document_title', 'Untitled Document')
    document_structure = state.get('document_structure', [])

    prompt = ChatPromptTemplate.from_messages([
        ("system", CONTENT_SPLITTER_SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT_TEMPLATE)
    ])

    # Note: Using the raw .llm attribute if your LLM class wraps it
    chain = prompt | llm.llm | StrOutputParser()

    def _process_node(node: Dict[str, Any], parent_headings: List[str]):
        """Recursively checks and splits content for a node and its children."""

        current_heading = node.get('numbered_title', node.get('title', ''))

        if node.get('content') and len(node['content']) > CONTENT_CHAR_LIMIT_FOR_SPLIT:
            print(f"Found oversized content in section '{current_heading}'. Attempting hierarchical split...")

            llm_response_str = chain.invoke({
                "document_title": document_title,
                "parent_headings": " -> ".join(parent_headings),
                "current_heading": current_heading,
                "content_to_split": node['content']
            })

            try:
                # 1. Clean and find the JSON substring
                # This is more robust against markdown code blocks or other text
                start_index = llm_response_str.find('[')
                if start_index == -1: start_index = llm_response_str.find('{')

                end_index = llm_response_str.rfind(']')
                if end_index == -1: end_index = llm_response_str.rfind('}')

                if start_index == -1 or end_index == -1:
                    raise ValueError("Could not find a JSON-like object in the response.")

                substring = llm_response_str[start_index : end_index + 1]

                # 2. Parse using strict=False. This can help with some formatting issues.
                split_data = json.loads(substring, strict=False)

                # If the LLM returns a single dict instead of a list
                if isinstance(split_data, dict):
                    split_data = [split_data]

                if not isinstance(split_data, list):
                    raise ValueError("LLM response is not a JSON list or object.")

                # Convert the LLM's nested tree into our standard node format
                new_children = _convert_llm_tree_to_nodes(split_data, node['level'])

                if not new_children:
                     raise ValueError("Failed to convert LLM response into valid nodes.")

                print(f"  -> LLM successfully created a nested structure. Adding {len(new_children)} top-level new sections.")

                # Replace the old content with the new hierarchical child nodes
                node['content'] = "" # Clear the original long content
                node['children'] = new_children + node.get('children', []) # Prepend new structure

            except (json.JSONDecodeError, ValueError) as e:
                print(f"  -> FAILED to process LLM response for '{current_heading}'. Keeping original content. Error: {e}")
                print(f"  -> LLM raw response was: {llm_response_str}")

        # Recurse into all children (including any that were just added)
        new_parent_headings = parent_headings + [current_heading]
        for child_node in node.get('children', []):
            _process_node(child_node, new_parent_headings)

    # Start the recursive process from the root nodes
    for root_node in document_structure:
        _process_node(root_node, [])

    state['document_structure'] = document_structure
    end_time = time.time()
    print(f"Content splitting took {end_time - start_time:.2f} seconds.")
    print("Hierarchical content splitting process complete.")
    return state