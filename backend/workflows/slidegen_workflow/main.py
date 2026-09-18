"""XML-only slide generation workflow entry points.

There is one renderer: ``run_canonical_slide_workflow``. DOCX, chatbot, and
the manual editor are responsible for preparing canonical chunks before they
reach this module. ``main_workflow`` remains as a thin compatibility adapter
for older callers that already have a preprocessed document state.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from backend.config import (
    ENABLE_SLIDE_PARALLELISM,
    SLIDE_MAX_CONCURRENCY,
    WORKFLOW_RECURSION_LIMIT,
)
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider
from backend.domain.canonical_chunks import normalize_canonical_chunks
from backend.workflows.slidegen_workflow.graph.builder import build_workflow
from backend.workflows.slidegen_workflow.graph.parallel_builder import (
    build_parallel_workflow,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT as XML_TOOLS_DICT,
)

logger = logging.getLogger(__name__)


def _setup_output_dirs(output_folder: str) -> Tuple[str, str]:
    """Create the directories expected by the XML renderer."""
    os.makedirs(output_folder, exist_ok=True)

    output_dir = os.path.join(output_folder, "output")
    output_debug_dir = os.path.join(output_folder, "output_debug")
    for base in (output_dir, output_debug_dir):
        os.makedirs(os.path.join(base, "xml"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "evaluation"), exist_ok=True)
    return output_dir, output_debug_dir


def _emit_event(
    callback: Optional[Callable[[str, Dict[Any, Any]], None]],
    event_type: str,
    data: Dict[Any, Any],
) -> None:
    """Emit workflow progress without allowing a UI callback to break a run."""
    if not callback:
        return
    try:
        callback(event_type, data)
    except Exception:
        logger.exception("Slide workflow callback failed")


def _log_slide_tool_summary(final_state: Dict[str, Any], workflow_label: str) -> None:
    """Log which XML tool rendered each completed slide."""
    final_slides = (final_state or {}).get("final_slides", [])

    print(f"\n========== {workflow_label}: SLIDE -> XML TOOL SUMMARY ==========")
    if not final_slides:
        print("No completed slides to summarize.")
        print("===============================================================\n")
        return

    rows = []
    tool_counts = Counter()
    for position, slide in enumerate(final_slides):
        tool_call = slide.get("tool_call") or {}
        tool_name = (
            tool_call.get("name") if isinstance(tool_call, dict) else None
        ) or "UNKNOWN_TOOL"
        slide_index = slide.get("index", position)
        try:
            display_index = int(slide_index) + 1
        except (TypeError, ValueError):
            display_index = position + 1
        rows.append((display_index, tool_name))
        tool_counts[tool_name] += 1

    for display_index, tool_name in sorted(rows, key=lambda row: row[0]):
        print(f"Slide {display_index:>3} -> {tool_name}")

    print("\nTool usage totals:")
    for tool_name, count in tool_counts.most_common():
        print(f"  {tool_name}: {count} slide(s)")
    print("===============================================================\n")
    logger.info("%s slide-tool summary: %s", workflow_label, dict(tool_counts))


def _prepare_slide_options(
    slide_options: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], str]:
    """Validate and normalize the renderer's XML-only options."""
    options = dict(slide_options or {})
    output_format = str(options.get("output_format", "xml")).lower()
    if output_format != "xml":
        raise ValueError("This workflow is XML-only; output_format must be 'xml'.")
    options["output_format"] = "xml"

    # A direct chatbot request has no legacy option payload, so it gets the
    # same deck-level defaults used by the chatbot and manual adapters.
    if not slide_options:
        options.update(
            {
                "enable_transition_slides": True,
                "enable_thank_you_slide": True,
            }
        )
    return options, output_format


def _build_graph_config(
    *,
    infra_providers: Dict[str, Any],
    output_folder: str,
    output_dir: str,
    output_debug_dir: str,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]],
    output_format: str,
    max_retries_per_slide: int,
) -> Dict[str, Any]:
    """Build the renderer graph config from already-created infrastructure."""
    llm_provider: LLMProvider = infra_providers["llm_provider"]
    planner_llm_provider: LLMProvider = infra_providers["planner_llm_provider"]
    capture_provider: CaptureProvider = infra_providers["capture_provider"]
    parser_provider: ParserProvider = infra_providers["parser_provider"]
    tool_retriever: ToolRetrieveProvider = infra_providers["tool_retriever"]

    return {
        "configurable": {
            "llm": llm_provider.llm_client,
            "planner_llm": planner_llm_provider.llm_client,
            "tool_retriever": tool_retriever,
            "capture_provider": capture_provider,
            "parser_provider": parser_provider,
            "tools_dict": XML_TOOLS_DICT,
            "output_format": output_format,
            "output_folder": output_folder,
            "max_retries": max_retries_per_slide,
            "temp_dir": output_dir,
            "temp_debug_dir": output_debug_dir,
            "stream_callback": lambda event_type, data: _emit_event(
                callback, event_type, data
            ),
            "parallel_progress_tracker": {
                "completed_indices": set(),
                "lock": threading.Lock(),
            },
            # LangGraph's max_concurrency does not reliably cap nested Send
            # workers, so keep an explicit gate around each slide worker.
            "slide_generation_semaphore": asyncio.Semaphore(
                max(1, int(SLIDE_MAX_CONCURRENCY))
            ),
            "image_relevance_verifier": infra_providers.get(
                "image_relevance_verifier"
            ),
            "llm_request_limiter": infra_providers.get("llm_request_limiter"),
        },
        "recursion_limit": WORKFLOW_RECURSION_LIMIT,
        "max_concurrency": SLIDE_MAX_CONCURRENCY,
    }


