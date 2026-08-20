"""Observation-only ViT evaluation for generated slides."""

import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.runnables import RunnableConfig

from backend.config import STATIC_DIR
from backend.infrastructure.aesthetic.vit_aesthetic_provider import get_vit_evaluator
from backend.workflows.slidegen_workflow.graph.stage import State


logger = logging.getLogger(__name__)


def _static_relative_path(path: str | Path | None) -> str | None:
    """Return a static-relative path without exposing an absolute filesystem path."""
    if not path:
        return None

    try:
        return Path(path).resolve().relative_to(STATIC_DIR.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _static_url(path: str | Path | None) -> str | None:
    relative_path = _static_relative_path(path)
    return f"/static/{relative_path}" if relative_path else None


def _evaluation_path(
    config: RunnableConfig,
    image_path: str | None,
    slide_index: int,
) -> Path:
    """Resolve the per-slide evaluation file inside the workflow output."""
    configurable = config.get("configurable", {}) if config else {}
    configured_dir = configurable.get("evaluation_dir")

    if configured_dir:
        evaluation_dir = Path(configured_dir)
    elif image_path:
        image_file = Path(image_path)
        # The XML renderer stores images in <project>/output/png. Keep the
        # JSON beside that directory in <project>/output/evaluation.
        evaluation_dir = (
            image_file.parent.parent / "evaluation"
            if image_file.parent.name.lower() == "png"
            else image_file.parent / "evaluation"
        )
    else:
        temp_dir = configurable.get("temp_dir")
        evaluation_dir = Path(temp_dir) / "evaluation" if temp_dir else STATIC_DIR / "evaluation"

    return evaluation_dir / f"slide_{slide_index + 1}.json"


def _save_evaluation_json(
    config: RunnableConfig,
    slide_index: int,
    image_path: str | None,
    record: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Persist one evaluation and return its internal path and public URL."""
    evaluation_path = _evaluation_path(config, image_path, slide_index)

    try:
        evaluation_path.parent.mkdir(parents=True, exist_ok=True)
        evaluation_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
    except Exception:
        logger.exception(
            "Could not save ViT evaluation JSON for slide %s",
            slide_index + 1,
        )
        return None, None

    return str(evaluation_path), _static_url(evaluation_path)


def slide_evaluator(state: State, config: RunnableConfig) -> State:
    """Evaluate a slide with ViT and report the result without retrying.

    The evaluation is intentionally observational. Its decision is kept in
    ``state`` for diagnostics, while detected issues are reported through the
    application logger and never fed back into slide generation.
    """
    retry_count = state.get("retry_count", 0)
    idx = state["current_slide_index"]
    logger.info(
        "Slide evaluator started (slide=%s, retry=%s, model=ViT)",
        idx + 1,
        retry_count,
    )

    current_image_path = state.get("current_image_path")
    state["vlm_feedback"] = "No feedback provided."
    state["vlm_decision"] = "not_evaluated"
    state["vlm_evaluation_path"] = ""
    state["vlm_evaluation_url"] = ""

    image_relative_path = _static_relative_path(current_image_path)
    evaluation_record: dict[str, Any] = {
        "schema_version": "1.0",
        "evaluator": "ViT",
        "slide_index": idx + 1,
        "retry_count": retry_count,
        "decision": "not_evaluated",
        "accepted": None,
        "errors": [],
        "scores": {},
        "image": {
            "relative_path": image_relative_path,
            "url": _static_url(current_image_path),
        },
    }

    if not current_image_path:
        logger.error(
            "ViT evaluation skipped for slide %s: current_image_path is missing",
            idx + 1,
        )
        state["vlm_decision"] = "evaluation_error"
        evaluation_record["decision"] = "evaluation_error"
    else:
        logger.info("Sending slide %s to ViT evaluator: %s", idx + 1, current_image_path)

        try:
            vit_evaluator = get_vit_evaluator()
            is_accept, errors, detailed_scores = vit_evaluator.evaluate(current_image_path)
        except Exception as exc:
            logger.exception("ViT evaluation failed for slide %s: %s", idx + 1, exc)
            state["vlm_decision"] = "evaluation_error"
            evaluation_record["decision"] = "evaluation_error"
            evaluation_record["error"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        else:
            errors = list(errors or [])
            evaluation_record["accepted"] = bool(is_accept)
            evaluation_record["errors"] = errors
            evaluation_record["scores"] = detailed_scores or {}

            logger.info(
                "ViT scores for slide %s: %s",
                idx + 1,
                json.dumps(detailed_scores, indent=2, ensure_ascii=False, default=str),
            )

            if is_accept:
                state["vlm_decision"] = "accept"
                evaluation_record["decision"] = "accept"
                logger.info("ViT evaluation passed for slide %s", idx + 1)
            else:
                errors = errors or ["unspecified aesthetic issue"]
                evaluation_record["errors"] = errors
                state["vlm_decision"] = "deny"
                evaluation_record["decision"] = "deny"
                logger.warning(
                    "ViT detected aesthetic errors on slide %s: %s",
                    idx + 1,
                    "; ".join(str(error) for error in errors),
                )

    if state["vlm_decision"] == "evaluation_error" and "error" not in evaluation_record:
        evaluation_record["error"] = {
            "type": "MissingImage",
            "message": "current_image_path is missing",
        }

    saved_path, saved_url = _save_evaluation_json(
        config=config,
        slide_index=idx,
        image_path=current_image_path,
        record=evaluation_record,
    )
    if saved_path:
        state["vlm_evaluation_path"] = saved_path
    if saved_url:
        state["vlm_evaluation_url"] = saved_url
        logger.info("Saved ViT evaluation JSON for slide %s: %s", idx + 1, saved_url)

    logger.info(
        "ViT evaluation completed for slide %s (decision=%s; observation-only)",
        idx + 1,
        state["vlm_decision"],
    )
    return state
