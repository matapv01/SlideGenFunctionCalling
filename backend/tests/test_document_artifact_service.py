from backend.application.services.document_artifact_service import (
    DocumentArtifactService,
)


def test_embedded_images_are_rendered_as_relative_markdown_links(tmp_path):
    image_dir = tmp_path / "document-1_images"
    image_dir.mkdir()
    image_path = image_dir / "0000_diagram.png"
    image_path.write_bytes(b"image")

    artifact = DocumentArtifactService().build(
        title="Architecture",
        markdown="# Architecture\nThe system has three layers.",
        structure=[{"title": "Architecture", "content": "The system has three layers."}],
        markdown_root=tmp_path,
        assets=[
            {
                "image_id": "document-1:0",
                "source_path": str(image_path),
                "filename": "diagram.png",
                "anchor_text": "The system has three layers.",
                "alt_text": "System architecture",
                "paragraph_index": 2,
            }
        ],
        source_type="docx",
    )

    assert "![System architecture](./document-1_images/0000_diagram.png)" in artifact.markdown
    assert artifact.assets[0]["relative_path"] == "document-1_images/0000_diagram.png"
    assert any(block.kind == "image" for block in artifact.blocks)


def test_images_without_text_anchor_are_kept_in_document_order(tmp_path):
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    first = image_dir / "0000.png"
    second = image_dir / "0001.png"
    first.write_bytes(b"1")
    second.write_bytes(b"2")

    artifact = DocumentArtifactService().build(
        title="Document",
        markdown="# Document\nSome text.",
        structure=[],
        markdown_root=tmp_path,
        assets=[
            {"image_id": "1", "source_path": str(first), "ordinal": 0},
            {"image_id": "2", "source_path": str(second), "ordinal": 1},
        ],
    )

    assert artifact.markdown.index("0000.png") < artifact.markdown.index("0001.png")