async def run_canonical_slide_workflow(
    *,
    slide_chunks: List[Any],
    title: str,
    output_folder: str,
    infra_providers: Dict[str, Any],
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, Any]] = None,
    slide_positions: Optional[List[Any]] = None,
    slide_context_maps: Optional[List[str]] = None,
    section_ids: Optional[List[str]] = None,
    max_retries_per_slide: int = 1,
) -> str:
    """Render canonical chunks through the only slide-generation graph."""
    normalized = normalize_canonical_chunks(
        slide_chunks,
        slide_positions=slide_positions,
        slide_context_maps=slide_context_maps,
        section_ids=section_ids,
    )
    canonical_chunks = normalized["slide_chunks"]
    if not canonical_chunks:
        raise ValueError("Canonical slide input is empty")

    output_dir, output_debug_dir = _setup_output_dirs(output_folder)
    _emit_event(
        callback,
        "status",
        {
            "step": 1,
            "title": "Starting",
            "description": "Initializing slide renderer...",
            "message": "Booting System",
        },
    )

    try:
        options, output_format = _prepare_slide_options(slide_options)
        workflow = (
            build_parallel_workflow()
            if ENABLE_SLIDE_PARALLELISM
            else build_workflow(router_flags=False)
        )
        app = workflow.compile()
        graph_config = _build_graph_config(
            infra_providers=infra_providers,
            output_folder=output_folder,
            output_dir=output_dir,
            output_debug_dir=output_debug_dir,
            callback=callback,
            output_format=output_format,
            max_retries_per_slide=max_retries_per_slide,
        )

        deck_title = str(title or "Untitled presentation").strip()
        initial_input = {
            "docx_file": None,
            "document_title": deck_title,
            "document_structure": [],
            "document_outline": [],
            "slide_chunks": canonical_chunks,
            "slide_positions": normalized["slide_positions"],
            "slide_context_maps": normalized["slide_context_maps"],
            "section_ids": normalized["section_ids"],
            "current_slide_index": -1,
            "retry_count": 0,
            "executor_retry_count": 0,
            "overflow_retry_count": 0,
            "max_retries": max_retries_per_slide,
            "final_slides": [],
            "batch_results": [],
            "all_debug_info": [],
            "vlm_decision": "accept",
            "slide_options": options,
            "output_format": output_format,
            "document_images": list(options.get("document_images") or []),
            "user_request": str(options.get("user_request") or ""),
        }

        print(
            "\n🚀 Starting canonical XML workflow "
            f"({len(canonical_chunks)} chunks)..."
        )
        _emit_event(
            callback,
            "status",
            {
                "step": 2,
                "title": "Creating Slides",
                "description": f"Generating {len(canonical_chunks)} slides...",
                "message": "Generating Slides",
            },
        )
        start_time = time.time()
        final_state = await app.ainvoke(initial_input, config=graph_config)

        if not final_state or not final_state.get("final_slides"):
            raise ValueError(
                "Không tạo được slide từ nội dung. "
                "Vui lòng kiểm tra nội dung hoặc thử lại."
            )

        _log_slide_tool_summary(final_state, "CANONICAL XML WORKFLOW")
        print(f"✅ Workflow completed in {time.time() - start_time:.2f}s")
        _emit_event(
            callback,
            "status",
            {
                "step": 3,
                "title": "Completed",
                "description": "Packaging...",
                "message": f'Created {len(final_state.get("final_slides", []))} slides',
            },
        )
        print(f"📦 Output saved to folder: {output_folder}")
        return output_folder
    except Exception:
        logger.exception("Canonical XML slide workflow failed")
        raise


async def main_workflow(
    router_flags: bool,
    docx_file: str,
    output_folder: str,
    doc_state: Dict[str, Any],
    infra_providers: Dict[str, Any],
    max_retries_per_slide: int = 1,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, Any]] = None,
) -> str:
    """Compatibility adapter for callers holding a preprocessed DOCX state."""
    del router_flags
    chunks = list((doc_state or {}).get("slide_chunks") or [])
    title = str(
        (doc_state or {}).get("document_title")
        or Path(docx_file or "presentation").stem
    )
    return await run_canonical_slide_workflow(
        slide_chunks=chunks,
        title=title,
        output_folder=output_folder,
        infra_providers=infra_providers,
        callback=callback,
        slide_options=slide_options,
        slide_positions=(doc_state or {}).get("slide_positions"),
        slide_context_maps=(doc_state or {}).get("slide_context_maps"),
        section_ids=(doc_state or {}).get("section_ids"),
        max_retries_per_slide=max_retries_per_slide,
    )
