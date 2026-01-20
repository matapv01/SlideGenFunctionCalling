# File: src/nodes/content_splitter.py

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.graph.stage import State
from langchain_core.runnables import RunnableConfig
from src.utils.config import CONTENT_CHAR_LIMIT_FOR_SPLIT
from src.utils.helper import _convert_llm_tree_to_nodes
from src.utils.prompts import CONTENT_SPLITTER_SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE
import time


def split_content(state: State, config: RunnableConfig) -> State:
    """
    Traverses the document structure and uses an LLM to hierarchically split
    any nodes with content exceeding a defined character limit.
    SKIP if slide_chunks already exists (from idea generation)
    """
    print("\n---------------- Executing Node: split_content ----------------")

    # Skip if slide_chunks already provided (idea-based workflow)
    if state.get('slide_chunks'):
        print("⏭️  Skipping split_content: slide_chunks already exists")
        return state

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
                if start_index == -1:
                    start_index = llm_response_str.find('{')

                end_index = llm_response_str.rfind(']')
                if end_index == -1:
                    end_index = llm_response_str.rfind('}')

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
                node['content'] = ""  # Clear the original long content
                node['children'] = new_children + node.get('children', [])  # Prepend new structure

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
    print(json.dumps(document_structure, indent=2, ensure_ascii=False))
    end_time = time.time()
    print(f"Content splitting took {end_time - start_time:.2f} seconds.")
    print("Hierarchical content splitting process complete.")
    return state
