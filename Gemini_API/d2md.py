from docling.document_converter import DocumentConverter

# source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
# source = ".\\SlideGenFunctionCalling\\Document\\test_ttcs - heading.docx"
source = ".\\SlideGenFunctionCalling\\Document\\SlideGen.pdf"

converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"
print("-" * 20)


from docling.document_converter import DocumentConverter

doc = result.document

from docling.chunking import HierarchicalChunker 

chunker = HierarchicalChunker()
chunk_iter = chunker.chunk(dl_doc=doc)
print(doc)

for i, chunk in enumerate(chunk_iter):
    print(f"=== {i} ===")
    print(f"chunk.text:\n{f'{chunk.text}…'!r}") # noi dung goc

    enriched_text = chunker.contextualize(chunk=chunk)
    print(f"chunker.contextualize(chunk):\n{f'{enriched_text}…'!r}") # Noi dung da duoc lam giau

    print()
