from backend.workflows.slidegen_workflow.utils.section_batches import (
    build_section_batches,
)


def test_groups_dfs_positions_by_top_level_section():
    state = {
        "slide_chunks": [{"heading": name} for name in ("INTRO", "A", "A.1", "B", "END")],
        "slide_positions": [["0"], ["1.T"], ["1.1"], ["2.1"], ["999"]],
        "slide_context_maps": ["intro", "a", "a1", "b", "end"],
        "slide_plans": [
            {"action": "INTRO_TOOLS"},
            {"action": "TRANSITION_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "THANK_YOU_TOOLS"},
        ],
    }

    jobs, batches = build_section_batches(state)

    assert [job["index"] for job in jobs] == [0, 1, 2, 3, 4]
    assert [batch["batch_id"] for batch in batches] == [
        "000_intro",
        "section_0001",
        "section_0002",
        "999_thank_you",
    ]
    assert [[job["index"] for job in batch["jobs"]] for batch in batches] == [
        [0],
        [1, 2],
        [3],
        [4],
    ]


def test_transition_starts_next_batch_when_positions_are_missing():
    state = {
        "slide_chunks": [
            {"slide_type": "intro"},
            {"heading": "First topic"},
            {"slide_type": "transition"},
            {"heading": "Second topic"},
        ],
        "slide_plans": [
            {"action": "INTRO_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "TRANSITION_TOOLS"},
            {"action": "CONTENT_TOOLS"},
        ],
    }

    _, batches = build_section_batches(state)

    assert [[job["index"] for job in batch["jobs"]] for batch in batches] == [
        [0],
        [1],
        [2, 3],
    ]


def test_first_transition_starts_section_one_when_positions_are_missing():
    state = {
        "slide_chunks": [
            {"slide_type": "intro"},
            {"slide_type": "transition"},
            {"heading": "First topic"},
        ],
        "slide_plans": [
            {"action": "INTRO_TOOLS"},
            {"action": "TRANSITION_TOOLS"},
            {"action": "CONTENT_TOOLS"},
        ],
    }

    _, batches = build_section_batches(state)

    assert [[job["index"] for job in batch["jobs"]] for batch in batches] == [
        [0],
        [1, 2],
    ]


def test_explicit_section_ids_work_without_dfs_positions_or_transitions():
    state = {
        "slide_chunks": [
            {"slide_type": "intro", "section_id": "intro"},
            {"heading": "A", "section_id": "section_1"},
            {"heading": "B", "section_id": "section_1"},
            {"heading": "C", "section_id": "section_2"},
        ],
        "slide_plans": [
            {"action": "INTRO_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "CONTENT_TOOLS"},
            {"action": "CONTENT_TOOLS"},
        ],
    }

    _, batches = build_section_batches(state)

    assert [[job["index"] for job in batch["jobs"]] for batch in batches] == [
        [0],
        [1, 2],
        [3],
    ]


def test_flat_legacy_chunks_use_bounded_fallback_batches():
    state = {
        "slide_chunks": [{"heading": f"Slide {index}"} for index in range(7)],
        "slide_plans": [{"action": "CONTENT_TOOLS"} for _ in range(7)],
    }

    _, batches = build_section_batches(state)

    assert [[job["index"] for job in batch["jobs"]] for batch in batches] == [
        [0, 1, 2],
        [3, 4, 5],
        [6],
    ]
