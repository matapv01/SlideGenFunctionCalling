"""Strict, frontend-grounded composite reward for XML SlideGen rollouts."""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from threading import Lock

import numpy as np

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.deck_style import apply_deck_style_to_tool_call
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    inject_approved_images,
    tool_matches_image_mode,
)
from rl.rewards.aesthetic_reward import _evaluate_batch, _get_model
from rl.rewards.content_reward import clean_words
from rl.rewards.dom_overflow_reward import _PENALTY_WEIGHTS
from rl.slidegen_adapter import execute_tool, render_xml_batch_to_png


_TOOL_BY_NAME = {
    tool.name: tool
    for tools in TOOLS_DICT.values()
    for tool in tools
}
_TEXT_EMBEDDER = None
_TEXT_EMBEDDER_LOCK = Lock()
_COMPONENT_NAMES = (
    "valid", "lexical", "semantic", "format", "dom", "aesthetic", "image_loaded"
)


def set_text_embedder(model) -> None:
    """Share the retriever's SentenceTransformer instead of loading it twice."""
    global _TEXT_EMBEDDER
    _TEXT_EMBEDDER = model


def _get_text_embedder():
    global _TEXT_EMBEDDER
    if _TEXT_EMBEDDER is None:
        with _TEXT_EMBEDDER_LOCK:
            if _TEXT_EMBEDDER is None:
                from sentence_transformers import SentenceTransformer
                from backend import config

                _TEXT_EMBEDDER = SentenceTransformer(
                    config.EMBEDDING_MODEL_NAME,
                    device=config.EMBEDDING_DEVICE,
                    cache_folder=config.EMBEDDING_CACHE_DIR,
                )
    return _TEXT_EMBEDDER


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_canonical_completion(completion: str) -> dict | None:
    if not isinstance(completion, str):
        return None
    stripped = completion.strip()
    if (
        not stripped.startswith("<tool_call>")
        or not stripped.endswith("</tool_call>")
        or stripped.count("<tool_call>") != 1
        or stripped.count("</tool_call>") != 1
    ):
        return None
    body = stripped[len("<tool_call>") : -len("</tool_call>")].strip()
    parsed = json.loads(body, object_pairs_hook=_reject_duplicate_keys)
    if (
        not isinstance(parsed, dict)
        or set(parsed) != {"name", "arguments"}
        or not isinstance(parsed.get("name"), str)
        or not isinstance(parsed.get("arguments"), dict)
    ):
        return None
    return parsed


def _validate_tool_arguments(tool, arguments: dict) -> dict | None:
    schema = getattr(tool, "args_schema", None)
    if schema is None:
        return None
    fields = getattr(schema, "model_fields", None)
    if fields is None or set(arguments) - set(fields):
        return None
    validated = schema.model_validate(arguments)
    return validated.model_dump(exclude_unset=True)


def _lexical_score(source: str, generated: str) -> float:
    source_words = clean_words(source)
    generated_words = clean_words(generated)
    if not source_words:
        return 1.0
    overlap = len(set(source_words).intersection(generated_words)) / len(set(source_words))
    length_ratio = len(generated_words) / max(1, len(source_words))
    return float(max(0.0, min(1.0, overlap * min(1.0, length_ratio / 0.3))))


def _dom_score(issues: list[dict]) -> float:
    penalty = min(
        2.0,
        sum(_PENALTY_WEIGHTS.get(issue["type"], 0.10) for issue in issues),
    )
    return max(-1.0, 1.0 - penalty)


