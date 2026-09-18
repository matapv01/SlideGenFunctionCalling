import json
import time
from typing import Any, Dict, List, Optional

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
    Complete the mixed-document pass.

    Explicit heading nodes are treated as already structured and are kept in
    place. Only an unstructured preamble or an oversized leaf body is sent to
    the LLM. The generated nodes are merged back into the existing tree, so a
    document containing both kinds of content does not get auto-structured a
    second time from the beginning.
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

    # The no-heading branch has already organized the entire document in
    # auto_structure. It is a completed tree, not an oversized heading leaf.
    if state.get("document_structure_origin") in {"llm", "fallback"}:
        state["document_preamble"] = ""
        print("Skipping mixed split: whole document already has a canonical structure")
        return state

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTENT_SPLITTER_SYSTEM_PROMPT),
            ("human", CONTENT_SPLITTER_USER_PROMPT),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    protected_node_ids: set[int] = set()

    def _protect_tree(nodes: List[Dict[str, Any]]) -> None:
        """Prevent a freshly inferred region from being sent to the LLM again."""
        for item in nodes:
            protected_node_ids.add(id(item))
            _protect_tree(item.get("children", []))

    def _parse_llm_nodes(
        llm_response_str: str,
        *,
        parent_level: int,
        region_label: str,
    ) -> Optional[List[Dict[str, Any]]]:
        try:
            start_index = llm_response_str.find("[")
            if start_index == -1:
                start_index = llm_response_str.find("{")

            end_index = llm_response_str.rfind("]")
            if end_index == -1:
                end_index = llm_response_str.rfind("}")

            if start_index == -1 or end_index == -1:
                raise ValueError("Could not find a JSON-like object in the response.")

            split_data = json.loads(
                llm_response_str[start_index : end_index + 1], strict=False
            )
            if isinstance(split_data, dict):
                split_data = [split_data]
            if not isinstance(split_data, list):
                raise ValueError("LLM response is not a JSON list or object.")

            new_nodes = _convert_llm_tree_to_nodes(split_data, parent_level)
            if not new_nodes:
                raise ValueError("Failed to convert LLM response into valid nodes.")
            return new_nodes
        except (json.JSONDecodeError, ValueError) as error:
            print(
                f"Failed to process LLM response for '{region_label}'. "
                f"Keeping original content. Error: {error}"
            )
            return None

    def _infer_region(
        content_to_split: str,
        *,
        parent_level: int,
        parent_headings: List[str],
        current_heading: str,
    ) -> Optional[List[Dict[str, Any]]]:
        response = chain.invoke(
            {
                "document_title": document_title,
                "parent_headings": " -> ".join(parent_headings),
                "current_heading": current_heading,
                "content_to_split": content_to_split,
            }
        )
        return _parse_llm_nodes(
            response,
            parent_level=parent_level,
            region_label=current_heading,
        )

    def _process_node(node: Dict[str, Any], parent_headings: List[str]) -> None:
        if id(node) in protected_node_ids:
            return

        current_heading = node.get("numbered_title", node.get("title", ""))

        # A node with explicit children already has an internal structure.
        # Keep its body exactly as authored and recurse only into descendants.
        if (
            node.get("content")
            and not node.get("children")
            and len(node["content"]) > CONTENT_CHAR_LIMIT_FOR_SPLIT
        ):
            new_children = _infer_region(
                node["content"],
                parent_level=int(node.get("level") or 1),
                parent_headings=parent_headings,
                current_heading=current_heading,
            )
            if new_children:
                _protect_tree(new_children)
                node["content"] = ""
                node["children"] = new_children

        new_parent_headings = parent_headings + [current_heading]
        for child_node in node.get("children", []):
            _process_node(child_node, new_parent_headings)

    # The preamble is the only unstructured region outside explicit heading
    # nodes. Infer headings for it and prepend the result. A preamble that is
    # exactly the document title is metadata only and does not need a call.
    preamble = str(state.get("document_preamble") or "").strip()
    # When the whole document had no headings, auto_structure has already
    # handled the only unstructured region. Running the mixed pass again here
    # would duplicate the LLM call and could duplicate content.
    has_explicit_headings = state.get("document_structure_origin") == "headings"
    if preamble and has_explicit_headings:
        if preamble == str(document_title).strip():
            state["document_preamble"] = ""
        else:
            inferred_preamble = _infer_region(
                preamble,
                parent_level=0,
                parent_headings=[],
                current_heading="Document introduction",
            )
            if inferred_preamble:
                _protect_tree(inferred_preamble)
                document_structure = inferred_preamble + document_structure
                state["document_preamble"] = ""
                state["document_structure_origin"] = "mixed"
            else:
                # Never lose an unstructured region when the LLM response is
                # invalid. Preserve it as a canonical introduction node.
                fallback_node = {
                    "level": 1,
                    "title": "Introduction",
                    "content": preamble,
                    "children": [],
                }
                protected_node_ids.add(id(fallback_node))
                document_structure = [fallback_node] + document_structure
                state["document_preamble"] = ""
                state["document_structure_origin"] = "mixed"

    for root_node in document_structure:
        _process_node(root_node, [])

    state["document_structure"] = document_structure
    print(json.dumps(document_structure, indent=2, ensure_ascii=False))
    end_time = time.time()
    print(f"Content splitting took {end_time - start_time:.2f} seconds.")
    return state
