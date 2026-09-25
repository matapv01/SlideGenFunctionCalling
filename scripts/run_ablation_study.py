#!/usr/bin/env python3
"""Run paired SlideGen ablations from one preprocessing result per document."""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.api.dependencies import get_slidegen_workflow_service
from backend.config import (
    ENABLE_VIT_EVALUATION,
    IDEA_STRUCTURE_LLM_MODEL,
    IDEA_STRUCTURE_LLM_TEMPERATURE,
    LLM_MODEL,
    LLM_TEMPERATURE,
    TOOL_RETRIEVER_TOP_K,
)
from backend.workflows.slidegen_workflow.ablation import (
    FULL,
    NO_PLANNER,
    NO_PLANNER_NO_RETRIEVER,
    NO_RETRIEVER,
    ablation_manifest,
)
from backend.workflows.slidegen_workflow.main import main_workflow


MODES = (FULL, NO_PLANNER, NO_RETRIEVER, NO_PLANNER_NO_RETRIEVER)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "document"


def json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    return repr(value)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=json_default) + "\n",
        encoding="utf-8",
    )


def copy_final_pngs(mode_dir: Path, evaluation_dir: Path) -> int:
    source_dir = mode_dir / "output" / "png"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(source_dir.glob("*.png")) if source_dir.is_dir() else []
    for path in paths:
        shutil.copy2(path, evaluation_dir / path.name)
    return len(paths)


async def run() -> int:
    args = parse_args()
    docs_dir = args.docs_dir.resolve()
    output_root = (args.output_root / args.run_id).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    docs = sorted(docs_dir.glob("*.docx"), key=lambda path: path.name.lower())
    if not docs:
        raise FileNotFoundError(f"No DOCX files found in {docs_dir}")
    if ENABLE_VIT_EVALUATION:
        raise RuntimeError("ENABLE_VIT_EVALUATION must be false for generation ablations")

    service = get_slidegen_workflow_service()
    providers = service._get_providers()
    slide_options = {
        "workflow_mode": "auto_no_heading",
        "output_format": "xml",
        "enable_transition_slides": True,
        "enable_thank_you_slide": True,
        "enable_vit_evaluation": False,
    }
    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "paired_protocol": (
            "Each document is preprocessed once; a deep copy of the same document "
            "state is supplied to every generation variant."
        ),
        "documents": [path.name for path in docs],
        "modes": list(MODES),
        "generation_configuration": {
            "slide_options": slide_options,
            "slide_llm_model": LLM_MODEL,
            "slide_llm_temperature": LLM_TEMPERATURE,
            "planner_llm_model": IDEA_STRUCTURE_LLM_MODEL,
            "planner_llm_temperature": IDEA_STRUCTURE_LLM_TEMPERATURE,
            "retriever_top_k": TOOL_RETRIEVER_TOP_K,
            "vit_in_generation": False,
            "rule_based_generation_checks": True,
        },
        "mode_manifests": {mode: ablation_manifest(mode) for mode in MODES},
        "runs": [],
    }
    summary_path = output_root / "generation_summary.json"
    write_json(summary_path, summary)

    failures = 0
    for doc_index, doc_path in enumerate(docs, start=1):
        doc_slug = slugify(doc_path.stem)
        doc_dir = output_root / "decks" / doc_slug
        doc_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[{doc_index}/{len(docs)}] Preprocessing once: {doc_path.name}", flush=True)
        preprocess_started = time.perf_counter()
        try:
            doc_state = await service.doc_workflow_service.preprocess_docx(
                docx_file=str(doc_path),
                workflow_mode=slide_options["workflow_mode"],
                slide_options=slide_options,
            )
        except Exception as exc:
            failures += len(MODES)
            summary["runs"].append(
                {
                    "document": doc_path.name,
                    "mode": "all",
                    "status": "preprocessing_failed",
                    "error": repr(exc),
                }
            )
            write_json(summary_path, summary)
            print(f"Preprocessing failed for {doc_path.name}: {exc!r}", flush=True)
            continue

        preprocess_seconds = time.perf_counter() - preprocess_started
        write_json(doc_dir / "preprocessed_state.json", doc_state)
        write_json(
            doc_dir / "preprocessing_manifest.json",
            {
                "document": doc_path.name,
                "seconds": preprocess_seconds,
                "slide_chunks": len(doc_state.get("slide_chunks", [])),
            },
        )

        for mode_index, mode in enumerate(MODES, start=1):
            mode_dir = doc_dir / mode
            options = dict(slide_options, ablation_mode=mode)
            print(
                f"[{doc_index}/{len(docs)} · {mode_index}/{len(MODES)}] "
                f"Generating {doc_path.name} / {mode}",
                flush=True,
            )
            started = time.perf_counter()
            error = None
            try:
                result = await main_workflow(
                    router_flags=False,
                    docx_file=str(doc_path),
                    output_folder=str(mode_dir),
                    doc_state=copy.deepcopy(doc_state),
                    infra_providers=providers,
                    max_retries_per_slide=1,
                    slide_options=options,
                )
                status = "completed" if result else "failed"
                if not result:
                    error = "main_workflow returned no output path"
            except Exception as exc:
                status = "failed"
                error = repr(exc)

            elapsed = time.perf_counter() - started
            png_count = copy_final_pngs(
                mode_dir,
                output_root / "evaluation_input" / doc_slug / mode,
            )
            xml_dir = mode_dir / "output" / "xml"
            xml_count = len(list(xml_dir.glob("*.xml"))) if xml_dir.is_dir() else 0
            record = {
                "document": doc_path.name,
                "document_slug": doc_slug,
                "mode": mode,
                "status": status,
                "seconds": elapsed,
                "preprocessing_seconds_shared": preprocess_seconds,
                "input_slide_chunks": len(doc_state.get("slide_chunks", [])),
                "final_png_count": png_count,
                "final_xml_count": xml_count,
                "output_directory": str(mode_dir),
                "error": error,
            }
            summary["runs"].append(record)
            if status != "completed" or png_count == 0:
                failures += 1
            write_json(mode_dir / "run_record.json", record)
            write_json(summary_path, summary)
            print(
                f"Finished {doc_path.name} / {mode}: {status}, "
                f"{png_count} final PNG(s), {elapsed:.1f}s",
                flush=True,
            )

    summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    summary["failed_variants"] = failures
    summary["completed_variants"] = sum(
        run.get("status") == "completed" and run.get("final_png_count", 0) > 0
        for run in summary["runs"]
    )
    summary["status"] = "completed" if failures == 0 else "completed_with_failures"
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
