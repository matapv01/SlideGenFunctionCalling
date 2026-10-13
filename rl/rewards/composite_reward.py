"""Strict, frontend-grounded composite reward for XML SlideGen rollouts."""

from __future__ import annotations

import json
import os
import re
import shutil
import time
from html import escape
import tempfile
from collections import defaultdict, Counter
from pathlib import Path
from urllib.parse import urlsplit, unquote

import numpy as np

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.deck_style import apply_deck_style_to_tool_call
from backend.workflows.slidegen_workflow.utils.xml_autofit import fit_xml_text
from backend.workflows.slidegen_workflow.utils.xml_contrast import enforce_xml_text_contrast
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    NoApprovedImageError,
    inject_approved_images,
    tool_matches_image_mode,
)
from rl.rewards.aesthetic_reward import _evaluate_batch, _get_model, reward_model_settings
from rl.rewards.content_reward import (
    _get_text_embedder,
    _language_consistency,
    _lexical_score,
    _numeric_fact_coverage,
    _semantic_reward_scores,
    _unsupported_number_fraction,
    _is_checkable_number,
    _number_support_key,
    _numeric_occurrences,
)
from rl.slidegen_adapter import execute_tool, render_xml_batch_to_png


_TOOL_BY_NAME = {
    tool.name: tool
    for tools in TOOLS_DICT.values()
    for tool in tools
}
_COMPONENT_NAMES = (
    "lexical", "semantic", "numeric_fact", "language", "dom", "aesthetic", "image_loaded"
)
_DOM_PENALTY_WEIGHTS = {
    # Calibrated on 820 human-rated slides (flag "display error"): cut-off text, collisions and unreadable
    # colours were confirmed by people 73-90% of the time; width overflow alone never was (0/38) and
    # box-height overflow alone rarely (10%), so those two no longer dominate the layout score.
    "text_cutoff": 0.40,
    "low_contrast": 0.40,
    "bbox_collision": 0.30,
    "markup_leak": 0.5,
    "slide_boundary": 0.15,
    "tiny_text": 0.30,
    # Round 2d learned to write 14% less text to avoid these two, which people rarely see (10% when alone),
    # and lost content coverage; they now carry almost no weight.
    "text_height": 0.03,
    "max_lines": 0.0,
    "text_width": 0.0,
}
# Rich-text markup the frontend failed to parse shows up verbatim on the slide.
_MARKUP_LEAK = re.compile(r"\[\[|\]\]|\[/?hl\b|</?(?:span|b|i|u|strong|em|font|br|p|div)\b[^>]*>|\bstyle\s*=\s*[\"']", re.IGNORECASE)

