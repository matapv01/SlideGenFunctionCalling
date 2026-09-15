import asyncio
import time

from backend.workflows.slidegen_workflow.nodes import pipelined_orchestrator as pipeline
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide


class _FakePlanner:
    def __init__(self, events):
        self.events = events

    def batch(self, inputs, config=None):
        index = inputs[0]["slide_number"] - 1
        self.events.append(f"plan_start_{index}")
        time.sleep(0.02)
        self.events.append(f"plan_end_{index}")
        return [
            {
                "slide_topic": f"Topic {index}",
                "thought": "Use a concise readable layout.",
                "image_mode": "none",
                "image_strategy": "decorative",
                "image_theme": "",
                "action": "CONTENT_TOOLS",
            }
        ]


def test_planner_next_batch_overlaps_generation(monkeypatch):
    events = []
    chunks = [
        {"heading": "First", "position": ["1.1"]},
        {"heading": "Second", "position": ["1.2"]},
    ]
    fake_planner = _FakePlanner(events)

    monkeypatch.setattr(pipeline, "PLANNING_BATCH_SIZE", 1)
    monkeypatch.setattr(
        pipeline,
        "prepare_planner_context",
        lambda state, config: {
            "slide_chunks": chunks,
            "slide_context_maps": ["first", "second"],
            "slide_positions": [["1.1"], ["1.2"]],
            "section_ids": [],
            "all_inputs": [
                {"slide_number": 1},
                {"slide_number": 2},
            ],
            "planner_chain": fake_planner,
            "stream_callback": None,
        },
    )
    monkeypatch.setattr(
        pipeline,
        "assign_layouts",
        lambda state, config: {
            "slide_jobs": state["slide_jobs"],
            "layout_assignment_report": {},
        },
    )

    async def fake_invoke_jobs(jobs, state, config):
        index = jobs[0]["index"]
        events.append(f"gen_start_{index}")
        await asyncio.sleep(0.04)
        events.append(f"gen_end_{index}")
        return {"final_slides": [{"index": index}]}

    monkeypatch.setattr(pipeline, "_invoke_jobs", fake_invoke_jobs)

    result = asyncio.run(
        pipeline.plan_and_generate_pipeline(
            {
                "slide_chunks": chunks,
                "slide_context_maps": ["first", "second"],
                "slide_positions": [["1.1"], ["1.2"]],
            },
            {"configurable": {}},
        )
    )

    assert events.index("gen_start_0") < events.index("plan_end_1")
    assert [slide["index"] for slide in result["final_slides"]] == [0, 1]


def test_streaming_progress_omits_unknown_total():
    events = []
    tracker = {
        "completed_indices": set(),
        "total_known": False,
    }

    finalize_slide(
        {
            "current_slide_index": 0,
            "current_tool_call": {"name": "layout_a"},
            "current_slide_text": {"title": "First"},
            "current_transitions": [],
            "final_slides": [],
            "current_xml_path": "/tmp/slide.xml",
        },
        {
            "configurable": {
                "parallel_progress_tracker": tracker,
                "stream_callback": lambda event_type, data: events.append(
                    (event_type, data)
                ),
            }
        },
    )

    progress = next(data for event, data in events if event == "progress")
    completed = next(
        data for event, data in events if event == "slide_completed"
    )
    assert progress["message"] == "Completed 1 slides"
    assert "total" not in progress
    assert "total" not in completed
