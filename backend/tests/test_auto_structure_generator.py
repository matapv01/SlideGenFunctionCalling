from backend.workflows.doc_workflow.nodes.auto_structure_generator import (
    _fallback_structure,
    _materialise_outline,
    _normalise_outline,
    _parse_json_response,
    _split_source_blocks,
)


def test_source_blocks_are_ordered_and_preserve_long_text():
    blocks = _split_source_blocks(
        "First paragraph.\n\nSecond paragraph.\n\n" + ("long text " * 300),
        max_chars=256,
    )

    assert [block["id"] for block in blocks] == [
        f"p{index:04d}" for index in range(1, len(blocks) + 1)
    ]
    assert "First paragraph." in blocks[0]["text"]
    assert "long text" in " ".join(block["text"] for block in blocks)


def test_json_parser_accepts_a_markdown_wrapped_outline():
    payload = _parse_json_response(
        "```json\n"
        '[{"title":"Overview","block_ids":["p0001"],"children":[]}]'
        "\n```"
    )

    assert payload[0]["title"] == "Overview"


def test_materialisation_keeps_unassigned_blocks_without_duplicate_content():
    blocks = [
        {"id": "p0001", "text": "Intro"},
        {"id": "p0002", "text": "Methods"},
        {"id": "p0003", "text": "Conclusion"},
    ]
    outline, assigned = _normalise_outline(
        [
            {
                "title": "Overview",
                "block_ids": ["p0001", "p0001", "unknown"],
                "children": [
                    {"title": "Methods", "block_ids": ["p0002"], "children": []}
                ],
            }
        ],
        {block["id"] for block in blocks},
    )

    structure = _materialise_outline(outline, blocks, assigned)
    content = "\n".join(
        [
            structure[0]["content"],
            structure[0]["children"][0]["content"],
            structure[1]["content"],
        ]
    )

    assert content.count("Intro") == 1
    assert content.count("Methods") == 1
    assert content.count("Conclusion") == 1
    assert structure[1]["title"] == "Additional content"


def test_fallback_structure_keeps_the_canonical_document_text():
    structure = _fallback_structure("Notes", "The original document text")

    assert structure == [
        {
            "level": 1,
            "title": "Notes",
            "content": "The original document text",
            "children": [],
        }
    ]
