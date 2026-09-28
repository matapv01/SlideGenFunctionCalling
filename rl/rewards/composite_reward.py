"""Strict, frontend-grounded composite reward for XML SlideGen rollouts."""

from __future__ import annotations

import json
import os
import time
from html import escape
import tempfile
from collections import defaultdict, Counter
from pathlib import Path
from urllib.parse import urlsplit, unquote

import numpy as np

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.deck_style import apply_deck_style_to_tool_call
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    inject_approved_images,
    tool_matches_image_mode,
)
from rl.rewards.aesthetic_reward import _evaluate_batch, _get_model
from rl.rewards.content_reward import (
    _get_text_embedder,
    _lexical_score,
    _numeric_fact_coverage,
    _semantic_reward_scores,
)
from rl.slidegen_adapter import execute_tool, render_xml_batch_to_png


_TOOL_BY_NAME = {
    tool.name: tool
    for tools in TOOLS_DICT.values()
    for tool in tools
}
_COMPONENT_NAMES = (
    "lexical", "semantic", "numeric_fact", "dom", "aesthetic", "image_loaded"
)
_DOM_PENALTY_WEIGHTS = {
    "text_width": 0.20,
    "text_height": 0.25,
    "max_lines": 0.20,
    "slide_boundary": 0.40,
    "bbox_collision": 0.25,
}

_DOM_PENALTY_CAP = 2.0


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


def _dom_score(issues: list[dict]) -> float:
    """Return a normalized layout score; image availability has its own component."""
    unique_issues = {
        (
            issue.get("type"),
            str(issue.get("textbox", "")),
            str(issue.get("other", "")),
        )
        for issue in issues
        if issue.get("type") and issue.get("type") != "image_load"
    }
    penalty = sum(
        _DOM_PENALTY_WEIGHTS.get(issue_type, 0.10)
        for issue_type, _, _ in unique_issues
    )
    return 1.0 - min(_DOM_PENALTY_CAP, penalty) / _DOM_PENALTY_CAP


def _weighted_reward(components: dict[str, float], weights: dict[str, float]) -> float:
    """Combine independent, bounded reward signals with explicit configured weights."""
    if components.keys() != weights.keys():
        raise ValueError("Reward components and weights must have identical keys")
    if any(not np.isfinite(value) or not 0.0 <= value <= 1.0 for value in components.values()):
        raise ValueError("Every reward component must be finite and in [0, 1]")
    return float(sum(weights[name] * value for name, value in components.items()))


def _asset_key(url: str) -> str:
    parsed = urlsplit(str(url))
    path = unquote(parsed.path)
    # The FE can resolve a portable static path against a separate BE origin.
    return path if path.startswith("/static/output/") else parsed._replace(fragment="").geturl()


def _image_loading_score(expected_urls: list[str], image_status: list[dict]) -> float:
    if not expected_urls:
        return 1.0
    loaded = Counter(_asset_key(image.get("src", "")) for image in image_status if image.get("loaded"))
    matched = 0
    for url in expected_urls:
        key = _asset_key(url)
        if loaded[key] > 0:
            matched += 1
            loaded[key] -= 1
    return matched / len(expected_urls)


def preflight_reward_runtime(approved_images=None) -> None:
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


    # Exercise each distinct corpus image through the same FE path as rewards.
    # Local decoding catches corrupt files; URL matching catches broken serving.
    from PIL import Image
    unique_assets = {}
    for asset in approved_images or []:
        url = str(asset.get("source_path") or "")
        if not url.startswith("/static/output/"):
            raise ValueError("Reward preflight requires locally cached corpus images")
        unique_assets.setdefault(url, asset)
    for asset in unique_assets.values():
        with Image.open(asset["local_path"]) as image:
            image.verify()
    urls = list(unique_assets)
    with tempfile.TemporaryDirectory(prefix="slidegen_image_preflight_") as directory:
        for start in range(0, len(urls), 16):
            batch = urls[start:start + 16]
            xmls = [
                '<presentation width="1600" height="900"><slide background="#ffffff">'
                f'<image src="{escape(url, quote=True)}" x="80" y="80" width="600" height="450" />'
                '</slide></presentation>' for url in batch
            ]
            paths = [str(Path(directory) / f"asset-{start + i}.png") for i in range(len(batch))]
            results = render_xml_batch_to_png(xmls, paths, max_concurrency=4)
            for url, result in zip(batch, results, strict=True):
                if _image_loading_score([url], result.get("image_status") or []) != 1.0:
                    raise RuntimeError(f"Corpus image cannot be loaded by the frontend: {url}")