# One clipped textbox costs 0.2-0.4; about three distinct failures zero the component.
_DOM_PENALTY_CAP = 1.0


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_qwen_native_tool_call(body: str) -> dict | None:
    match = re.fullmatch(
        r"<function=([A-Za-z_][A-Za-z0-9_]*)>\s*(.*?)\s*</function>",
        body,
        flags=re.DOTALL,
    )
    if match is None:
        return None
    name, arguments_body = match.groups()
    parameter_pattern = re.compile(
        r"<parameter=([A-Za-z_][A-Za-z0-9_]*)>(.*?)</parameter>",
        flags=re.DOTALL,
    )
    parameters = list(parameter_pattern.finditer(arguments_body))
    if not parameters or parameter_pattern.sub("", arguments_body).strip():
        return None

    tool = _TOOL_BY_NAME.get(name)
    try:
        properties = (
            tool.args_schema.model_json_schema().get("properties", {})
            if tool is not None
            else {}
        )
    except (AttributeError, TypeError, ValueError):
        properties = {}

    arguments = {}
    for parameter in parameters:
        key, raw_value = parameter.groups()
        if key in arguments:
            return None
        value = raw_value.strip()
        expected_type = (properties.get(key) or {}).get("type")
        if expected_type in {"array", "object", "integer", "number", "boolean"}:
            try:
                value = json.loads(value, object_pairs_hook=_reject_duplicate_keys)
            except (json.JSONDecodeError, ValueError):
                # Structured and non-text parameters must parse as JSON. Never
                # pass malformed structured data to the compatibility executor.
                return None
            if expected_type == "array" and not isinstance(value, list):
                return None
            if expected_type == "object" and not isinstance(value, dict):
                return None
            if expected_type == "boolean" and not isinstance(value, bool):
                return None
        arguments[key] = value
    return {"name": name, "arguments": arguments}


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
    if body.startswith("<function="):
        return _parse_qwen_native_tool_call(body)

    try:
        parsed = json.loads(body, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        return None
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
    try:
        validated = schema.model_validate(arguments)
    except (TypeError, ValueError):
        return None
    return validated.model_dump(exclude_unset=True)


def _dom_score(issues: list[dict]) -> float:
    """Graded layout integrity so each removed overflow/collision still earns signal."""
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
        print(f"Pairwise ViT preflight: score={aesthetic_score:.6f} "
              f"settings={reward_model_settings()} "
              f"metrics={getattr(model, 'last_metrics', {})}")
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


_SAMPLE_DUMP = {"dir": None, "keys": frozenset()}


def configure_sample_dump(directory, keys) -> None:
    """Save the first completion of each watched (doc_id, slide_index) at every step it is scored."""
    _SAMPLE_DUMP["dir"] = Path(directory) if directory else None
    _SAMPLE_DUMP["keys"] = frozenset((str(doc), int(index)) for doc, index in keys)


def _watched_indices(doc_ids, slide_indices, count) -> dict[int, tuple[str, int]]:
    if _SAMPLE_DUMP["dir"] is None or doc_ids is None or slide_indices is None:
        return {}
    watched = {}
    for index, key in enumerate(zip(map(str, doc_ids), map(int, slide_indices))):
        if index < count and key in _SAMPLE_DUMP["keys"] and key not in watched.values():
            watched[index] = key
    return watched


def _sample_path(step: int, key: tuple[str, int], suffix: str) -> Path:
    directory = _SAMPLE_DUMP["dir"] / f"step_{step:04d}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{key[0]}_slide{key[1]:02d}{suffix}"


def _log_unsupported_numbers(step: int, source: str, visible_text: str) -> None:
    """Record figures absent from the source so fabrication can be told apart from rounding/units."""
    source_numbers = [number for number, _ in _numeric_occurrences(source)]
    supported = {_number_support_key(number) for number in source_numbers}
    flagged = [
        {"value": number, "context": sorted(context)}
        for number, context in _numeric_occurrences(visible_text)
        if _is_checkable_number(number) and _number_support_key(number) not in supported
    ]
    _SAMPLE_DUMP["dir"].mkdir(parents=True, exist_ok=True)
    with open(_SAMPLE_DUMP["dir"] / "unsupported_numbers.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "step": step, "flagged": flagged, "source_numbers": source_numbers,
            "visible_text": visible_text[:600],
        }, ensure_ascii=False) + "\n")


