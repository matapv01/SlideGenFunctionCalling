"""Single-pass GRPO reward for the XML SlideGen pipeline."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from threading import Lock

import numpy as np

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.deck_style import (
    apply_deck_style_to_tool_call,
)
from rl.rewards.aesthetic_reward import _evaluate_batch, _get_model
from rl.rewards.content_reward import clean_words
from rl.rewards.dom_overflow_reward import _PENALTY_WEIGHTS, _check_xml_issues
from rl.slidegen_adapter import (
    execute_tool,
    parse_tool_call_json,
    render_xml_batch_to_png,
)


_TOOL_BY_NAME = {
    tool.name: tool
    for tools in TOOLS_DICT.values()
    for tool in tools
}

_TEXT_EMBEDDER = None
_TEXT_EMBEDDER_LOCK = Lock()


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


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)


def _lexical_score(source: str, generated: str) -> float:
    source_words = clean_words(source)
    generated_words = clean_words(generated)
    if not source_words:
        return 1.0
    overlap = len(set(source_words).intersection(generated_words)) / len(
        set(source_words)
    )
    length_ratio = len(generated_words) / max(1, len(source_words))
    return float(max(0.0, min(1.0, overlap * min(1.0, length_ratio / 0.3))))


def _format_score(completion: str, parsed: dict) -> float:
    stripped = completion.strip()
    canonical = (
        stripped.startswith("<tool_call>")
        and stripped.endswith("</tool_call>")
        and stripped.count("<tool_call>") == 1
        and stripped.count("</tool_call>") == 1
    )
    return 1.0 if canonical and isinstance(parsed.get("arguments"), dict) else 0.0




def preflight_reward_runtime() -> None:
    """Fail before training if Chrome or the aesthetic checkpoint is unusable."""
    _get_model()
    from playwright.sync_api import sync_playwright

    configured = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    options = {"headless": True}
    if configured:
        path = Path(configured).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Configured Chromium not found: {path}")
        options["executable_path"] = str(path)
    elif Path("/usr/bin/google-chrome").is_file():
        options["executable_path"] = "/usr/bin/google-chrome"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**options)
        browser.close()


def slidegen_composite_reward(
    prompts,
    completions,
    assigned_tool_name=None,
    source_content=None,
    deck_style=None,
    **kwargs,
):
    del prompts, kwargs
    expected = list(assigned_tool_name or [""] * len(completions))
    sources = list(source_content or [""] * len(completions))
    styles = list(deck_style or [{}] * len(completions))
    invalid_reward = float(os.getenv("RL_INVALID_REWARD", "-2.0"))
    rewards = [invalid_reward] * len(completions)
    parsed_rows = []
    render_jobs = []

    for index, completion in enumerate(completions):
        try:
            parsed = parse_tool_call_json(completion)
            if not parsed or parsed.get("name") != expected[index]:
                continue
            tool = _TOOL_BY_NAME[expected[index]]
            styled_call = apply_deck_style_to_tool_call(
                parsed,
                [tool],
                styles[index] or {},
            )
            xml_content = execute_tool(styled_call)
            generated = " ".join(_strings(parsed.get("arguments") or {}))
            issues = _check_xml_issues(xml_content)
            dom_penalty = min(
                2.0,
                sum(_PENALTY_WEIGHTS.get(issue["type"], 0.10) for issue in issues),
            )
            parsed_rows.append(
                {
                    "index": index,
                    "generated": generated,
                    "source": sources[index],
                    "lexical": _lexical_score(sources[index], generated),
                    "format": _format_score(completion, parsed),
                    "dom": max(-1.0, 1.0 - dom_penalty),
                }
            )
            render_jobs.append((index, xml_content))
        except (TypeError, ValueError, KeyError):
            continue
        except Exception:
            continue

    if not parsed_rows:
        print(f"  [Composite Reward] all {len(completions)} completions invalid")
        return rewards

    embedder = _get_text_embedder()
    generated_embeddings = embedder.encode(
        [row["generated"] or "." for row in parsed_rows],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    source_embeddings = embedder.encode(
        [row["source"] or "." for row in parsed_rows],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    workers = max(
        1,
        min(int(os.getenv("RL_REWARD_RENDER_WORKERS", "4")), len(render_jobs)),
    )
    with tempfile.TemporaryDirectory(prefix="slidegen_reward_") as directory:
        rendered = [
            (index, Path(directory) / f"reward_{index}.png")
            for index, _ in render_jobs
        ]
        render_xml_batch_to_png(
            [xml_content for _, xml_content in render_jobs],
            [str(path) for _, path in rendered],
            max_concurrency=workers,
        )
        aesthetic_scores = _evaluate_batch(
            _get_model(), [path for _, path in rendered]
        )
        aesthetic_by_index = {
            index: float(score)
            for (index, _), score in zip(rendered, aesthetic_scores)
        }
        weights = {
            "valid": float(os.getenv("RL_REWARD_VALID_WEIGHT", "1.5")),
            "lexical": float(os.getenv("RL_REWARD_LEXICAL_WEIGHT", "0.7")),
            "semantic": float(os.getenv("RL_REWARD_SEMANTIC_WEIGHT", "0.8")),
            "format": float(os.getenv("RL_REWARD_FORMAT_WEIGHT", "0.3")),
            "dom": float(os.getenv("RL_REWARD_DOM_WEIGHT", "0.8")),
            "aesthetic": float(os.getenv("RL_REWARD_AESTHETIC_WEIGHT", "1.0")),
        }
        for row, generated_embedding, source_embedding in zip(
            parsed_rows, generated_embeddings, source_embeddings
        ):
            semantic = float(
                np.clip(np.dot(generated_embedding, source_embedding), 0.0, 1.0)
            )
            score = (
                weights["valid"]
                + weights["lexical"] * row["lexical"]
                + weights["semantic"] * semantic
                + weights["format"] * row["format"]
                + weights["dom"] * row["dom"]
                + weights["aesthetic"] * aesthetic_by_index[row["index"]]
            )
            rewards[row["index"]] = float(score)

    print(
        "  [Composite Reward] "
        f"valid={len(parsed_rows)}/{len(completions)} "
        f"scores=[{' '.join(f'{score:.3f}' for score in rewards)}]"
    )
    return rewards
