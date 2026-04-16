import json
import time
from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from backend.config import CONTENT_CHAR_LIMIT_FOR_SPLIT
from backend.workflows.doc_workflow.graph.stage import State
from backend.workflows.doc_workflow.utils.helper import _convert_llm_tree_to_nodes
from backend.workflows.doc_workflow.utils.prompts import (
    CONTENT_SPLITTER_SYSTEM_PROMPT,
    CONTENT_SPLITTER_USER_PROMPT,
)


def split_content(state: State, config: RunnableConfig) -> State:
    """
    Traverse and hierarchically split oversized section content using LLM.
    """
    print("\n---------------- Executing Node: split_content ----------------")

    if state.get("slide_chunks"):
        print("Skipping split_content: slide_chunks already exists")
        return state

    start_time = time.time()

    configurable = config["configurable"]
    llm = configurable.get("llm")

    stream_callback = configurable.get("stream_callback")
    if stream_callback:
        stream_callback(
            "status",
            {
                "step": 2,
                "title": "Prepare Content",
                "description": "Analyzing and organizing content...",
                "message": "Processing document structure",
            },
        )
        time.sleep(2)

    if not llm:
        raise ValueError("LLM is not found in config. Cannot proceed with content splitting.")

    document_title = state.get("document_title", "Untitled Document")
    document_structure = state.get("document_structure", [])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTENT_SPLITTER_SYSTEM_PROMPT),
            ("human", CONTENT_SPLITTER_USER_PROMPT),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    def _process_node(node: Dict[str, Any], parent_headings: List[str]) -> None:
        current_heading = node.get("numbered_title", node.get("title", ""))

        if node.get("content") and len(node["content"]) > CONTENT_CHAR_LIMIT_FOR_SPLIT:
            llm_response_str = chain.invoke(
                {
                    "document_title": document_title,
                    "parent_headings": " -> ".join(parent_headings),
                    "current_heading": current_heading,
                    "content_to_split": node["content"],
                }
            )

            try:
                start_index = llm_response_str.find("[")
                if start_index == -1:
                    start_index = llm_response_str.find("{")

                end_index = llm_response_str.rfind("]")
                if end_index == -1:
                    end_index = llm_response_str.rfind("}")

                if start_index == -1 or end_index == -1:
                    raise ValueError("Could not find a JSON-like object in the response.")

                substring = llm_response_str[start_index : end_index + 1]
                split_data = json.loads(substring, strict=False)

                if isinstance(split_data, dict):
                    split_data = [split_data]

                if not isinstance(split_data, list):
                    raise ValueError("LLM response is not a JSON list or object.")

                new_children = _convert_llm_tree_to_nodes(split_data, node["level"])

                if not new_children:
                    raise ValueError("Failed to convert LLM response into valid nodes.")

                node["content"] = ""
                node["children"] = new_children + node.get("children", [])

            except (json.JSONDecodeError, ValueError) as error:
                print(
                    f"Failed to process LLM response for '{current_heading}'. Keeping original content. Error: {error}"
                )

        new_parent_headings = parent_headings + [current_heading]
        for child_node in node.get("children", []):
            _process_node(child_node, new_parent_headings)

    for root_node in document_structure:
        _process_node(root_node, [])

    state["document_structure"] = document_structure
    print(json.dumps(document_structure, indent=2, ensure_ascii=False))
    end_time = time.time()
    print(f"Content splitting took {end_time - start_time:.2f} seconds.")
    return state
