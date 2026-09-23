import asyncio

from backend.workflows.slidegen_workflow.nodes import pipelined_orchestrator as pipeline
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide


def test_generation_uses_final_refined_plans(monkeypatch):
    events = []
    chunks = [
        {"heading": "First", "position": ["1.1"]},
        {"heading": "Second", "position": ["1.2"]},
    ]
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
                "slide_plans": [
                    {"action": "CONTENT_TOOLS", "image_mode": "none"},
                    {"action": "CONTENT_TOOLS", "image_mode": "none"},
                ],
                "slide_final_contents": [
                    "First refined content",
                    "Second refined content",
                ],
            },
            {"configurable": {}},
        )
    )

    assert events == ["gen_start_0", "gen_start_1", "gen_end_0", "gen_end_1"]
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