def reward_weights() -> dict[str, float]:
    weights = {
        "lexical": float(os.getenv("RL_REWARD_LEXICAL_WEIGHT", "0.7")),
        "semantic": float(os.getenv("RL_REWARD_SEMANTIC_WEIGHT", "0.8")),
        "numeric_fact": float(os.getenv("RL_REWARD_NUMERIC_FACT_WEIGHT", "1.5")),
        "dom": float(os.getenv("RL_REWARD_DOM_WEIGHT", "0.8")),
        "aesthetic": float(os.getenv("RL_REWARD_AESTHETIC_WEIGHT", "1.0")),
        "image_loaded": float(os.getenv("RL_REWARD_IMAGE_LOADED_WEIGHT", "0.4")),
    }
    if any(not np.isfinite(value) or value < 0 for value in weights.values()):
        raise ValueError("Reward weights must be finite and nonnegative")
    return weights


def slidegen_composite_reward(
    prompts,
    completions,
    assigned_tool_name=None,
    source_content=None,
    deck_style=None,
    approved_images=None,
    image_mode=None,
    numeric_facts=None,
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
    fact_rows = list(numeric_facts) if numeric_facts is not None else [None] * len(completions)
    if not (
        len(expected)
        == len(sources)
        == len(styles)
        == len(assets_by_sample)
        == len(modes_by_sample)
        == len(fact_rows)
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
            if len(injection_history) != len(sample_images):
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
                    "injected_image_count": len(sample_images),
                    "expected_image_urls": [item["result_url"] for item in injection_history],
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
        render_started = time.perf_counter()
        frontend_results = render_xml_batch_to_png(
            [row["xml"] for row in rows], [str(path) for path in paths],
            max_concurrency=workers,
        )
        render_seconds = time.perf_counter() - render_started
        for row, frontend in zip(rows, frontend_results, strict=True):
            image_status = list(frontend.get("image_status") or [])
            expected_count = int(row["injected_image_count"])
            score = _image_loading_score(row["expected_image_urls"], image_status)
            failed_count = sum(not image.get("loaded") for image in image_status)
            missing_count = round(expected_count * (1.0 - score))
            for _ in range(max(failed_count, missing_count)):
                frontend.setdefault("issues", []).append({"type": "image_load"})
            row["image_loaded"] = score
        vit_started = time.perf_counter()
        aesthetic_scores = _evaluate_batch(_get_model(), paths)
        vit_seconds = time.perf_counter() - vit_started

    if len(frontend_results) != len(rows) or len(aesthetic_scores) != len(rows):
        raise RuntimeError("Renderer or ViT returned a different number of scores")

    generated_texts = [result["visible_text"] for result in frontend_results]
    embedder = _get_text_embedder()
    semantic_started = time.perf_counter()
    semantic_scores = _semantic_reward_scores(
        [row["source"] for row in rows], generated_texts, embedder,
    )
    semantic_seconds = time.perf_counter() - semantic_started
    if log_metric is not None:
        log_metric("reward_time/render_seconds", render_seconds)
        log_metric("reward_time/vit_seconds", vit_seconds)
        log_metric("reward_time/semantic_seconds", semantic_seconds)
    weights = reward_weights()
    component_values = defaultdict(list)
    for row, frontend, semantic, aesthetic in zip(
        rows, frontend_results, semantic_scores, aesthetic_scores, strict=True,
    ):
        source_facts = fact_rows[row["index"]]
        lexical = _lexical_score(row["source"], frontend["visible_text"])
        fact_coverage = _numeric_fact_coverage(
            row["source"], frontend["visible_text"], source_facts,
        )
        dom = _dom_score(frontend["issues"])
        components = {
            "lexical": lexical,
            "semantic": semantic,
            "numeric_fact": fact_coverage,
            "dom": dom,
            "aesthetic": float(aesthetic),
            "image_loaded": float(row["image_loaded"]),
        }
        rewards[row["index"]] = _weighted_reward(components, weights)
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
