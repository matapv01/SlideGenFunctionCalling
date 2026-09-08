from backend.workflows.idea_workflow.utils.section_metadata import (
    normalize_section_metadata,
)


def test_idea_without_transitions_is_distributed_into_sections():
    chunks = [
        {"slide_type": "intro", "title": "Intro"},
        *[
            {"slide_type": "content", "title": f"Content {index}"}
            for index in range(6)
        ],
        {"slide_type": "thank_you", "title": "Thanks"},
    ]

    normalized = normalize_section_metadata(chunks, estimated_sections=3)

    assert [chunk["section_id"] for chunk in normalized] == [
        "intro",
        "section_1",
        "section_1",
        "section_2",
        "section_2",
        "section_3",
        "section_3",
        "closing",
    ]


def test_transition_belongs_to_the_section_it_introduces():
    chunks = [
        {"slide_type": "intro"},
        {"slide_type": "content"},
        {"slide_type": "transition"},
        {"slide_type": "content"},
    ]

    normalized = normalize_section_metadata(chunks, estimated_sections=2)

    assert [chunk["section_id"] for chunk in normalized] == [
        "intro",
        "section_1",
        "section_2",
        "section_2",
    ]
