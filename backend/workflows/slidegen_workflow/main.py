# File: backend/workflows/slidegen_workflow/main.py

import zipfile
import os
import time
import logging
from typing import Optional, Callable, Dict, Any, Tuple, List
from backend.workflows.slidegen_workflow.graph.builder import build_workflow
from backend.workflows.manual_workflow.main import run_manual_workflow
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider

logger = logging.getLogger(__name__)


# HELPER FUNCTIONS
def _setup_output_dirs(output_folder: str) -> Tuple[str, str]:
    """Creates necessary directories for output."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    output_dir = os.path.join(output_folder, "output")
    output_debug_dir = os.path.join(output_folder, "output_debug")
    
    for base in [output_dir, output_debug_dir]:
        os.makedirs(os.path.join(base, "html"), exist_ok=True)
        os.makedirs(os.path.join(base, "png"), exist_ok=True)
        
    return output_dir, output_debug_dir

def _emit_event(callback, event_type: str, data: Dict[Any, Any]):
    """Safe event emission."""
    if callback:
        try:
            callback(event_type, data)
        except Exception as e:
            logger.error(f"Error in callback: {e}")

def _extract_images_with_positions(docx_path: str, images_dir: str) -> List[dict]:
    """
    Use python-docx to extract ALL images from a DOCX, saving each to images_dir.

    Returns a list (in document order) of:
        {
            'filename':    'image_001.png',
            'rel_path':    'images/image_001.png',
            'para_idx':    N,
            'text_before': '...',   # nearest non-empty paragraph before image
            'text_after':  '...',   # nearest non-empty paragraph after image
        }
    """
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        logger.warning("python-docx not available; image extraction skipped")
        return []

    os.makedirs(images_dir, exist_ok=True)

    doc = Document(docx_path)
    paragraphs = doc.paragraphs
    results: List[dict] = []
    counter = 0

    MIME_TO_EXT = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
        "image/tiff": ".tif",
    }

    for para_idx, para in enumerate(paragraphs):
        drawings = para._element.findall(".//" + qn("w:drawing"))
        if not drawings:
            continue

        for drawing in drawings:
            for blip in drawing.findall(".//" + qn("a:blip")):
                rId = blip.get(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
                )
                if not rId:
                    continue
                try:
                    image_part = doc.part.related_parts[rId]
                    ext = MIME_TO_EXT.get(image_part.content_type, ".png")

                    counter += 1
                    filename = f"image_{counter:03d}{ext}"
                    dest = os.path.join(images_dir, filename)

                    with open(dest, "wb") as f:
                        f.write(image_part.blob)

                    # Surrounding text context (for images_map.json)
                    text_before = ""
                    for i in range(para_idx - 1, -1, -1):
                        t = paragraphs[i].text.strip()
                        if t:
                            text_before = t
                            break

                    text_after = ""
                    for j in range(para_idx + 1, len(paragraphs)):
                        t = paragraphs[j].text.strip()
                        if t:
                            text_after = t
                            break

                    results.append({
                        "filename": filename,
                        "rel_path": f"images/{filename}",
                        "para_idx": para_idx,
                        "text_before": text_before,
                        "text_after": text_after,
                    })
                    logger.info(f"Extracted image: {filename} (para {para_idx})")
                except Exception as e:
                    logger.warning(f"Could not extract image rId={rId}: {e}")

    return results


def _replace_base64_with_local_paths(
    markdown_content: str,
    image_infos: List[dict],
    images_dir: str,
) -> str:
    """
    Replace `![alt](data:...)` markers in MarkItDown markdown with local image paths.

    MarkItDown can emit either:
      - a full inline base64:  ![](data:image/png;base64,iVBORw0K...)
      - a truncated placeholder: ![](data:image/png;base64...)

    Both patterns share the `data:` prefix and are enclosed in `(...)`.
    We match ALL of them with a broad `data:[^)]+` pattern and map the
    Nth occurrence → Nth image extracted by python-docx (same paragraph order).
    """
    import re

    # Broad pattern: matches any Markdown image whose URL starts with "data:"
    DATA_URI_PATTERN = re.compile(
        r'!\[(?P<alt>[^\]]*)\]\(data:[^)]+\)',
        re.DOTALL,
    )

    matches = DATA_URI_PATTERN.findall(markdown_content)  # for count logging
    n_b64 = len(matches)
    n_img = len(image_infos)
    logger.info(f"Found {n_b64} data: URI(s) in markdown, {n_img} image(s) from python-docx")

    if n_b64 == 0:
        # Nothing to replace
        return markdown_content

    nth = [0]

    def _replace(match: re.Match) -> str:
        idx = nth[0]
        nth[0] += 1

        alt = match.group("alt") or ""

        if idx < n_img:
            rel_path = image_infos[idx]["rel_path"]
            logger.info(f"Replacing data: URI #{idx + 1} → {rel_path}")
            return f"![{alt}]({rel_path})"

        # More placeholders in markdown than extracted images — strip marker
        logger.warning(f"No image_info for data: URI #{idx + 1}; removing placeholder")
        return ""

    return DATA_URI_PATTERN.sub(_replace, markdown_content)


def _save_markdown_source(output_folder: str, markdown_content: str, docx_path: str = ""):
    """Save source.md with base64 blobs replaced by local image paths.

    Strategy:
    - python-docx extracts images in document order → image_001.png, image_002.png, ...
    - MarkItDown markdown has ![](data:image/...;base64,...) in the same order
    - Replace Nth base64 → images/image_NNN.ext  (in-place, no new lines added)
    - Missed images (python-docx found but MarkItDown skipped) go to images_map.json only
    - source.md structure (headings, paragraphs) is never touched
    """
    import json as _json

    try:
        md_dir = os.path.join(output_folder, "markdown")
        images_dir = os.path.join(md_dir, "images")
        os.makedirs(md_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        image_infos: List[dict] = []

        if docx_path and os.path.exists(docx_path):
            # Extract all images via python-docx (ground truth)
            image_infos = _extract_images_with_positions(docx_path, images_dir)

        # Replace base64 URIs in-place with local paths
        processed = _replace_base64_with_local_paths(
            markdown_content, image_infos, images_dir
        )

        with open(os.path.join(md_dir, "source.md"), "w", encoding="utf-8") as f:
            f.write(processed)
        logger.info(f"Saved source.md → {md_dir}")

        # Write image catalog (position context for downstream use)
        if image_infos:
            map_path = os.path.join(md_dir, "images_map.json")
            with open(map_path, "w", encoding="utf-8") as f:
                _json.dump(image_infos, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved images_map.json ({len(image_infos)} image(s))")

    except Exception as e:
        logger.error(f"Error saving markdown source: {e}")


def _generate_markdown_from_chunks(title: str, slide_chunks: list) -> str:
    """Generate markdown text from a list of slide chunks (Idea/Manual mode)."""
    lines = []
    if title:
        lines.append(f"# {title}")

    for idx, chunk in enumerate(slide_chunks):
        title_text = chunk.get("title") or chunk.get("heading")
        content_text = chunk.get("content") or chunk.get("description")

        if title_text:
            lines.append(f"## {title_text}")
        if content_text:
            lines.append(str(content_text))

        if not title_text and not content_text:
            lines.append(f"## Slide {idx + 1}")

    return "\n\n".join(lines)


# ==============================================================================
# MAIN WORKFLOWS
# ==============================================================================

async def main_workflow(
    router_flags: bool,
    docx_file: str,
    output_folder: str,
    doc_state: Dict[str, Any],
    infra_providers: Dict[str, Any], # 🟢 NHẬN TỪ WORKFLOW SERVICE
    max_retries_per_slide: int = 1,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None
):
    output_dir, output_debug_dir = _setup_output_dirs(output_folder)
    _emit_event(callback, 'status', {'step': 1, 'title': 'Starting', 'message': 'System ready'})

    try:
        # 1. 🟢 LẤY CÁC INSTANCE ĐÃ CÓ SẴN (KHÔNG KHỞI TẠO MỚI)
        llm_provider: LLMProvider = infra_providers['llm_provider']
        capture_provider: CaptureProvider = infra_providers['capture_provider']
        parser_provider: ParserProvider = infra_providers['parser_provider']
        tool_retriever: ToolRetrieveProvider = infra_providers['tool_retriever']
        conversion_service = infra_providers.get('conversion_service')

        # Vì node slide_generator cần LangChain Runnable, ta lấy từ client
        langchain_llm = llm_provider.llm_client 

        # 2. Setup Graph
        workflow = build_workflow(router_flags)
        app = workflow.compile()

        # 3. Graph Config (Inject công cụ vào các Node)
        graph_config = {
            "configurable": {
                "llm": langchain_llm,
                "tool_retriever": tool_retriever,
                "capture_provider": capture_provider,
                "parser_provider": parser_provider,
                "tools_dict": TOOLS_DICT,
                "conversion_service": conversion_service,
                "output_folder": output_folder,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": lambda t, d: _emit_event(callback, t, d),
            },
            "recursion_limit": 500
        }

        _slide_options = slide_options or {}

        # 4. Feed preprocessed doc state into planning/generation workflow
        if not doc_state or not doc_state.get("slide_chunks"):
            raise ValueError("Preprocessed document state has no slide chunks")

        initial_input = {
            "docx_file": docx_file,
            "workflow_mode": _slide_options.get("workflow_mode", "auto_no_heading"),
            "document_title": doc_state.get("document_title"),
            "document_structure": doc_state.get("document_structure", []),
            "document_outline": doc_state.get("document_outline", []),
            "slide_chunks": doc_state.get("slide_chunks", []),
            "slide_positions": doc_state.get("slide_positions", []),
            "slide_context_maps": doc_state.get("slide_context_maps", []),
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "vlm_decision": "accept",
            "slide_options": _slide_options
        }

        # --- Save markdown + extract images (python-docx ground truth) ---
        plain_text = doc_state.get("plain_text", "")

        # 1. Extract images from DOCX → save to markdown/images/
        #    Returns image_infos with rel_paths (e.g. "images/image_001.png")
        md_dir = os.path.join(output_folder, "markdown")
        images_dir = os.path.join(md_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        image_infos: List[dict] = []
        print(f"\n🖼️  [IMAGE] docx_file={docx_file!r}, exists={os.path.exists(docx_file) if docx_file else False}")
        if docx_file and os.path.exists(docx_file):
            image_infos = _extract_images_with_positions(docx_file, images_dir)
            print(f"🖼️  [IMAGE] python-docx found {len(image_infos)} image(s)")
            if image_infos:
                import json as _json
                with open(os.path.join(md_dir, "images_map.json"), "w", encoding="utf-8") as _f:
                    _json.dump(image_infos, _f, indent=2, ensure_ascii=False)
                logger.info(f"Extracted {len(image_infos)} image(s) + saved images_map.json")

        # 2. Replace data: URIs → local paths in plain_text & save source.md
        if plain_text:
            import re as _re2
            _n_uri = len(_re2.findall(r'!\[[^\]]*\]\(data:[^)]+\)', plain_text, _re2.DOTALL))
            print(f"🖼️  [IMAGE] plain_text has {_n_uri} data: URI(s), will replace with {len(image_infos)} local paths")
            processed_text = _replace_base64_with_local_paths(plain_text, image_infos, images_dir)
            with open(os.path.join(md_dir, "source.md"), "w", encoding="utf-8") as _f:
                _f.write(processed_text)
            print(f"🖼️  [IMAGE] source.md saved → {os.path.join(md_dir, 'source.md')}")
        else:
            md_text = _generate_markdown_from_chunks(
                doc_state.get("document_title", "Untitled"),
                initial_input["slide_chunks"]
            )
            processed_text = md_text
            with open(os.path.join(md_dir, "source.md"), "w", encoding="utf-8") as _f:
                _f.write(md_text)

        # 3. Update slide_chunks content: replace data: URIs with FULL STATIC URLs
        #    e.g. /static/output/{doc_name}/markdown/images/image_001.png
        if image_infos:
            import re as _re
            DATA_URI_RE = _re.compile(r'!\[([^\]]*)\]\(data:[^)]+\)', _re.DOTALL)

            # Build the URL-accessible base for images
            _STATIC_ROOT = "/app/static"
            if output_folder.replace("\\", "/").startswith(_STATIC_ROOT):
                _url_base = "/static" + output_folder.replace("\\", "/")[len(_STATIC_ROOT):]
            else:
                # fallback: try to extract /static/ portion
                _folder_norm = output_folder.replace("\\", "/")
                _idx = _folder_norm.find("/static/")
                _url_base = _folder_norm[_idx:] if _idx >= 0 else _folder_norm
            images_url_base = f"{_url_base}/markdown/images"
            print(f"🖼️  [IMAGE] images_url_base = {images_url_base}")

            def _patch_chunks(chunks: list, img_infos: list) -> list:
                nth = [0]
                def _repl(m: _re.Match) -> str:
                    idx = nth[0]; nth[0] += 1
                    if idx < len(img_infos):
                        # Use full static URL so browser can resolve the image
                        img_name = img_infos[idx]['rel_path'].split('/')[-1]
                        full_url = f"{images_url_base}/{img_name}"
                        return f"![{m.group(1)}]({full_url})"
                    return ""

                patched = []
                for chunk in chunks:
                    c = dict(chunk)
                    # Patch ALL text fields that may contain image references
                    for field in ("text_content", "content", "description"):
                        if c.get(field):
                            c[field] = DATA_URI_RE.sub(_repl, str(c[field]))
                    patched.append(c)
                return patched

            patched_chunks = _patch_chunks(initial_input["slide_chunks"], image_infos)
            initial_input["slide_chunks"] = patched_chunks

            # --- LOG: Print full content of patched chunks ---
            TEXT_FIELDS = ("text_content", "content", "description")
            IMG_URL_MARKER = images_url_base.split("/")[-3] if "/" in images_url_base else "images"
            print("\n" + "="*60)
            print(f"🖼️  [PATCHED SLIDE CHUNKS] {len(patched_chunks)} total chunks")
            print("="*60)
            for i, c in enumerate(patched_chunks):
                label  = c.get("heading") or c.get("title") or f"chunk[{i}]"
                text = next((str(c.get(f, "")) for f in TEXT_FIELDS if c.get(f)), "(empty)")
                has_img = any("/static/" in str(c.get(f, "")) for f in TEXT_FIELDS)
                marker = "🖼️ " if has_img else "   "
                print(f"\n{marker}--- Chunk [{i}] '{label}' ---")
                print(text)
            print("="*60 + "\n")

            # Save full slide_chunks to markdown/slide_chunks_debug.json
            import json as _json2
            debug_path = os.path.join(md_dir, "slide_chunks_debug.json")
            with open(debug_path, "w", encoding="utf-8") as _f2:
                _json2.dump(patched_chunks, _f2, indent=2, ensure_ascii=False)
            print(f"📄 [IMAGE] slide_chunks_debug.json → {debug_path}")

        # Run planning and generation workflow
        print("\n🚀 Running Workflow with Singleton Infrastructure...")
        final_state = await app.ainvoke(initial_input, config=graph_config)
        print("\n🚀 Workflow completed.")
        return output_folder

    except Exception as e:
        logger.error(f"❌ Workflow Error: {e}")
        return None


async def main_workflow_from_chunks(
    slide_chunks: list,
    title: str,
    output_folder: str,
    infra_providers: Dict[str, Any], # 🟢 NHẬN TỪ WORKFLOW SERVICE
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None
):
    """
    Idea Workflow: Chunks -> Slides
    Bypasses Parser, uses same Infrastructure for everything else.
    """
    output_dir, output_debug_dir = _setup_output_dirs(output_folder)
    
    _emit_event(callback, 'status', {
        'step': 1, 'title': 'Starting', 'description': 'Initializing Infrastructure...', 'message': 'Booting System'
    })

    try:
        # --- INFRASTRUCTURE INITIALIZATION ---
        llm_provider: LLMProvider = infra_providers['llm_provider']
        capture_provider: CaptureProvider = infra_providers['capture_provider']
        parser_provider: ParserProvider = infra_providers['parser_provider']
        tool_retriever: ToolRetrieveProvider = infra_providers['tool_retriever']
        conversion_service = infra_providers.get('conversion_service')
        langchain_llm = llm_provider.llm_client

        # Router flag is False because we don't need to route document conversion
        workflow = build_workflow(router_flags=False) 
        app = workflow.compile()

        if slide_options is None:
            slide_options = {"enable_transition_slides": True, "enable_thank_you_slide": True}

        # --- CONFIG & INPUT ---
        graph_config = {
            "configurable": {
                "llm": langchain_llm,
                "tool_retriever": tool_retriever,
                "capture_provider": capture_provider,
                "parser_provider": parser_provider,
                "tools_dict": TOOLS_DICT,
                "conversion_service": conversion_service,
                "output_folder": output_folder,
                "max_retries": 1,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": lambda t, d: _emit_event(callback, t, d),
            },
            "recursion_limit": 500
        }

        initial_input = {
            "docx_file": None,
            "document_structure": {"title": title},
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "vlm_decision": "accept",
            "slide_options": slide_options
        }

        # Run standalone manual workflow first to normalize chunks/context maps.
        manual_state = await run_manual_workflow(
            slide_chunks=slide_chunks,
            title=title,
            slide_options=slide_options,
            graph_config=graph_config,
        )

        initial_input["slide_chunks"] = manual_state.get("slide_chunks", slide_chunks)
        initial_input["slide_context_maps"] = manual_state.get("slide_context_maps", [])
        initial_input["document_structure"] = manual_state.get("document_structure", {"title": title})

        # Save markdown representation
        md_text = _generate_markdown_from_chunks(
            initial_input["document_structure"].get("title", title), 
            initial_input["slide_chunks"]
        )
        _save_markdown_source(output_folder, md_text)

        # --- EXECUTION ---
        print(f"\n🚀 Starting Workflow (Idea Mode - {len(slide_chunks)} chunks)...")
        start_time = time.time()

        _emit_event(callback, 'status', {
            'step': 2, 'title': 'Creating Slides', 'description': f'Generating {len(slide_chunks)} slides...', 'message': 'Generating Slides'
        })

        final_state = await app.ainvoke(initial_input, config=graph_config)

        print(f"✅ Workflow completed in {time.time() - start_time:.2f}s")

        # --- FINALIZE ---
        if not final_state or not final_state.get('final_slides'):
            _emit_event(callback, 'error', {'message': 'No slides were created'})
            return None

        _emit_event(callback, 'status', {
            'step': 3, 'title': 'Completed', 'description': 'Packaging...', 
            'message': f'Created {len(final_state.get("final_slides", []))} slides'
        })

        print(f"📦 Output saved to folder: {output_folder}")
        return output_folder

    except Exception as e:
        print(f"❌ Workflow Failed: {e}")
        import traceback; traceback.print_exc()
        return None