def reward_weights() -> dict[str, float]:
    weights = {
        "lexical": float(os.getenv("RL_REWARD_LEXICAL_WEIGHT", "0.5")),
        "semantic": float(os.getenv("RL_REWARD_SEMANTIC_WEIGHT", "0.7")),
        "numeric_fact": float(os.getenv("RL_REWARD_NUMERIC_FACT_WEIGHT", "1.0")),
        "dom": float(os.getenv("RL_REWARD_DOM_WEIGHT", "1.5")),
        "aesthetic": float(os.getenv("RL_REWARD_AESTHETIC_WEIGHT", "1.0")),
        "image_loaded": float(os.getenv("RL_REWARD_IMAGE_LOADED_WEIGHT", "0.25")),
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
    trainer_state = kwargs.get("trainer_state")
    step = int(getattr(trainer_state, "global_step", 0) or 0)
    watched = _watched_indices(kwargs.get("source_doc_id"), kwargs.get("slide_index"), len(completions))
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
    invalid_reasons = Counter()
    for index, completion in enumerate(completions):
        reason = "tool_input"
        try:
            parsed = _parse_canonical_completion(completion)
            if parsed is None:
                invalid_reasons["format"] += 1
                continue
            if parsed["name"] != expected[index]:
                invalid_reasons["wrong_tool"] += 1
                continue
            tool = _TOOL_BY_NAME.get(expected[index])
            if tool is None:
                invalid_reasons["unknown_expected_tool"] += 1
                continue
            mode = str(modes_by_sample[index] or "none")
            sample_images = list(assets_by_sample[index] or [])
            if mode not in {"none", "semantic"}:
                invalid_reasons["image_mode"] += 1
                continue
            if mode == "semantic" and not sample_images:
                invalid_reasons["missing_images"] += 1
                continue
            if not tool_matches_image_mode(tool, mode, len(sample_images)):
                invalid_reasons["tool_image_compatibility"] += 1
                continue
            arguments = _validate_tool_arguments(tool, parsed["arguments"])
            if arguments is None:
                invalid_reasons["schema"] += 1
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
                invalid_reasons["image_injection"] += 1
                continue
            styled_arguments = _validate_tool_arguments(
                tool, injected_call.get("arguments", {})
            )
            if styled_arguments is None:
                invalid_reasons["styled_schema"] += 1
                continue
            try:
                xml_content = execute_tool(
                    {"name": tool.name, "arguments": styled_arguments}
                )
            except Exception:
                # Policy text reaches layout code (e.g. control chars break minidom); never kill training.
                invalid_reasons["tool_execution"] += 1
                continue
            # Same final boundary as the production renderer node: shrink text to fit, then repair unreadable colours.
            style = styles[index] or {}
            if os.getenv("RL_TEXT_AUTOFIT", "true").lower() in {"1", "true", "yes", "on"}:
                xml_content, _ = fit_xml_text(xml_content)
            if os.getenv("RL_CONTRAST_GUARD", "true").lower() in {"1", "true", "yes", "on"}:
                xml_content, _ = enforce_xml_text_contrast(
                    xml_content,
                    preferred_colors=[
                        color for color in (style.get("accent_color"), style.get("primary_color"),
                                            style.get("secondary_color"), style.get("text_color")) if color
                    ],
                    protect_unknown_surfaces=True,
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
        except NoApprovedImageError:
            invalid_reasons["image_injection"] += 1
        except (TypeError, ValueError, KeyError):
            invalid_reasons[reason] += 1

    if not rows:
        for index, key in watched.items():
            _sample_path(step, key, ".json").write_text(json.dumps({
                "step": step, "doc_id": key[0], "slide_index": key[1], "reward": rewards[index],
                "valid": False, "completion": completions[index],
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        if log_metric is not None:
            log_metric("reward/valid_fraction", 0.0)
            for name in _COMPONENT_NAMES:
                log_metric(f"reward_component/{name}", 0.0)
            for name in ("format", "wrong_tool", "unknown_expected_tool", "image_mode",
                         "missing_images", "tool_image_compatibility", "schema",
                         "image_injection", "styled_schema", "tool_execution", "tool_input"):
                log_metric(f"reward/invalid_{name}_fraction", invalid_reasons[name] / len(completions))
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
            if _MARKUP_LEAK.search(frontend.get("visible_text") or ""):
                frontend.setdefault("issues", []).append({"type": "markup_leak"})
        vit_started = time.perf_counter()
        vit_model = _get_model()
        aesthetic_scores = _evaluate_batch(vit_model, paths)
        if log_metric is not None:
            for name, value in getattr(vit_model, "last_metrics", {}).items():
                log_metric(f"reward_pairwise/{name}", value)
        vit_seconds = time.perf_counter() - vit_started
        for row, path in zip(rows, paths, strict=True):
            if row["index"] in watched and path.is_file():
                shutil.copyfile(path, _sample_path(step, watched[row["index"]], ".png"))

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
    unsupported_numbers = []
    row_components = {}
    dom_issue_slides = Counter()
    for row, frontend, semantic, aesthetic in zip(
        rows, frontend_results, semantic_scores, aesthetic_scores, strict=True,
    ):
        source_facts = fact_rows[row["index"]]
        lexical = _lexical_score(row["source"], frontend["visible_text"])
        fact_coverage = _numeric_fact_coverage(
            row["source"], frontend["visible_text"], source_facts,
        )
        dom = _dom_score(frontend["issues"])
        dom_issue_slides.update({issue.get("type") for issue in frontend["issues"]} - {None})
        components = {
            "lexical": lexical,
            "semantic": semantic,
            "numeric_fact": fact_coverage,
            "language": _language_consistency(row["source"], frontend["visible_text"]),
            "dom": dom,
            "aesthetic": float(aesthetic),
            "image_loaded": float(row["image_loaded"]),
        }
        # A slide in the wrong language is useless however well it scores otherwise.
        rewards[row["index"]] = _weighted_reward(
            {name: value for name, value in components.items() if name != "language"}, weights
        ) * components["language"]
        row_components[row["index"]] = {name: round(value, 4) for name, value in components.items()}
        unsupported_numbers.append(
            _unsupported_number_fraction(row["source"], frontend["visible_text"])
        )
        if unsupported_numbers[-1] and _SAMPLE_DUMP["dir"] is not None:
            _log_unsupported_numbers(step, row["source"], frontend["visible_text"])
        for name, value in components.items():
            component_values[name].append(value)

    scored = {row["index"]: (row, frontend) for row, frontend in zip(rows, frontend_results, strict=True)}
    for index, key in watched.items():
        row, frontend = scored.get(index, (None, None))
        record = {
            "step": step, "doc_id": key[0], "slide_index": key[1], "reward": rewards[index],
            "valid": row is not None, "components": row_components.get(index),
            "dom_issues": sorted({issue.get("type") for issue in frontend["issues"]} - {None}) if frontend else None,
            "visible_text": frontend["visible_text"] if frontend else None,
            "min_contrast": frontend.get("min_contrast") if frontend else None,
            "min_font_px": frontend.get("min_font_px") if frontend else None,
            "completion": completions[index],
        }
        _sample_path(step, key, ".json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    if log_metric is not None:
        log_metric("reward/valid_fraction", len(rows) / max(1, len(completions)))
        log_metric("reward_content/unsupported_number_fraction", float(np.mean(unsupported_numbers)))
        for issue_type in (*_DOM_PENALTY_WEIGHTS, "image_load"):
            log_metric(f"reward_dom/{issue_type}_fraction", dom_issue_slides[issue_type] / len(rows))
        for name in _COMPONENT_NAMES:
            values = component_values.get(name, [])
            log_metric(
                f"reward_component/{name}",
                float(np.mean(values)) if values else 0.0,
            )
        for name in ("format", "wrong_tool", "unknown_expected_tool", "image_mode",
                     "missing_images", "tool_image_compatibility", "schema",
                     "image_injection", "styled_schema", "tool_execution", "tool_input"):
            log_metric(f"reward/invalid_{name}_fraction", invalid_reasons[name] / len(completions))

    print(
        "  [Composite Reward] "
        f"valid={len(rows)}/{len(completions)} "
        f"components={{{' '.join(f'{key}={np.mean(value):.3f}' for key, value in component_values.items())}}} "
        f"invalid={dict(invalid_reasons)} "
        f"scores=[{' '.join(f'{score:.3f}' for score in rewards)}]"
    )
    return rewards