def _chunk_semantic_text(
    text: str, tokenizer, max_seq_length: int
) -> tuple[list[str], list[int]]:
    """Split text by model tokens so embedding never truncates slide content."""
    value = str(text).strip() or "."
    if tokenizer is None:
        tokens = value.split()
        chunk_size = max(1, min(96, max_seq_length - 2))
        overlap = min(12, chunk_size // 8)
        chunks, weights = [], []
        start = 0
        while start < len(tokens):
            end = min(len(tokens), start + chunk_size)
            chunks.append(" ".join(tokens[start:end]))
            weights.append(end - start)
            if end == len(tokens):
                break
            start = end - overlap
        return chunks, weights

    token_ids = tokenizer.encode(value, add_special_tokens=False)
    if not token_ids:
        token_ids = tokenizer.encode(".", add_special_tokens=False)
    chunk_size = max(1, max_seq_length - tokenizer.num_special_tokens_to_add(pair=False))
    overlap = min(16, chunk_size // 8)
    chunks, weights = [], []
    start = 0
    while start < len(token_ids):
        end = min(len(token_ids), start + chunk_size)
        chunk = tokenizer.decode(token_ids[start:end], skip_special_tokens=True).strip()
        chunks.append(chunk or ".")
        weights.append(end - start)
        if end == len(token_ids):
            break
        start = end - overlap
    return chunks, weights


def _semantic_reward_scores(
    sources: list[str], generated: list[str], embedder
) -> list[float]:
    tokenizer = getattr(embedder, "tokenizer", None)
    max_seq_length = int(getattr(embedder, "max_seq_length", 128) or 128)
    grouped_chunks = []
    all_chunks = []
    for source, output in zip(sources, generated, strict=True):
        source_chunks, source_weights = _chunk_semantic_text(
            source, tokenizer, max_seq_length
        )
        generated_chunks, generated_weights = _chunk_semantic_text(
            output, tokenizer, max_seq_length
        )
        source_start = len(all_chunks)
        all_chunks.extend(source_chunks)
        generated_start = len(all_chunks)
        all_chunks.extend(generated_chunks)
        grouped_chunks.append(
            (
                source_start,
                len(source_chunks),
                source_weights,
                generated_start,
                len(generated_chunks),
                generated_weights,
            )
        )

    embeddings = np.asarray(
        embedder.encode(
            all_chunks,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
    )
    scores = []
    for (
        source_start,
        source_count,
        source_weights,
        generated_start,
        generated_count,
        generated_weights,
    ) in grouped_chunks:
        source_vectors = embeddings[source_start : source_start + source_count]
        generated_vectors = embeddings[generated_start : generated_start + generated_count]
        similarities = np.clip(source_vectors @ generated_vectors.T, 0.0, 1.0)
        source_coverage = np.average(
            similarities.max(axis=1), weights=source_weights
        )
        generated_precision = np.average(
            similarities.max(axis=0), weights=generated_weights
        )
        denominator = source_coverage + generated_precision
        scores.append(
            float(2.0 * source_coverage * generated_precision / denominator)
            if denominator > 0
            else 0.0
        )
    return scores


def preflight_reward_runtime() -> None:
    """Load and execute the reward model against the real BE frontend render."""
    model = _get_model()
    from rl.slidegen_adapter import render_xml_to_png

    sample_xml = (
        '<presentation width="1600" height="900" slideWidthInches="13.333" '
        'slideHeightInches="7.5"><slide background="#ffffff">'
        '<textbox x="80" y="80" width="500" height="100" size="32">'
        'GRPO frontend preflight</textbox></slide></presentation>'
    )
    with tempfile.TemporaryDirectory(prefix="slidegen_preflight_") as directory:
        output = Path(directory) / "preview.png"
        render_xml_to_png(sample_xml, str(output))
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("BE XML frontend preview produced no image")
        aesthetic_score = _evaluate_batch(model, [output])[0]
        if not np.isfinite(aesthetic_score) or not 0.0 <= aesthetic_score <= 1.0:
            raise RuntimeError(
                f"ViT preflight returned an invalid aesthetic score: {aesthetic_score}"
            )


def slidegen_composite_reward(
    prompts,
    completions,
    assigned_tool_name=None,
    source_content=None,
    deck_style=None,
    approved_images=None,
    image_mode=None,
    log_metric=None,
    **kwargs,
):
    del prompts, kwargs
    expected = list(assigned_tool_name) if assigned_tool_name is not None else []
    assets_by_sample = (
        list(approved_images)
        if approved_images is not None
        else [[] for _ in completions]
    )
    modes_by_sample = (
        list(image_mode)
        if image_mode is not None
        else ["none"] * len(completions)
    )
    sources = list(source_content) if source_content is not None else []
    styles = list(deck_style) if deck_style is not None else []
    if not (
        len(expected)
        == len(sources)
        == len(styles)
        == len(assets_by_sample)
        == len(modes_by_sample)
        == len(completions)
    ):
        raise ValueError("GRPO reward metadata does not match completion batch size")

    invalid_reward = float(os.getenv("RL_INVALID_REWARD", "-2.0"))
    rewards = [invalid_reward] * len(completions)
    rows = []
    for index, completion in enumerate(completions):
        try:
            parsed = _parse_canonical_completion(completion)
            if parsed is None or parsed["name"] != expected[index]:
                continue
            tool = _TOOL_BY_NAME.get(expected[index])
            if tool is None:
                continue
            mode = str(modes_by_sample[index] or "none")
            sample_images = list(assets_by_sample[index] or [])
            if mode not in {"none", "semantic"}:
                continue
            if mode == "semantic" and not sample_images:
                continue
            if not tool_matches_image_mode(tool, mode, len(sample_images)):
                continue
            arguments = _validate_tool_arguments(tool, parsed["arguments"])
            if arguments is None:
                continue
            validated_call = {"name": tool.name, "arguments": arguments}
            styled_call = apply_deck_style_to_tool_call(
                validated_call, [tool], styles[index] or {}
            )
            injected_call, injection_history = inject_approved_images(
                styled_call,
                tool=tool,
                approved_images=sample_images if mode == "semantic" else [],
                asset_dir=None,
            )
            if mode == "semantic" and not injection_history:
                continue
            # Validate the final styled and image-injected call before execution.
            styled_arguments = _validate_tool_arguments(
                tool, injected_call.get("arguments", {})
            )
            if styled_arguments is None:
                continue
            xml_content = execute_tool(
                {"name": tool.name, "arguments": styled_arguments}
            )
            rows.append(
                {
                    "index": index,
                    "source": str(sources[index]),
                    "xml": xml_content,
                    "image_mode": mode,
                    "injected_image_count": len(injection_history),
                    "format": 1.0,
                }
            )
        except (TypeError, ValueError, KeyError):
            # Schema and tool-input failures make this completion invalid.
            continue

    if not rows:
        if log_metric is not None:
            log_metric("reward/valid_fraction", 0.0)
            for name in _COMPONENT_NAMES:
                log_metric(f"reward_component/{name}", 0.0)
        return rewards

    workers = max(1, min(int(os.getenv("RL_REWARD_RENDER_WORKERS", "4")), len(rows)))
    with tempfile.TemporaryDirectory(prefix="slidegen_reward_") as directory:
        paths = [Path(directory) / f"reward_{row['index']}.png" for row in rows]
        frontend_results = render_xml_batch_to_png(
            [row["xml"] for row in rows], [str(path) for path in paths],
            max_concurrency=workers,
        )
        for row, frontend in zip(rows, frontend_results, strict=True):
            image_status = list(frontend.get("image_status") or [])
            expected_count = int(row["injected_image_count"])
            loaded_count = sum(bool(image.get("loaded")) for image in image_status)
            missing_count = max(0, expected_count - len(image_status))
            failed_count = len(image_status) - loaded_count
            for _ in range(failed_count + missing_count):
                frontend.setdefault("issues", []).append({"type": "image_load"})
            row["image_loaded"] = (
                min(1.0, loaded_count / expected_count)
                if expected_count
                else 1.0
            )
        aesthetic_scores = _evaluate_batch(_get_model(), paths)

    if len(frontend_results) != len(rows) or len(aesthetic_scores) != len(rows):
        raise RuntimeError("Renderer or ViT returned a different number of scores")

    generated_texts = [result["visible_text"] for result in frontend_results]
    embedder = _get_text_embedder()
    semantic_scores = _semantic_reward_scores(
        [row["source"] for row in rows], generated_texts, embedder
    )
    weights = {
        "valid": float(os.getenv("RL_REWARD_VALID_WEIGHT", "1.5")),
        "lexical": float(os.getenv("RL_REWARD_LEXICAL_WEIGHT", "0.7")),
        "semantic": float(os.getenv("RL_REWARD_SEMANTIC_WEIGHT", "0.8")),
        "format": float(os.getenv("RL_REWARD_FORMAT_WEIGHT", "0.3")),
        "dom": float(os.getenv("RL_REWARD_DOM_WEIGHT", "0.8")),
        "aesthetic": float(os.getenv("RL_REWARD_AESTHETIC_WEIGHT", "1.0")),
        "image_loaded": float(os.getenv("RL_REWARD_IMAGE_LOADED_WEIGHT", "0.4")),
    }
    component_values = defaultdict(list)
    for row, frontend, semantic, aesthetic in zip(
        rows, frontend_results, semantic_scores, aesthetic_scores, strict=True,
    ):
        lexical = _lexical_score(row["source"], frontend["visible_text"])
        dom = _dom_score(frontend["issues"])
        components = {
            "valid": 1.0,
            "lexical": lexical,
            "semantic": semantic,
            "image_loaded": float(row["image_loaded"]),
            "format": row["format"],
            "dom": dom,
            "aesthetic": float(aesthetic),
        }
        rewards[row["index"]] = float(
            sum(weights[name] * value for name, value in components.items())
        )
        for name, value in components.items():
            component_values[name].append(value)

    if log_metric is not None:
        log_metric("reward/valid_fraction", len(rows) / max(1, len(completions)))
        for name in _COMPONENT_NAMES:
            values = component_values.get(name, [])
            log_metric(
                f"reward_component/{name}",
                float(np.mean(values)) if values else 0.0,
            )

    print(
        "  [Composite Reward] "
        f"valid={len(rows)}/{len(completions)} "
        f"components={{{' '.join(f'{key}={np.mean(value):.3f}' for key, value in component_values.items())}}} "
        f"scores=[{' '.join(f'{score:.3f}' for score in rewards)}]"
    )
    return rewards
