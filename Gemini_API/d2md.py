from docling.document_converter import DocumentConverter

# source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
source = "C:\\Users\\pvmkt\\OneDrive\\Desktop\\SlideGenSourceCode\\SlideGenFunctionCalling\\Document\\VẤN ĐỀ VỀ CHỦ QUYỀN BIỂN ĐẢO VIỆT NAM.docx"
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"
print("-" * 20)


from docling.document_converter import DocumentConverter

doc = result.document

from docling.chunking import HybridChunker

chunker = HybridChunker()
chunk_iter = chunker.chunk(dl_doc=doc)

for i, chunk in enumerate(chunk_iter):
    print(f"=== {i} ===")
    print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}") # noi dung goc

    enriched_text = chunker.contextualize(chunk=chunk)
    print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}") # Noi dung da duoc lam giau

    print()
