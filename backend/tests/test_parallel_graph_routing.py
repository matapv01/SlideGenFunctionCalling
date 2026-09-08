import asyncio

from langgraph.graph import END, StateGraph

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.graph.parallel_builder import (
    build_parallel_workflow,
)
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
    dispatch_section_batches,
    merge_batch_results,
    prepare_section_batches,
)


class _Tool:
    def __init__(self, name):
        self.name = name


class _Retriever:
    def __init__(self, tools):
        self.tools = tools

    def get_relevant_tools(self, **_kwargs):
        return self.tools


async def _fake_section_worker(state):
    batch = state["section_batch"]
    slides = [{"index": job["index"]} for job in batch["jobs"]]
    return {
        "batch_results": [
            {"order": batch["order"], "slides": slides}
        ]
    }


def test_send_fan_out_merges_batches_back_in_slide_order():
    graph = StateGraph(State)
    graph.add_node("prepare", prepare_section_batches)
    graph.add_node("run_section_batch", _fake_section_worker)
    graph.add_node("merge_batch_results", merge_batch_results)
    graph.set_entry_point("prepare")
    graph.add_conditional_edges("prepare", dispatch_section_batches)
    graph.add_edge("run_section_batch", "merge_batch_results")
    graph.add_edge("merge_batch_results", END)

    state = {
        "slide_chunks": [
            {"heading": "INTRO"},
            {"heading": "Section one"},
            {"heading": "Section two"},
        ],
        "slide_positions": [["0"], ["1.1"], ["2.1"]],
        "slide_context_maps": ["intro", "one", "two"],
        "slide_plans": [
            {"action": "INTRO_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "CONTENT_TOOLS"},
        ],
        "batch_results": [],
    }

    result = asyncio.run(
        graph.compile().ainvoke(state, config={"max_concurrency": 3})
    )

    assert [slide["index"] for slide in result["final_slides"]] == [0, 1, 2]


def test_layouts_are_assigned_globally_before_fan_out():
    tools = [_Tool("layout_a"), _Tool("layout_b")]
    jobs = [
        {
            "index": index,
            "section_id": "section_1",
            "batch_id": "section_0001",
            "plan": {"action": "CONTENT_TOOLS", "thought": "content"},
        }
        for index in range(3)
    ]

    result = assign_layouts(
        {"slide_jobs": jobs},
        {
            "configurable": {
                "tools_dict": {"CONTENT_TOOLS": tools},
                "tool_retriever": _Retriever(tools),
            }
        },
    )

    assert [job["preferred_tool_name"] for job in result["slide_jobs"]] == [
        "layout_a",
        "layout_b",
        "layout_a",
    ]


def test_parallel_graph_has_no_final_duplicate_repair_node():
    graph = build_parallel_workflow()

    assert "assign_layouts" in graph.nodes
    assert "repair_cross_batch_duplicates" not in graph.nodes
