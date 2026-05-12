import json
import logging
import os
import re
import shutil
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.runnables import RunnableConfig

from backend.workflows.doc_workflow.nodes.document_converter import parse_markdown_to_hierarchical_json
from backend.workflows.pdf_workflow.graph.stage import State

logger = logging.getLogger(__name__)


def _write_marker_image_file(dest_path: str, image_obj: Any) -> None:
    """Persist marker-rendered image object as an encoded image file."""
    if isinstance(image_obj, (bytes, bytearray)):
        with open(dest_path, "wb") as f:
            f.write(image_obj)
        return

    if hasattr(image_obj, "save"):
        image_obj.save(dest_path)
        return

    if hasattr(image_obj, "tobytes"):
        try:
            from PIL import Image
            import numpy as np

            arr = np.asarray(image_obj)
            img = Image.fromarray(arr)
            img.save(dest_path)
            return
        except Exception as exc:
            raise ValueError(f"Unsupported image object type for '{dest_path}': {type(image_obj)!r}") from exc

    raise ValueError(f"Unsupported image payload type for '{dest_path}': {type(image_obj)!r}")


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def _collect_marker_images(marker_output_dir: str) -> List[str]:
    """
    Scan the directory where marker wrote its image outputs and return a list
    of absolute paths to every image file it produced (sorted by name so that
    the page/figure ordering is stable).
    """
    if not os.path.isdir(marker_output_dir):
        return []

    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
    found = []
    for fname in sorted(os.listdir(marker_output_dir)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in IMAGE_EXTS:
            found.append(os.path.join(marker_output_dir, fname))
    return found


def _extract_marker_image_refs(markdown_text: str) -> List[str]:
    """
    Return all image src values that marker embedded in the markdown.
    marker uses both:
      - standard markdown:  ![alt](path)
      - HTML img tags:      <img ... src="path" ...>

    We collect them in document order so they align with the sorted file list.
    """
    refs_md = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown_text)
    refs_html = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', markdown_text, re.IGNORECASE)

    # Deduplicate while preserving order
    seen = set()
    ordered = []
    for r in refs_md + refs_html:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return ordered


