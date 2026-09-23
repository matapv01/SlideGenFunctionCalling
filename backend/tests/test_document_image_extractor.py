from __future__ import annotations

import zipfile

from backend.application.services.document_image_extractor import (
    DocumentImageExtractor,
)


def _write_docx_fixture(path) -> None:
    document_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
      xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <w:body>
        <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>History</w:t></w:r></w:p>
        <w:p>
          <w:r><w:t>Context for the document image</w:t></w:r>
          <w:r><a:blip r:embed="rIdImage1"/></w:r>
        </w:p>
      </w:body>
    </w:document>
    """
    document_rels = """<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rIdImage1" Target="media/image1.png"/>
    </Relationships>
    """
    header_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
      xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <w:p><w:r><a:blip r:embed="rIdHeaderImage"/></w:r></w:p>
    </w:hdr>
    """
    header_rels = """<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rIdHeaderImage" Target="media/image2.png"/>
    </Relationships>
    """
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("word/document.xml", document_xml)
        package.writestr("word/_rels/document.xml.rels", document_rels)
        package.writestr("word/header1.xml", header_xml)
        package.writestr("word/_rels/header1.xml.rels", header_rels)
        package.writestr("word/media/image1.png", b"image-one")
        package.writestr("word/media/image2.png", b"image-two")


def test_extracts_images_from_document_and_header_parts(tmp_path):
    source = tmp_path / "images.docx"
    _write_docx_fixture(source)

    images = DocumentImageExtractor().extract(
        docx_path=source,
        document_id="document-1",
        output_root=tmp_path / "assets",
    )

    assert len(images) == 2
    assert {item["source_part"] for item in images} == {
        "word/document.xml",
        "word/header1.xml",
    }
    document_image = next(
        item for item in images if item["source_part"] == "word/document.xml"
    )
    assert document_image["section_path"] == "History"
    assert (tmp_path / "assets" / "document-1_images").is_dir()