def _build_image_infos_and_patch_markdown(
    markdown_text: str,
    marker_image_files: List[str],
    images_dir: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    1. Copy marker images into images_dir with canonical names (image_001.png …).
    2. Build image_infos list (same schema used by the DOCX pipeline).
    3. Patch the markdown so every marker image reference is replaced by the
       canonical relative path `images/image_NNN.ext`.

    Returns (patched_markdown, image_infos).
    """
    os.makedirs(images_dir, exist_ok=True)

    # ── Map marker src value → canonical name ──────────────────────────────
    #   marker refs in markdown may be bare filenames or relative paths like
    #   `_page_0_Figure_7.jpeg`. We match on the basename.
    image_refs_in_md = _extract_marker_image_refs(markdown_text)
    n_refs = len(image_refs_in_md)
    n_files = len(marker_image_files)
    logger.info(f"[PDF] marker markdown has {n_refs} image ref(s), {n_files} file(s) on disk")

    # Build two lookup tables:
    #   ref_to_canonical  – the markdown src value → canonical rel_path
    #   file_index        – list of (src_file, dest_rel_path, canonical_name) in copy order
    ref_to_canonical: Dict[str, str] = {}
    image_infos: List[Dict[str, Any]] = []
    MIME_TO_EXT = {
        ".jpg": ".jpg", ".jpeg": ".jpg", ".png": ".png",
        ".gif": ".gif", ".bmp": ".bmp", ".webp": ".webp",
        ".tif": ".png", ".tiff": ".png",
    }

    # Strategy: if marker image files and refs are same length, zip them.
    # Otherwise, try to match by basename.
    def _basename_no_ext(p: str) -> str:
        return os.path.splitext(os.path.basename(p))[0]

    if n_files == n_refs:
        pairs = list(zip(image_refs_in_md, marker_image_files))
    else:
        # Build a lookup: basename_no_ext → file_path
        file_map = {_basename_no_ext(f): f for f in marker_image_files}
        pairs = []
        for ref in image_refs_in_md:
            key = _basename_no_ext(ref)
            if key in file_map:
                pairs.append((ref, file_map[key]))
            else:
                logger.warning(f"[PDF] No file found for marker ref '{ref}' – skipping")

    for idx, (ref, src_file) in enumerate(pairs):
        src_ext = os.path.splitext(src_file)[1].lower()
        dest_ext = MIME_TO_EXT.get(src_ext, ".png")
        canonical_name = f"image_{idx + 1:03d}{dest_ext}"
        dest_path = os.path.join(images_dir, canonical_name)
        rel_path = f"images/{canonical_name}"

        try:
            shutil.copy2(src_file, dest_path)
            logger.info(f"[PDF] Copied image: {os.path.basename(src_file)} → {canonical_name}")
        except Exception as e:
            logger.warning(f"[PDF] Could not copy image {src_file}: {e}")
            continue

        # Map *all* representations of this ref to the canonical path
        ref_to_canonical[ref] = rel_path
        # Also map bare basename (marker sometimes writes just the filename)
        ref_to_canonical[os.path.basename(ref)] = rel_path

        image_infos.append({
            "filename": canonical_name,
            "rel_path": rel_path,
            "original_name": os.path.basename(src_file),
        })

    # ── Patch markdown ──────────────────────────────────────────────────────
    # Replace markdown image syntax
    def _replace_md_img(m: re.Match) -> str:
        alt = m.group(1)
        src = m.group(2)
        canon = ref_to_canonical.get(src) or ref_to_canonical.get(os.path.basename(src))
        if canon:
            return f"![{alt}]({canon})"
        return m.group(0)  # leave unchanged

    patched = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _replace_md_img, markdown_text)

    # Replace HTML img src attributes
    def _replace_html_img(m: re.Match) -> str:
        quote = m.group(1)
        src = m.group(2)
        canon = ref_to_canonical.get(src) or ref_to_canonical.get(os.path.basename(src))
        if canon:
            return f'src={quote}{canon}{quote}'
        return m.group(0)

    patched = re.sub(
        r'src=(["\'])([^"\']+)\1',
        _replace_html_img,
        patched,
        flags=re.IGNORECASE,
    )

    return patched, image_infos


# ---------------------------------------------------------------------------
# Main node
# ---------------------------------------------------------------------------

def convert_document(state: State, config: Optional[RunnableConfig] = None) -> State:
    """Convert PDF to markdown with Marker, extract & relocate images, then detect structure."""
    print("\n---------------- Executing Node: convert_pdf_document ----------------")

    if state.get("slide_chunks"):
        print("Skipping convert_pdf_document: slide_chunks already exists")
        return state

    start_time = time.time()
    pdf_file = state["pdf_file"]

    if config:
        configurable = config.get("configurable", {})
        stream_callback = configurable.get("stream_callback")
        if stream_callback:
            stream_callback(
                "status",
                {
                    "step": 1,
                    "title": "Analyze PDF Content",
                    "description": "Reading and converting PDF with Marker...",
                    "message": f"Processing file: {os.path.basename(pdf_file) if pdf_file else 'Unknown'}",
                },
            )

    if not os.path.exists(pdf_file):
        raise FileNotFoundError(f"The specified PDF file was not found: {pdf_file}")

    # ── Run Marker inside a dedicated temp directory so we can capture images ──
    # marker writes images alongside the markdown when output_dir is set.
    marker_tmp_dir = tempfile.mkdtemp(prefix="marker_pdf_")
    try:
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            from marker.output import text_from_rendered
        except ImportError as exc:
            raise ImportError(
                "marker-pdf is not installed. "
                "Add 'marker-pdf' to your pyproject.toml dependencies."
            ) from exc

        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(pdf_file)
        markdown_text, _, out_meta = text_from_rendered(rendered)

        # marker may have written images into `output_dir` (when configured) or
        # alongside the page in `images` sub-dict of rendered. Try both.
        marker_image_files: List[str] = []

        # 1. Check rendered.images dict (marker >= 0.3)
        if hasattr(rendered, "images") and rendered.images:
            for img_name, img_bytes in rendered.images.items():
                dest = os.path.join(marker_tmp_dir, img_name)
                try:
                    _write_marker_image_file(dest, img_bytes)
                    marker_image_files.append(dest)
                except Exception as e:
                    logger.warning(f"[PDF] Could not write rendered image {img_name}: {e}")
            logger.info(f"[PDF] Extracted {len(marker_image_files)} image(s) from rendered.images")

        # 2. Fallback: scan a images/ folder next to the pdf (some marker versions)
        if not marker_image_files:
            pdf_dir = os.path.dirname(pdf_file)
            candidate_dirs = [
                os.path.join(pdf_dir, "images"),
                pdf_dir,
                marker_tmp_dir,
            ]
            for candidate in candidate_dirs:
                found = _collect_marker_images(candidate)
                if found:
                    marker_image_files = found
                    logger.info(f"[PDF] Found {len(found)} image(s) in '{candidate}'")
                    break

    finally:
        # We keep marker_tmp_dir until after image processing below
        pass

    # ── Resolve where final images should live ─────────────────────────────
    # The canonical images_dir is determined by slide_options OR we use a
    # sibling folder next to the pdf. The slidegen_workflow main.py will
    # ultimately move them to <output_folder>/markdown/images/, but we need
    # a stable path right now so we can patch the markdown.
    slide_options = state.get("slide_options") or {}
    output_folder = slide_options.get("output_folder") or os.path.dirname(pdf_file)
    images_dir = os.path.join(output_folder, "markdown", "images")

    patched_markdown, image_infos = _build_image_infos_and_patch_markdown(
        markdown_text, marker_image_files, images_dir
    )

    # Clean up temp dir now that images have been copied
    try:
        shutil.rmtree(marker_tmp_dir, ignore_errors=True)
    except Exception:
        pass

    logger.info(f"[PDF] {len(image_infos)} image(s) processed and written to '{images_dir}'")
    if image_infos:
        logger.info(f"[PDF] image_infos: {[i['rel_path'] for i in image_infos]}")

    # ── Parse markdown structure ────────────────────────────────────────────
    title, structure = parse_markdown_to_hierarchical_json(patched_markdown)

    state["plain_text"] = patched_markdown
    state["image_infos"] = image_infos

    has_structure = len(structure) > 0
    workflow_mode = state.get("workflow_mode", "auto_no_heading")

    if workflow_mode == "auto_heading" and not has_structure:
        raise ValueError(
            "PDF does not contain heading structure, but mode auto_heading was selected. "
            "Please use auto_no_heading mode."
        )

    if has_structure:
        state["document_title"] = title
        state["document_structure"] = structure
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    else:
        fallback_title = os.path.splitext(os.path.basename(pdf_file))[0]
        state["document_title"] = title if title and title.strip() else fallback_title
        state["document_structure"] = []

    end_time = time.time()
    print(f"PDF conversion took {end_time - start_time:.2f} seconds.")
    print(f"[PDF] Extracted {len(image_infos)} image(s)")

    return state
